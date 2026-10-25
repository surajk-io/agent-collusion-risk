"""Vertex generateContent REST adapter. Never invoked by the offline CLI.

Reference: https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/projects.locations.publishers.models/generateContent
"""
from dataclasses import dataclass
import re
import time
import urllib.error
import urllib.request

from foundations.contracts import Invalid, strict_json
from foundations.contracts import canonical
from foundations.provider import ModelConfig


@dataclass(frozen=True)
class Reply:
    payload: bytes
    representation: str  # http_response_body, or scripted_provider_payload
    status: int = 200


class CallError(Exception):
    def __init__(self, code, payload=b"", representation="no_response_body"):
        super().__init__(code)
        self.code, self.payload, self.representation = code, payload, representation


def extract(reply):
    """Retain full payload separately; action text excludes every thought part."""
    if reply.status != 200:
        raise Invalid("provider_http_error")
    body = strict_json(reply.payload)
    candidates = body.get("candidates", [])
    if len(candidates) != 1:
        raise Invalid("provider_candidate_count")
    candidate = candidates[0]
    if candidate.get("finishReason") != "STOP":
        raise Invalid("provider_finish")
    parts = candidate.get("content", {}).get("parts", [])
    if any("functionCall" in part for part in parts):
        raise Invalid("provider_tool_call")
    visible = [part["text"] for part in parts if "text" in part and not part.get("thought", False)]
    if not visible:
        raise Invalid("provider_no_text")
    return "".join(visible).encode("utf-8")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http(endpoint, body, bearer, timeout):
    request = urllib.request.Request(endpoint, data=body, method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + bearer})
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout) as response:
            return Reply(response.read(), "http_response_body", response.status)
    except urllib.error.HTTPError as exc:
        return Reply(exc.read(), "http_response_body", exc.code)
    except Exception:
        # No exception string, request object, credentials or headers are logged.
        raise CallError("transport_error") from None


class VertexAdapter:
    """External immutable endpoint/model/settings, injected token supplier.

    Uses retained HTTP body bytes rather than reconstructed SDK objects. No
    automatic retries, continuations, fallback models, cache or shared sessions.
    Token acquisition and endpoint capacity/billing require separate preflight.
    """
    scripted = False

    @classmethod
    def from_file(cls, path, token_supplier, transport=http):
        from pathlib import Path
        config = strict_json(Path(path).read_bytes())
        if set(config) != {"provider", "endpoint", "model", "generation_config"}:
            raise ValueError("external_config_fields")
        from .materials import GENERATION_FIELDS
        if set(config["generation_config"]) - GENERATION_FIELDS:
            raise ValueError("external_generation_fields")
        return cls(ModelConfig(config["provider"], config["endpoint"], config["model"],
                               canonical(config["generation_config"])), token_supplier, transport)

    def __init__(self, config, token_supplier, transport=http):
        pattern = (r"https://(?:[a-z0-9-]+-)?aiplatform\.googleapis\.com/v1/projects/"
                   r"[A-Za-z0-9._-]+/locations/[a-z0-9-]+/publishers/google/models/"
                   r"([A-Za-z0-9._-]+):generateContent")
        match = re.fullmatch(pattern, config.endpoint)
        if not match or match.group(1) != config.model:
            raise ValueError("vertex_endpoint_model")
        self.config, self._token, self._transport = config, token_supplier, transport

    def complete(self, request, timeout):
        if request.config != self.config:
            raise CallError("config_changed")
        body = strict_json(request.input_bytes)
        if body.get("generationConfig") != strict_json(self.config.settings_json):
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
