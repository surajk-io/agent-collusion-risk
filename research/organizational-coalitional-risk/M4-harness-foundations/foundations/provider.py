"""Stateless provider boundary; the only concrete adapter is a fixed script."""
import platform
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Protocol

from .contracts import Invalid, canonical, check_actor, strict_json
from .records import blob


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    endpoint: str
    model: str
    settings_json: bytes  # full fixed sampling/reasoning/seed/limit configuration

    def __post_init__(self):
        if not all((self.provider, self.endpoint, self.model)):
            raise Invalid("model_config")
        if not isinstance(strict_json(self.settings_json), dict):
            raise Invalid("model_settings")


@dataclass(frozen=True)
class Session:
    episode: str
    actor: str
    namespace: str  # separate diagnostic vs future spontaneous namespaces

    def __post_init__(self):
        check_actor(self.actor)
        if not self.episode or not self.namespace:
            raise Invalid("session")


@dataclass(frozen=True)
class Request:
    session: Session
    slot_nonce: str
    config: ModelConfig
    input_bytes: bytes  # complete serialized provider request, no implicit history


@dataclass(frozen=True)
class Response:
    output_bytes: bytes
    metadata_json: bytes  # resolved route/version, response ID, finish, usage/cost


class Adapter(Protocol):
    def complete(self, request: Request) -> Response:
        """One completion; no hidden session, retry, repair, truncation or fallback.

        Future implementations must return retained wire bytes plus explicit
        resolved metadata. No networking implementation is supplied here.
        """
        ...


class ScriptedAdapter:
    def __init__(self, config, responses):
        self.config = config
        self._responses = dict(responses)  # (Session, nonce) -> bytes or Exception
        self._used = set()

    def complete(self, request):
        key = (request.session, request.slot_nonce)
        if request.config != self.config:
            raise Invalid("config_changed")
        if key in self._used:
            raise Invalid("duplicate_invocation")
        self._used.add(key)
        result = self._responses[key]
        if isinstance(result, Exception):
            raise result
        return Response(result, canonical({"origin": "script", "resolved_model":
                                           self.config.model, "usage": None,
                                           "cost": None, "finish_reason": "script"}))


def now():
    return {"utc": datetime.now(timezone.utc).isoformat(),
            "monotonic_ns": time.monotonic_ns()}


def within_cutoff(handoff_ns, receipt_ns, allowance_ns):
    if allowance_ns < 0 or receipt_ns < handoff_ns:
        raise Invalid("clock")
    return receipt_ns <= handoff_ns + allowance_ns


def invoke(adapter, request, journal, clock=now):
    """Write-ahead request and terminal response. An interrupted call stays open.

    A recorded invocation is never silently sampled again after crash/restart.
    No decision deadline/fallback policy is selected by this function.
    """
    key = canonical([asdict(request.session), request.slot_nonce]).decode("utf-8")
    if any(e["key"] == key + ":request" for e in journal.events):
        raise Invalid("invocation_already_recorded")
    journal.append(key + ":request", "provider_request", {
        "session": asdict(request.session), "slot_nonce": request.slot_nonce,
        "config": {"provider": request.config.provider, "endpoint": request.config.endpoint,
                   "model": request.config.model, "settings": blob(request.config.settings_json)},
        "input": blob(request.input_bytes), "activation": clock(),
        "python": platform.python_version()})
    handoff = clock()
    try:
        response = adapter.complete(request)
    except Exception as exc:
        journal.append(key + ":response", "provider_error", {
            "handoff": handoff, "receipt": clock(), "type": type(exc).__name__, "message": str(exc)})
        raise
    journal.append(key + ":response", "provider_response", {
        "handoff": handoff, "receipt": clock(), "output": blob(response.output_bytes),
        "metadata": blob(response.metadata_json)})
    return response
