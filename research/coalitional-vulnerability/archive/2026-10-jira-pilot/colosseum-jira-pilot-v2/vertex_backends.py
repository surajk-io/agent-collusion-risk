"""Vertex AI inference adapters for the Jira-mini pilot.

Gemini uses the official ``google-genai`` SDK with Vertex AI enabled. Managed
open models (for example DeepSeek V4.1 Flash) use the Vertex AI
OpenAI-compatible Chat Completions endpoint through the ``openai`` SDK.

Authentication always comes from Google Cloud Application Default Credentials
(ADC). Access tokens are refreshed as needed and are never written to logs.
Optional SDK imports are deliberately lazy so the deterministic game remains
usable with only the Python standard library.
"""
from dataclasses import dataclass
import os
import time
from importlib.metadata import PackageNotFoundError, version

ADC_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)
RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class Completion:
    """Visible model text plus audit metadata for one completed inference call."""
    text: str
    metadata: dict


class InferenceError(RuntimeError):
    """Inference failure carrying structured details for the per-call trace."""

    def __init__(self, message, *, details=None):
        super().__init__(message)
        self.details = details or {}


def _package_version(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def resolve_vertex_settings(project=None, location=None, adc_project=None):
    """Resolve project/location from arguments, standard env vars, then ADC."""
    resolved_project = (project or os.environ.get("GOOGLE_CLOUD_PROJECT")
                        or os.environ.get("VERTEX_PROJECT") or adc_project)
    resolved_location = (location or os.environ.get("GOOGLE_CLOUD_LOCATION")
                         or os.environ.get("VERTEX_LOCATION") or "global")
    if not resolved_project:
        raise ValueError(
            "Vertex AI requires a project. Pass --project or set GOOGLE_CLOUD_PROJECT "
            "(an ADC quota project is used as a fallback when present)."
        )
    return str(resolved_project), str(resolved_location)


def vertex_api_host(location):
    """Return the documented Vertex AI host for global, multi-region, or regional locations."""
    if location == "global":
        return "https://aiplatform.googleapis.com"
    if location in ("us", "eu"):
        return f"https://aiplatform.{location}.rep.googleapis.com"
    return f"https://{location}-aiplatform.googleapis.com"


def vertex_openai_base_url(project, location):
    """Return the documented Vertex AI OpenAI-compatible base URL."""
    return (f"{vertex_api_host(location)}/v1/projects/{project}"
            f"/locations/{location}/endpoints/openapi")


def _load_adc(credentials=None):
    if credentials is not None:
        return credentials, None
    try:
        import google.auth
        loaded, project = google.auth.default(scopes=list(ADC_SCOPES))
        return loaded, project
    except Exception as exc:
        raise RuntimeError(
            "Could not load Google Cloud Application Default Credentials. Run "
            "`gcloud auth application-default login` and retry."
        ) from exc


def _ensure_credentials(credentials, force=False):
    """Refresh an expired OAuth token; force is used after an HTTP 401."""
    if credentials is None:
        return
    if force or not getattr(credentials, "valid", True):
        import google.auth.transport.requests
        credentials.refresh(google.auth.transport.requests.Request())


def _error_status(exc):
    for attr in ("status_code", "code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
    response = getattr(exc, "response", None)
    value = getattr(response, "status_code", None)
    return value if isinstance(value, int) else None


def _is_retryable(exc, status, *, retry_auth):
    if status in RETRYABLE_STATUS or (retry_auth and status == 401):
        return True
    name = type(exc).__name__.lower()
    return (isinstance(exc, (TimeoutError, ConnectionError))
            or "timeout" in name or "connection" in name)


def _retry_delay(exc):
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None) or getattr(exc, "headers", None) or {}
    value = headers.get("retry-after", headers.get("Retry-After", "4"))
    try:
        return min(30.0, max(2.0, float(value)))
    except (TypeError, ValueError):
        return 4.0


def _error_summary(exc):
    status = _error_status(exc)
    return {
        "type": type(exc).__name__,
        "status_code": status,
        "message": str(exc)[:4000],
    }


def _invoke_with_retries(call, *, retry_auth=False, before_retry=None, attempts=3):
    """Run one API call with the pilot's small, explicit retry policy."""
    attempt_log = []
    for attempt in range(1, attempts + 1):
        started = time.perf_counter()
        try:
            value = call(attempt)
        except Exception as exc:
            record = {
                "attempt": attempt,
                "outcome": "error",
                "latency_seconds": round(time.perf_counter() - started, 6),
                **_error_summary(exc),
            }
            attempt_log.append(record)
            status = record["status_code"]
            if not _is_retryable(exc, status, retry_auth=retry_auth) or attempt == attempts:
                raise InferenceError(
                    f"Vertex AI request failed after {attempt} attempt(s): {exc}",
                    details={"api_attempts": attempt_log, "last_error": record},
                ) from exc
            delay = 0.0 if status == 401 else _retry_delay(exc)
            record["retry_delay_seconds"] = delay
            if before_retry is not None:
                before_retry(status)
            time.sleep(delay)
        else:
            attempt_log.append({
                "attempt": attempt,
                "outcome": "success",
                "latency_seconds": round(time.perf_counter() - started, 6),
            })
            return value, attempt_log
    raise InferenceError("Vertex AI retry loop exhausted", details={"api_attempts": attempt_log})


def _jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        try:
            return dump(exclude_none=True, mode="json")
        except TypeError:
            return _jsonable(dump(exclude_none=True))
    enum_value = getattr(value, "value", None)
    if enum_value is not None:
        return _jsonable(enum_value)
    return str(value)


def _gemini_usage(usage):
    if usage is None:
        return None
    return {
        "input_tokens": getattr(usage, "prompt_token_count", None),
        "output_tokens": getattr(usage, "candidates_token_count", None),
        "thought_tokens": getattr(usage, "thoughts_token_count", None),
        "total_tokens": getattr(usage, "total_token_count", None),
        "raw": _jsonable(usage),
    }


def _openai_usage(usage):
    if usage is None:
        return None
    return {
        "input_tokens": getattr(usage, "prompt_tokens", None),
        "output_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
        "raw": _jsonable(usage),
    }


def _finish_reason(candidate):
    reason = getattr(candidate, "finish_reason", None)
    return _jsonable(getattr(reason, "value", reason))


def _gemini_generate(client, model, system, prompt, temperature, max_tokens):
    """Single SDK request, isolated so mocked tests need not import google-genai."""
    from google.genai import types
    return client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )


