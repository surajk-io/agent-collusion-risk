"""Google Model Garden OpenAI-compatible Chat Completions, one request per slot.

No SDK session, retry, redirect, continuation, fallback, or action JSON repair.
"""
from dataclasses import dataclass
import http.client as http_client
import re
import socket
import ssl
import threading
import time
from urllib.parse import urlsplit

from foundations.contracts import Invalid, canonical, strict_json
from foundations.provider import ModelConfig, now
from .materials import GENERATION_FIELDS, MODEL, validate_visible


@dataclass(frozen=True)
class Reply:
    payload: bytes
    representation: str
    status: int = 200
    final_byte: dict | None = None


class CallError(Exception):
    def __init__(self, code, payload=b"", representation="no_response_body", *, status=None):
        super().__init__(code)
        self.code, self.payload, self.representation, self.status = code, payload, representation, status


def extract(reply):
    """Only final message.content is an action. Full response is archived first."""
    if reply.status != 200:
        raise Invalid("provider_http_error")
    body = strict_json(reply.payload)
    if not isinstance(body, dict):
        raise Invalid("provider_object")
    # Historical scripted apparatus payloads only, never a live provider fallback.
    if reply.representation == "scripted_provider_payload" and "candidates" in body:
        candidate = body["candidates"][0]
        if candidate.get("finishReason") != "STOP":
            raise Invalid("provider_finish")
        return "".join(p["text"] for p in candidate["content"]["parts"]
                       if "text" in p and not p.get("thought", False)).encode()
    if body.get("model") != MODEL:
        raise Invalid("provider_model")
    choices = body.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise Invalid("provider_choice_count")
    choice = choices[0]
    if choice.get("index") != 0 or choice.get("finish_reason") != "stop":
        raise Invalid("provider_finish")
    message = choice.get("message", {})
    if message.get("role") != "assistant" or message.get("tool_calls") or message.get("function_call"):
        raise Invalid("provider_message")
    content = message.get("content")
    if not isinstance(content, str) or not content:
        raise Invalid("provider_no_text")
    return content.encode("utf-8")


def metadata(reply):
    """Convenience projection only; raw bytes remain authoritative, even on errors."""
    result = {"http_status": reply.status, "representation": reply.representation,
              "final_byte": reply.final_byte}
    try:
        body = strict_json(reply.payload)
        if isinstance(body, dict):
            result.update({k: body.get(k) for k in ("id", "model", "created", "usage", "metadata", "error")})
            result["finish_reasons"] = [c.get("finish_reason") for c in body.get("choices", [])]
    except (Invalid, AttributeError, TypeError):
        result["metadata_parse"] = "unavailable"
    return result


def http(endpoint, body, bearer, timeout):
    """Absolute elapsed transport deadline; keep every body byte read on failure.

    A timer interrupts a stalled socket, including header/body reads. System DNS
    resolution itself is OS-controlled; the runner watchdog independently closes
    the slot. No timeout can cancel generation already running at the provider.
    """
    url = urlsplit(endpoint)
    deadline = time.monotonic() + timeout
    connection = http_client.HTTPSConnection(url.hostname, timeout=timeout, context=ssl.create_default_context())
    partial, status, expired = bytearray(), None, threading.Event()
    sockets = []  # retain socket even if getresponse detaches it for Connection: close

    def cancel():
        expired.set()
        for sock in sockets or [connection.sock]:
            if sock is None:
                continue
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        connection.close()

    timer = threading.Timer(timeout, cancel)
    timer.daemon = True
    timer.start()
    try:
        connection.request("POST", url.path, body=body,
                           headers={"Content-Type": "application/json", "Authorization": "Bearer " + bearer})
        if connection.sock is not None:
            sockets.append(connection.sock)
        if expired.is_set():
            cancel()
            raise TimeoutError
        response = connection.getresponse()
        status = response.status
        # No redirect handling: 3xx is a retained provider failure.
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or expired.is_set():
                raise TimeoutError
            for sock in sockets or [connection.sock]:
                if sock is not None:
                    sock.settimeout(remaining)
            chunk = response.read1(65536)
            if not chunk:
                if response.length not in (None, 0):
                    raise CallError("transport_error", bytes(partial), "partial_http_response_body", status=status)
                break
            partial.extend(chunk)
        final_byte = now()
        if expired.is_set() or time.monotonic() > deadline:
            raise TimeoutError
        return Reply(bytes(partial), "http_response_body", status, final_byte)
    except CallError:
        raise
    except Exception as exc:
        if isinstance(exc, http_client.IncompleteRead):
            partial.extend(exc.partial)
        # Never log exception text, credentials, headers or request objects.
        code = "timeout" if expired.is_set() or isinstance(exc, (TimeoutError, socket.timeout)) else "transport_error"
        raise CallError(code, bytes(partial), "partial_http_response_body" if partial else "no_response_body",
                        status=status) from None
    finally:
        timer.cancel()
        connection.close()


class VertexAdapter:
    """Immutable DeepSeek MaaS configuration; credentials injected at handoff."""
    scripted = False

    @classmethod
    def from_file(cls, path, token_supplier, transport=http):
        from pathlib import Path
        config = strict_json(Path(path).read_bytes())
        if set(config) != {"provider", "endpoint", "model", "generation_config"}:
            raise ValueError("external_config_fields")
        return cls(ModelConfig(config["provider"], config["endpoint"], config["model"],
                               canonical(config["generation_config"])), token_supplier, transport)

    def __init__(self, config, token_supplier, transport=http):
        pattern = (r"https://aiplatform\.googleapis\.com/v1/projects/"
                   r"[A-Za-z0-9._-]+/locations/global/endpoints/openapi/chat/completions")
        if not re.fullmatch(pattern, config.endpoint) or config.model != MODEL or config.provider != "gcp-model-garden":
            raise ValueError("vertex_endpoint_model")
        settings = strict_json(config.settings_json)
        if set(settings) != GENERATION_FIELDS:
            raise ValueError("external_generation_fields")
        self.config, self._token, self._transport = config, token_supplier, transport

    def complete(self, request, timeout):
        if request.config != self.config:
            raise CallError("config_changed")
        body = strict_json(request.input_bytes)
        validate_visible(request.input_bytes)
        if {k: body[k] for k in GENERATION_FIELDS} != strict_json(self.config.settings_json):
            raise CallError("settings_changed")
        start = time.monotonic()
        try:
            token = self._token()
        except Exception:
            raise CallError("credential_acquisition_failed") from None
        remaining = timeout - (time.monotonic() - start)
        if remaining <= 0:
            raise CallError("credential_timeout")
        return self._transport(self.config.endpoint, request.input_bytes, token, remaining)
