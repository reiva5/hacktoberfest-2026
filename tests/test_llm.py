"""Offline transport and credential tests for Gemma 4; no network or model calls."""
import base64
import json
import traceback

import httpx
import pytest
from pydantic import BaseModel

from gateway import config, llm

TEST_KEY = "offline-test-credential"


class Answer(BaseModel):
    count: int


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(config, "LLM_MODEL", "gemma-4-26b-a4b-it")
    monkeypatch.setattr(config, "LLM_SMALL_MODEL", "gemma-4-31b-it")
    monkeypatch.setattr(config, "LLM_API_KEY", TEST_KEY)
    monkeypatch.setattr(config, "LLM_API_KEY_FILE", "")
    monkeypatch.setattr(config, "LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setattr(llm.time, "sleep", lambda _: None)


def _reply(text='{"count": 2}', **candidate):
    return {"candidates": [{
        "finishReason": "STOP",
        "content": {"parts": [{"text": text}]},
        **candidate,
    }]}


@pytest.fixture
def transport(monkeypatch):
    requests = []
    responses = []

    def handle(request):
        requests.append(request)
        if not responses:
            pytest.fail("Unexpected model request")
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def post(url, **kwargs):
        with httpx.Client(transport=httpx.MockTransport(handle)) as client:
            return client.post(url, **kwargs)

    monkeypatch.setattr(httpx, "post", post)
    return requests, responses


def test_gemini_key_is_header_only_and_result_is_validated(transport, tmp_path, monkeypatch, capsys):
    requests, responses = transport
    key_file = tmp_path / "private.txt"
    key_file.write_text(TEST_KEY + "\n", encoding="utf-8-sig")
    monkeypatch.setattr(config, "LLM_API_KEY_FILE", str(key_file))
    monkeypatch.setattr(config, "LLM_API_KEY", "unused-key")
    responses.append(httpx.Response(200, json=_reply()))

    assert llm.chat_json("Extract facts.", "Public page text.", Answer).count == 2
    [request] = requests
    assert str(request.url) == f"{llm.GEMINI_BASE_URL}/models/gemma-4-26b-a4b-it:generateContent"
    assert request.headers["x-goog-api-key"] == TEST_KEY
    assert not request.url.query
    assert TEST_KEY not in request.content.decode()
    body = json.loads(request.content)
    assert body["contents"] == [{"role": "user", "parts": [{"text": "Public page text."}]}]
    assert body["generationConfig"]["temperature"] == 0
    assert "Extract facts." in body["systemInstruction"]["parts"][0]["text"]
    assert '"count"' in body["systemInstruction"]["parts"][0]["text"]
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("provider", ["gemini", "openai"])
def test_schema_instruction_stays_compact_for_both_transports(transport, monkeypatch, provider):
    requests, responses = transport
    monkeypatch.setattr(config, "LLM_PROVIDER", provider)
    if provider == "openai":
        monkeypatch.setattr(config, "LLM_MODEL", "gemma4:e4b")
        responses.append(httpx.Response(200, json={"choices": [{"message": {"content": '{"count": 2}'}}]}))
    else:
        responses.append(httpx.Response(200, json=_reply()))

    assert llm.chat_json("Extract.", "Page.", Answer).count == 2
    body = json.loads(requests[0].content)
    instruction = (body["systemInstruction"]["parts"][0]["text"] if provider == "gemini"
                   else body["messages"][0]["content"])
    assert instruction == (
        "Extract.\n\nReply with a single JSON object that matches this JSON schema, and nothing else:\n"
        + json.dumps(Answer.model_json_schema(), separators=(",", ":"))
    )


def test_gemini_vision_and_small_model_use_same_transport(transport):
    requests, responses = transport
    responses.append(httpx.Response(200, json=_reply()))
    llm.chat_json("Extract.", "Slide.", Answer, model=config.LLM_SMALL_MODEL, images=[b"fake-png"])
    [request] = requests
    assert "/gemma-4-31b-it:" in str(request.url)
    parts = json.loads(request.content)["contents"][0]["parts"]
    assert parts[1]["inlineData"] == {
        "mimeType": "image/png", "data": base64.b64encode(b"fake-png").decode(),
    }


def test_gemini_corrects_invalid_json_once(transport):
    requests, responses = transport
    responses.extend([
        httpx.Response(200, json=_reply('{"count": "wrong"}')),
        httpx.Response(200, json=_reply('```json\n{"count": 3}\n```')),
    ])
    assert llm.chat_json("Extract.", "Page.", Answer).count == 3
    assert len(requests) == 2
    contents = json.loads(requests[1].content)["contents"]
    assert [message["role"] for message in contents] == ["user", "model", "user"]
    assert contents[1]["parts"][0]["text"] == '{"count": "wrong"}'
    assert "Return corrected JSON only" in contents[2]["parts"][0]["text"]
    assert "wrong" not in contents[2]["parts"][0]["text"]


def test_gemini_ignores_thinking_text(transport):
    _, responses = transport
    responses.append(httpx.Response(200, json=_reply(content={"parts": [
        {"text": "Private reasoning.", "thought": True},
        {"text": '{"count":'},
        {"text": " 4}"},
    ]})))
    assert llm.chat_json("Extract.", "Page.", Answer).count == 4


@pytest.mark.parametrize("model", [
    "gemini-2.5-flash", "gemma-3-27b-it", "gemma4:e4b", "gpt-4o",
    "gemma-4-31b-it:evil", "../gemini-pro", "",
])
def test_gemini_rejects_other_models_before_network(transport, monkeypatch, model):
    requests, _ = transport
    monkeypatch.setattr(config, "LLM_MODEL", model)
    with pytest.raises(llm.LLMError, match="Only Gemma 4"):
        llm.chat_json("Extract.", "Page.", Answer)
    assert not requests


def test_discovery_override_cannot_use_proprietary_model(transport):
    requests, _ = transport
    with pytest.raises(llm.LLMError, match="Only Gemma 4"):
        llm.chat_json("Classify.", "Page.", Answer, model="gemini-2.5-flash")
    assert not requests


def test_empty_model_override_does_not_silently_use_default(transport):
    requests, _ = transport
    with pytest.raises(llm.LLMError, match="Only Gemma 4"):
        llm.chat_json("Extract.", "Page.", Answer, model="")
    assert not requests


@pytest.mark.parametrize("model", ["gemma3:4b", "gemini-pro", "gemma4:e4b/../../other"])
def test_local_rejects_other_models(transport, monkeypatch, model):
    requests, _ = transport
    monkeypatch.setattr(config, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(config, "LLM_MODEL", model)
    with pytest.raises(llm.LLMError, match="Only Gemma 4"):
        llm.chat_json("Extract.", "Page.", Answer)
    assert not requests


def test_local_transport_retains_schema_fallback_and_images(transport, monkeypatch):
    requests, responses = transport
    monkeypatch.setattr(config, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(config, "LLM_MODEL", "gemma4:e4b")
    responses.extend([
        httpx.Response(400),
        httpx.Response(200, json={"choices": [{"message": {"content": '{"count": 5}'}}]}),
    ])
    assert llm.chat_json("Extract.", "Page.", Answer, images=[b"png"]).count == 5
    assert len(requests) == 2
    assert str(requests[0].url) == "http://localhost:11434/v1/chat/completions"
    assert requests[0].headers["Authorization"] == f"Bearer {TEST_KEY}"
    assert json.loads(requests[0].content)["response_format"]["type"] == "json_schema"
    assert json.loads(requests[1].content)["response_format"]["type"] == "json_object"
    content = json.loads(requests[0].content)["messages"][1]["content"]
    assert content[0] == {"type": "text", "text": "Page."}
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")


def test_local_correction_retry(transport, monkeypatch):
    requests, responses = transport
    monkeypatch.setattr(config, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(config, "LLM_MODEL", "gemma4:e4b")
    responses.extend([
        httpx.Response(200, json={"choices": [{"message": {"content": "invalid"}}]}),
        httpx.Response(200, json={"choices": [{"message": {"content": '{"count": 6}'}}]}),
    ])
    assert llm.chat_json("Extract.", "Page.", Answer).count == 6
    messages = json.loads(requests[1].content)["messages"]
    assert [message["role"] for message in messages] == ["system", "user", "assistant", "user"]


@pytest.mark.parametrize("status", [400, 401, 403, 429, 500, 502, 503, 504])
def test_http_errors_never_leak_credentials(transport, capsys, caplog, status):
    requests, responses = transport
    attempts = 2 if status >= 500 else 1
    responses.extend(httpx.Response(status, text=TEST_KEY) for _ in range(attempts))
    with pytest.raises(llm.LLMError, match=f"HTTP {status}") as error:
        llm.chat_json("Extract.", "Page.", Answer)
    assert len(requests) == attempts
    assert TEST_KEY not in "".join(traceback.format_exception(error.value))
    assert TEST_KEY not in caplog.text
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_transient_gemini_failure_retries_same_model_once(transport, monkeypatch, caplog, status):
    requests, responses = transport
    delays = []
    monkeypatch.setattr(llm.time, "sleep", delays.append)
    responses.extend([
        httpx.Response(status, text=TEST_KEY),
        httpx.Response(200, json=_reply()),
    ])
    assert llm.chat_json("Extract.", "Page.", Answer).count == 2
    assert len(requests) == 2
    assert requests[0].url == requests[1].url
    assert requests[0].content == requests[1].content
    assert delays == [2]
    assert f"HTTP {status}" in caplog.text
    assert TEST_KEY not in caplog.text


def test_local_server_failure_is_not_automatically_retried(transport, monkeypatch):
    requests, responses = transport
    monkeypatch.setattr(config, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(config, "LLM_MODEL", "gemma4:e4b")
    responses.append(httpx.Response(500))
    with pytest.raises(llm.LLMError, match="HTTP 500"):
        llm.chat_json("Extract.", "Page.", Answer)
    assert len(requests) == 1


def test_transport_error_never_leaks_credentials(transport):
    _, responses = transport
    responses.append(httpx.ConnectError(f"Connection failed with {TEST_KEY}"))
    with pytest.raises(llm.LLMError, match="ConnectError") as error:
        llm.chat_json("Extract.", "Page.", Answer)
    assert TEST_KEY not in "".join(traceback.format_exception(error.value))


@pytest.mark.parametrize("body", [
    {}, {"candidates": []}, {"candidates": None}, {"candidates": [None]},
    _reply(content={"parts": [{"text": None}]}),
    _reply(content={"parts": []}),
    _reply(finishReason="MAX_TOKENS"),
    _reply(finishReason="SAFETY"),
    {"promptFeedback": {"blockReason": "SAFETY"}},
])
def test_malformed_blocked_or_truncated_responses_fail(transport, body):
    _, responses = transport
    responses.append(httpx.Response(200, json=body))
    with pytest.raises(llm.LLMError):
        llm.chat_json("Extract.", "Page.", Answer)


def test_non_json_response_fails_without_leaking_body(transport):
    _, responses = transport
    responses.append(httpx.Response(200, text=TEST_KEY))
    with pytest.raises(llm.LLMError, match="malformed") as error:
        llm.chat_json("Extract.", "Page.", Answer)
    assert TEST_KEY not in str(error.value)


def test_invalid_output_stops_after_one_retry_without_logging_input(transport):
    requests, responses = transport
    responses.extend([httpx.Response(200, json=_reply(TEST_KEY)) for _ in range(2)])
    with pytest.raises(llm.LLMError, match="after 2 attempt") as error:
        llm.chat_json("Extract.", "Page.", Answer)
    assert len(requests) == 2
    assert TEST_KEY not in "".join(traceback.format_exception(error.value))


@pytest.mark.parametrize("file_content", [b"", b" \n", b"two keys", b"\xff"])
def test_invalid_key_file_fails_before_network(transport, tmp_path, monkeypatch, file_content):
    requests, _ = transport
    key_file = tmp_path / "invalid.txt"
    key_file.write_bytes(file_content)
    monkeypatch.setattr(config, "LLM_API_KEY_FILE", str(key_file))
    with pytest.raises(llm.LLMError):
        llm.chat_json("Extract.", "Page.", Answer)
    assert not requests


def test_missing_key_file_does_not_fall_back(transport, tmp_path, monkeypatch):
    requests, _ = transport
    monkeypatch.setattr(config, "LLM_API_KEY_FILE", str(tmp_path / "missing.txt"))
    with pytest.raises(llm.LLMError, match="Could not read"):
        llm.chat_json("Extract.", "Page.", Answer)
    assert not requests


def test_missing_key_fails_before_network(transport, monkeypatch):
    requests, _ = transport
    monkeypatch.setattr(config, "LLM_API_KEY", "")
    with pytest.raises(llm.LLMError, match="Set LLM_API_KEY"):
        llm.chat_json("Extract.", "Page.", Answer)
    assert not requests


def test_unknown_provider_fails_before_network(transport, monkeypatch):
    requests, _ = transport
    monkeypatch.setattr(config, "LLM_PROVIDER", "unknown")
    with pytest.raises(llm.LLMError, match="LLM_PROVIDER"):
        llm.chat_json("Extract.", "Page.", Answer)
    assert not requests


def test_negative_retries_fails_before_network(transport):
    requests, _ = transport
    with pytest.raises(llm.LLMError, match="retries must be non-negative"):
        llm.chat_json("Extract.", "Page.", Answer, retries=-1)
    assert not requests


def test_zero_retries_does_not_send_correction(transport):
    requests, responses = transport
    responses.append(httpx.Response(200, json=_reply("not-json")))
    with pytest.raises(llm.LLMError, match="after 1 attempt"):
        llm.chat_json("Extract.", "Page.", Answer, retries=0)
    assert len(requests) == 1
