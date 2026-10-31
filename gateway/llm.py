"""Thin client for any OpenAI-compatible chat endpoint (Ollama, vLLM, llama.cpp, hosted Gemma).

Everything we ask the model returns JSON validated against a pydantic model, so a page redesign
can change the HTML but not the shape of what comes out.
"""
import base64
import json
import re
from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from . import config

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    pass


def _image_part(png: bytes) -> dict:
    return {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}


def _post(payload: dict) -> httpx.Response:
    return httpx.post(
        f"{config.LLM_BASE_URL}/chat/completions",
        json=payload,
        headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
        timeout=config.LLM_TIMEOUT,
    )


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
    content: str | list = user
    if images:
        content = [{"type": "text", "text": user}] + [_image_part(i) for i in images]
    messages = [
        {"role": "system", "content": system + "\n\nReply with a single JSON object that matches this JSON schema, and nothing else:\n"
         + json.dumps(schema.model_json_schema(), separators=(",", ":"))},
        {"role": "user", "content": content},
    ]
    payload = {
        "model": model or config.LLM_MODEL,
        "messages": messages,
        "temperature": 0,
        "response_format": {"type": "json_schema", "json_schema": {"name": schema.__name__, "schema": schema.model_json_schema()}},
    }

    for attempt in range(retries + 1):
        try:
            resp = _post(payload)
            if resp.status_code == 400 and payload["response_format"]["type"] == "json_schema":
                # Some servers only support plain JSON mode.
                payload["response_format"] = {"type": "json_object"}
                resp = _post(payload)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise LLMError(f"LLM request to {config.LLM_BASE_URL} failed: {e}") from e

        text = resp.json()["choices"][0]["message"]["content"] or ""
        try:
            return schema.model_validate_json(_strip_fences(text))
        except ValidationError as e:
            if attempt == retries:
                raise LLMError(f"Model output did not match {schema.__name__}: {e}") from e
            # Show the model its mistake once, then try again.
            payload["messages"] = messages + [
                {"role": "assistant", "content": text},
                {"role": "user", "content": f"That JSON was invalid: {e}. Return corrected JSON only."},
            ]
    raise LLMError("unreachable")
