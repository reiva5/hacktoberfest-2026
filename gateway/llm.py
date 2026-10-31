"""Validated Gemma 4 JSON through Gemini API or an OpenAI-compatible Gemma server.

Everything we ask the model returns JSON validated against a pydantic model, so a page redesign
can change the HTML but not the shape of what comes out.
"""
import base64
import json
import logging
import re
import time
from pathlib import Path
from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from . import config

T = TypeVar("T", bound=BaseModel)
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODELS = {"gemma-4-31b-it", "gemma-4-26b-a4b-it"}


class LLMError(RuntimeError):
    pass


def _check_model(model: str) -> None:
    if config.LLM_PROVIDER not in {"openai", "gemini"}:
        raise LLMError("LLM_PROVIDER must be openai or gemini")
    if config.LLM_PROVIDER == "gemini":
        allowed = model in GEMINI_MODELS
    else:
        allowed = bool(re.fullmatch(r"gemma4(?::[a-z0-9._-]+)?|gemma-4-(?:31b|26b-a4b|12b|e4b|e2b)-it", model))
    if not allowed:
        raise LLMError("Only Gemma 4 models are allowed; check LLM_MODEL and LLM_SMALL_MODEL")


def _api_key() -> str:
    if config.LLM_API_KEY_FILE:
        try:
            key = Path(config.LLM_API_KEY_FILE).read_text(encoding="utf-8-sig").strip()
        except (OSError, UnicodeError):
            raise LLMError("Could not read LLM_API_KEY_FILE; use a readable UTF-8 key file") from None
    else:
        key = config.LLM_API_KEY
    if not key or any(c.isspace() for c in key):
        raise LLMError("Set LLM_API_KEY or LLM_API_KEY_FILE to a single API key")
    return key


def _image_part(png: bytes) -> dict:
    return {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}


def _post(payload: dict) -> httpx.Response:
    if config.LLM_PROVIDER == "gemini":
        return httpx.post(
            f"{GEMINI_BASE_URL}/models/{payload['model']}:generateContent",
            json={k: v for k, v in payload.items() if k != "model"},
            headers={"x-goog-api-key": _api_key()},
            timeout=config.LLM_TIMEOUT,
        )
    return httpx.post(
        f"{config.LLM_BASE_URL}/chat/completions",
        json=payload,
        headers={"Authorization": f"Bearer {_api_key()}"},
        timeout=config.LLM_TIMEOUT,
    )


def _request(payload: dict) -> httpx.Response:
    response = _post(payload)
    if config.LLM_PROVIDER == "gemini" and response.status_code in {500, 502, 503, 504}:
        logging.getLogger(__name__).warning(
            "Gemma 4 API returned HTTP %d; retrying once in 2 seconds", response.status_code
        )
        time.sleep(2)
        response = _post(payload)
    return response


def _response_text(resp: httpx.Response) -> str:
    try:
        body = resp.json()
        if config.LLM_PROVIDER == "gemini":
            candidate = body["candidates"][0]
            if not isinstance(candidate, dict):
                raise LLMError("LLM returned a malformed response")
            if candidate.get("finishReason", "STOP") != "STOP":
                raise LLMError("Gemma 4 response was blocked or incomplete")
            text = "".join(part["text"] for part in candidate["content"]["parts"]
                           if "text" in part and not part.get("thought"))
        else:
            text = body["choices"][0]["message"]["content"]
        if not isinstance(text, str) or not text.strip():
            raise LLMError("LLM returned no text")
        return text
    except (ValueError, KeyError, IndexError, TypeError):
        raise LLMError("LLM returned a malformed response") from None


def _strip_fences(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    # Fall back to the outermost JSON object if the model added prose around it.
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if start != -1 and end > start else text


def chat_json(system: str, user: str, schema: type[T], *, model: str | None = None,
              images: list[bytes] | None = None, retries: int = 1) -> T:
    selected_model = config.LLM_MODEL if model is None else model
    _check_model(selected_model)
    if retries < 0:
        raise LLMError("retries must be non-negative")
    instruction = system + "\n\nReply with a single JSON object that matches this JSON schema, and nothing else:\n" \
        + json.dumps(schema.model_json_schema())
    content: str | list = user
    if images:
        content = [{"type": "text", "text": user}] + [_image_part(i) for i in images]
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": content},
    ]
    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": 0,
        "response_format": {"type": "json_schema", "json_schema": {"name": schema.__name__, "schema": schema.model_json_schema()}},
    }
    if config.LLM_PROVIDER == "gemini":
        parts: list[dict] = [{"text": user}]
        for image in images or []:
            parts.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(image).decode()}})
        payload = {
            "model": selected_model,
            "systemInstruction": {"parts": [{"text": instruction}]},
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": 0, "thinkingConfig": {"thinkingLevel": "minimal"}},
        }

    for attempt in range(retries + 1):
        try:
            resp = _request(payload)
            if (resp.status_code == 400 and config.LLM_PROVIDER == "openai"
                    and payload["response_format"]["type"] == "json_schema"):
                # Some servers only support plain JSON mode.
                payload["response_format"] = {"type": "json_object"}
                resp = _post(payload)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise LLMError(f"LLM request failed: HTTP {e.response.status_code}") from None
        except httpx.HTTPError as e:
            raise LLMError(f"LLM request failed: {type(e).__name__}") from None

        text = _response_text(resp)
        try:
            return schema.model_validate_json(_strip_fences(text))
        except ValidationError as e:
            if attempt == retries:
                raise LLMError(f"Model output did not match {schema.__name__} after {attempt + 1} attempt(s)") from None
            # Show the model its mistake once, then try again.
            correction = f"That JSON was invalid: {e.errors(include_input=False, include_url=False)}. Return corrected JSON only."
            if config.LLM_PROVIDER == "gemini":
                payload["contents"].extend([
                    {"role": "model", "parts": [{"text": text}]},
                    {"role": "user", "parts": [{"text": correction}]},
                ])
            else:
                payload["messages"] = messages + [
                    {"role": "assistant", "content": text},
                    {"role": "user", "content": correction},
                ]
    raise LLMError("unreachable")