def make_vertex_gemini_chat(model, temperature, max_tokens, *, project=None,
                            location=None, timeout=120, credentials=None, client=None):
    """Create a Gemini chat callable backed by Vertex AI and ADC."""
    credentials, adc_project = _load_adc(credentials)
    project, location = resolve_vertex_settings(project, location, adc_project)
    if client is None:
        from google import genai
        from google.genai import types
        client = genai.Client(
            vertexai=True,
            credentials=credentials,
            project=project,
            location=location,
            http_options=types.HttpOptions(
                timeout=int(timeout * 1000),
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
    settings = {
        "provider": "Google Cloud Vertex AI",
        "api": "google-genai.models.generate_content",
        "sdk": "google-genai",
        "sdk_version": _package_version("google-genai"),
        "vertexai": True,
        "project": project,
        "location": location,
        "endpoint": vertex_api_host(location),
        "requested_model": model,
        "temperature": temperature,
        "max_output_tokens": max_tokens,
        "timeout_seconds": timeout,
        "auth": "Application Default Credentials",
        "thinking_config": "model default (not overridden)",
    }

    def chat(system, prompt):
        force_refresh = [False]
        started = time.perf_counter()

        def call(_attempt):
            _ensure_credentials(credentials, force=force_refresh[0])
            force_refresh[0] = False
            return _gemini_generate(client, model, system, prompt, temperature, max_tokens)

        try:
            response, attempt_log = _invoke_with_retries(
                call,
                retry_auth=True,
                before_retry=lambda status: force_refresh.__setitem__(0, status == 401),
            )
        except InferenceError as exc:
            exc.details.setdefault("backend", "vertex-gemini")
            exc.details.setdefault("requested_model", model)
            exc.details.setdefault("api_settings", dict(settings))
            raise
        latency = round(time.perf_counter() - started, 6)
        try:
            text = response.text
        except Exception as exc:
            raise InferenceError(
                f"Could not read Gemini response text: {exc}",
                details={
                    "backend": "vertex-gemini",
                    "requested_model": model,
                    "api_settings": dict(settings),
                    "api_attempts": attempt_log,
                    "last_error": _error_summary(exc),
                },
            ) from exc
        candidates = getattr(response, "candidates", None) or []
        finish_reason = _finish_reason(candidates[0]) if candidates else None
        if not isinstance(text, str) or not text.strip():
            raise InferenceError(
                "Gemini returned no visible text; adjust model/max tokens before interpreting results",
                details={
                    "backend": "vertex-gemini",
                    "requested_model": model,
                    "served_model": getattr(response, "model_version", None),
                    "api_settings": dict(settings),
                    "api_attempts": attempt_log,
                    "finish_reason": finish_reason,
                    "usage": _gemini_usage(getattr(response, "usage_metadata", None)),
                },
            )
        metadata = {
            "backend": "vertex-gemini",
            "requested_model": model,
            "served_model": getattr(response, "model_version", None),
            "api_settings": dict(settings),
            "latency_seconds": latency,
            "api_attempts": attempt_log,
            "usage": _gemini_usage(getattr(response, "usage_metadata", None)),
            "response_id": getattr(response, "response_id", None),
            "finish_reason": finish_reason,
        }
        return Completion(text=text, metadata=metadata)

    chat.settings = dict(settings)
    chat.requested_model = model
    chat.backend = "vertex-gemini"
    return chat


def make_vertex_openai_chat(model, temperature, max_tokens, *, project=None,
                            location=None, timeout=120, credentials=None,
                            client_factory=None):
    """Create a managed-open-model chat callable via Vertex AI's OpenAI endpoint."""
    credentials, adc_project = _load_adc(credentials)
    project, location = resolve_vertex_settings(project, location, adc_project)
    base_url = vertex_openai_base_url(project, location)
    if client_factory is None:
        def client_factory(token):
            from openai import OpenAI
            return OpenAI(
                base_url=base_url,
                api_key=token,
                timeout=timeout,
                max_retries=0,
            )
    settings = {
        "provider": "Google Cloud Vertex AI",
        "api": "openai.chat.completions",
        "sdk": "openai",
        "sdk_version": _package_version("openai"),
        "project": project,
        "location": location,
        "base_url": base_url,
        "endpoint": base_url + "/chat/completions",
        "requested_model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout_seconds": timeout,
        "auth": "Application Default Credentials (OAuth token refreshed per call)",
        "thinking_config": "model default (not overridden)",
    }

    def chat(system, prompt):
        force_refresh = [False]
        started = time.perf_counter()
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]

        def call(_attempt):
            _ensure_credentials(credentials, force=force_refresh[0])
            force_refresh[0] = False
            token = getattr(credentials, "token", None)
            if not token:
                raise RuntimeError("Application Default Credentials did not provide an access token")
            client = client_factory(token)
            return client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        try:
            response, attempt_log = _invoke_with_retries(
                call,
                retry_auth=True,
                before_retry=lambda status: force_refresh.__setitem__(0, status == 401),
            )
        except InferenceError as exc:
            exc.details.setdefault("backend", "vertex-openai")
            exc.details.setdefault("requested_model", model)
            exc.details.setdefault("api_settings", dict(settings))
            raise
        latency = round(time.perf_counter() - started, 6)
        choices = getattr(response, "choices", None) or []
        message = getattr(choices[0], "message", None) if choices else None
        text = getattr(message, "content", None)
        served_model = getattr(response, "model", None)
        finish_reason = getattr(choices[0], "finish_reason", None) if choices else None
        usage = _openai_usage(getattr(response, "usage", None))
        if not isinstance(text, str) or not text.strip():
            raise InferenceError(
                "Model returned no visible text; adjust model/max tokens before interpreting results",
                details={
                    "backend": "vertex-openai",
                    "requested_model": model,
                    "served_model": served_model,
                    "api_settings": dict(settings),
                    "api_attempts": attempt_log,
                    "finish_reason": finish_reason,
                    "usage": usage,
                },
            )
        metadata = {
            "backend": "vertex-openai",
            "requested_model": model,
            "served_model": served_model,
            "api_settings": dict(settings),
            "latency_seconds": latency,
            "api_attempts": attempt_log,
            "usage": usage,
            "response_id": getattr(response, "id", None),
            "finish_reason": finish_reason,
        }
        return Completion(text=text, metadata=metadata)

    chat.settings = dict(settings)
    chat.requested_model = model
    chat.backend = "vertex-openai"
    return chat
