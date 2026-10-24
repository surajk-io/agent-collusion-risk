import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import vertex_backends as vb
from run import main, make_api_chat, run_episode


class FakeCredentials:
    def __init__(self, token="adc-token-1", valid=True):
        self.token = token
        self.valid = valid
        self.refresh_calls = 0

    def refresh(self, request):
        self.refresh_calls += 1
        self.token = f"adc-token-{self.refresh_calls + 1}"
        self.valid = True


class FakeHTTPError(Exception):
    def __init__(self, status_code, headers=None):
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code
        self.response = SimpleNamespace(status_code=status_code, headers=headers or {})


def gemini_response(text='{"message":"hello"}'):
    return SimpleNamespace(
        text=text,
        model_version="gemini-3.7-flash",
        response_id="gemini-response-1",
        candidates=[SimpleNamespace(finish_reason=SimpleNamespace(value="STOP"))],
        usage_metadata=SimpleNamespace(
            prompt_token_count=10,
            candidates_token_count=5,
            thoughts_token_count=2,
            total_token_count=17,
        ),
    )


class FakeCompletions:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeOpenAIClient:
    def __init__(self, completions):
        self.chat = SimpleNamespace(completions=completions)


def openai_response(text='{"task":"X"}'):
    return SimpleNamespace(
        id="openai-response-1",
        model="deepseek-ai/deepseek-v4.1-flash-maas",
        choices=[SimpleNamespace(
            message=SimpleNamespace(content=text),
            finish_reason="stop",
        )],
        usage=SimpleNamespace(prompt_tokens=11, completion_tokens=2, total_tokens=13),
    )


class VertexSettingsTests(unittest.TestCase):
    def test_global_and_regional_endpoint_formats(self):
        self.assertEqual(
            vb.vertex_openai_base_url("proj", "global"),
            "https://aiplatform.googleapis.com/v1/projects/proj/locations/global/endpoints/openapi",
        )
        self.assertEqual(
            vb.vertex_openai_base_url("proj", "us-central1"),
            "https://us-central1-aiplatform.googleapis.com/v1/projects/proj/locations/us-central1/endpoints/openapi",
        )
        self.assertEqual(
            vb.vertex_openai_base_url("proj", "us"),
            "https://aiplatform.us.rep.googleapis.com/v1/projects/proj/locations/us/endpoints/openapi",
        )
        self.assertEqual(
            vb.vertex_openai_base_url("proj", "eu"),
            "https://aiplatform.eu.rep.googleapis.com/v1/projects/proj/locations/eu/endpoints/openapi",
        )

    def test_project_and_location_resolution(self):
        with patch.dict("os.environ", {"GOOGLE_CLOUD_PROJECT": "env-proj",
                                      "GOOGLE_CLOUD_LOCATION": "us-east5"}, clear=True):
            self.assertEqual(vb.resolve_vertex_settings(), ("env-proj", "us-east5"))
            self.assertEqual(vb.resolve_vertex_settings("arg-proj", "global"),
                             ("arg-proj", "global"))
        self.assertEqual(vb.resolve_vertex_settings("adc-proj", None, "adc-proj"),
                         ("adc-proj", "global"))
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                vb.resolve_vertex_settings(location="global")

    def test_make_api_chat_dispatches_vertex_backends(self):
        with patch("run.make_vertex_gemini_chat", return_value="gemini-chat") as gemini:
            self.assertEqual(
                make_api_chat("vertex-gemini", "gemini-3.7-flash", 0.5, 512,
                              project="proj", location="global"),
                "gemini-chat",
            )
            gemini.assert_called_once_with(
                "gemini-3.7-flash", 0.5, 512, project="proj", location="global", timeout=120,
            )
        with patch("run.make_vertex_openai_chat", return_value="openai-chat") as openai_chat:
            self.assertEqual(
                make_api_chat("vertex-openai", "deepseek-ai/deepseek-v4.1-flash-maas", 0.5, 512,
                              project="proj", location="global"),
                "openai-chat",
            )
            openai_chat.assert_called_once_with(
                "deepseek-ai/deepseek-v4.1-flash-maas", 0.5, 512,
                project="proj", location="global", timeout=120,
            )


class VertexGeminiTests(unittest.TestCase):
    def test_mocked_success_records_audit_metadata(self):
        credentials = FakeCredentials()
        with patch.object(vb, "_gemini_generate", return_value=gemini_response()) as generate:
            chat = vb.make_vertex_gemini_chat(
                "gemini-3.7-flash", 0.2, 64,
                project="proj", location="global", credentials=credentials, client=object(),
            )
            result = chat("system prompt", "user prompt")

        self.assertIsInstance(result, vb.Completion)
        self.assertEqual(result.text, '{"message":"hello"}')
        self.assertEqual(result.metadata["requested_model"], "gemini-3.7-flash")
        self.assertEqual(result.metadata["served_model"], "gemini-3.7-flash")
        self.assertEqual(result.metadata["usage"]["input_tokens"], 10)
        self.assertEqual(result.metadata["usage"]["output_tokens"], 5)
        self.assertEqual(result.metadata["usage"]["thought_tokens"], 2)
        self.assertEqual(result.metadata["api_settings"]["project"], "proj")
        self.assertEqual(result.metadata["api_settings"]["temperature"], 0.2)
        self.assertEqual(result.metadata["api_attempts"][0]["outcome"], "success")
        self.assertGreaterEqual(result.metadata["latency_seconds"], 0)
        generate.assert_called_once_with(
            generate.call_args.args[0], "gemini-3.7-flash", "system prompt",
            "user prompt", 0.2, 64,
        )

    def test_retry_on_429_is_logged(self):
        credentials = FakeCredentials()
        outcomes = [FakeHTTPError(429, {"Retry-After": "2"}), gemini_response()]
        with patch.object(vb, "_gemini_generate", side_effect=outcomes), \
                patch.object(vb.time, "sleep") as sleep:
            chat = vb.make_vertex_gemini_chat(
                "gemini-3.7-flash", 0.2, 64,
                project="proj", location="global", credentials=credentials, client=object(),
            )
            result = chat("system", "prompt")

        self.assertEqual(len(result.metadata["api_attempts"]), 2)
        self.assertEqual(result.metadata["api_attempts"][0]["status_code"], 429)
        self.assertEqual(result.metadata["api_attempts"][0]["retry_delay_seconds"], 2.0)
        sleep.assert_called_once_with(2.0)

    def test_401_refreshes_gemini_credentials_and_retries(self):
        credentials = FakeCredentials()
        outcomes = [FakeHTTPError(401), gemini_response()]
        refreshes = []

        def ensure(creds, force=False):
            if force:
                refreshes.append(True)
                creds.refresh(None)

        with patch.object(vb, "_gemini_generate", side_effect=outcomes), \
                patch.object(vb, "_ensure_credentials", side_effect=ensure), \
                patch.object(vb.time, "sleep"):
            chat = vb.make_vertex_gemini_chat(
                "gemini-3.7-flash", 0.2, 64,
                project="proj", location="global", credentials=credentials, client=object(),
            )
            result = chat("system", "prompt")

        self.assertEqual(refreshes, [True])
        self.assertEqual(len(result.metadata["api_attempts"]), 2)
        self.assertEqual(result.metadata["api_attempts"][0]["status_code"], 401)

    def test_empty_visible_text_fails_without_fabrication(self):
        credentials = FakeCredentials()
        with patch.object(vb, "_gemini_generate", return_value=gemini_response(text=None)):
            chat = vb.make_vertex_gemini_chat(
                "gemini-3.7-flash", 0.2, 64,
                project="proj", location="global", credentials=credentials, client=object(),
            )
            with self.assertRaises(vb.InferenceError) as raised:
                chat("system", "prompt")
        self.assertIn("no visible text", str(raised.exception))
        self.assertEqual(raised.exception.details["requested_model"], "gemini-3.7-flash")


class VertexOpenAITests(unittest.TestCase):
    def test_mocked_open_model_success_records_request_and_response(self):
        credentials = FakeCredentials()
        completions = FakeCompletions([openai_response()])
        tokens = []
        chat = vb.make_vertex_openai_chat(
            "deepseek-ai/deepseek-v4.1-flash-maas", 0.3, 128,
            project="proj", location="global", credentials=credentials,
            client_factory=lambda token: tokens.append(token) or FakeOpenAIClient(completions),
        )
        result = chat("system prompt", "user prompt")

        self.assertEqual(result.text, '{"task":"X"}')
        self.assertEqual(result.metadata["served_model"], "deepseek-ai/deepseek-v4.1-flash-maas")
        self.assertEqual(result.metadata["usage"]["input_tokens"], 11)
        self.assertEqual(result.metadata["usage"]["output_tokens"], 2)
        self.assertEqual(result.metadata["api_settings"]["base_url"],
                         "https://aiplatform.googleapis.com/v1/projects/proj/locations/global/endpoints/openapi")
        self.assertEqual(tokens, ["adc-token-1"])
        call = completions.calls[0]
        self.assertEqual(call["model"], "deepseek-ai/deepseek-v4.1-flash-maas")
        self.assertEqual(call["temperature"], 0.3)
        self.assertEqual(call["max_tokens"], 128)
        self.assertEqual(call["messages"], [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "user prompt"},
        ])

    def test_401_refreshes_token_and_retries(self):
        credentials = FakeCredentials()
        completions = FakeCompletions([FakeHTTPError(401), openai_response()])
        tokens = []

        def ensure(creds, force=False):
            if force:
                creds.refresh(None)

        with patch.object(vb, "_ensure_credentials", side_effect=ensure), \
                patch.object(vb.time, "sleep"):
            chat = vb.make_vertex_openai_chat(
                "deepseek-ai/deepseek-v4.1-flash-maas", 0.3, 128,
                project="proj", location="global", credentials=credentials,
                client_factory=lambda token: tokens.append(token) or FakeOpenAIClient(completions),
            )
            result = chat("system", "prompt")

        self.assertEqual(tokens, ["adc-token-1", "adc-token-2"])
        self.assertEqual(len(result.metadata["api_attempts"]), 2)
        self.assertEqual(result.metadata["api_attempts"][0]["status_code"], 401)

    def test_non_retryable_400_is_surfaced(self):
        credentials = FakeCredentials()
        completions = FakeCompletions([FakeHTTPError(400)])
        chat = vb.make_vertex_openai_chat(
            "deepseek-ai/deepseek-v4.1-flash-maas", 0.3, 128,
            project="proj", location="global", credentials=credentials,
            client_factory=lambda token: FakeOpenAIClient(completions),
        )
        with self.assertRaises(vb.InferenceError) as raised:
            chat("system", "prompt")
        self.assertEqual(raised.exception.details["last_error"]["status_code"], 400)
        self.assertEqual(len(completions.calls), 1)


class RunnerMetadataTests(unittest.TestCase):
    def test_main_mock_preserves_cli_and_records_inference_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mock.jsonl"
            self.assertEqual(main([
                "--backend", "mock", "--mode", "no-chat", "--rounds", "0",
                "--seed", "7", "--out", str(path),
            ]), 0)
            result = json.loads(path.read_text(encoding="utf-8").strip())
        self.assertEqual(result["backend"], "mock")
        self.assertEqual(result["requested_model"], "scripted-smoke-test")
        self.assertTrue(result["mock_not_llm"])
        self.assertEqual(result["inference_settings"]["requested_model"], "scripted-smoke-test")
        self.assertIsNone(result["attempted_explicit_collusion"])
        self.assertIsNone(result["successful_explicit_collusion"])

    def test_completion_metadata_is_preserved_in_transcript_and_api_events(self):
        def fake_chat(system, prompt):
            import re
            role = re.search(r"Your identity: Engineer ([ABC])", prompt).group(1)
            if "Phase: planning" in prompt:
                text = '{"message":"planning"}'
            else:
                text = '{"task":"' + {"A": "X", "B": "Z", "C": "Y"}[role] + '"}'
            return vb.Completion(text, {
                "backend": "fake-vertex",
                "requested_model": "requested-model",
                "served_model": "served-model",
                "latency_seconds": 0.01,
                "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
            })

        result = run_episode(fake_chat, mode="public", rounds=1, seed=3)
        self.assertEqual(result["outcome"]["welfare"], 51.0)
        self.assertIsNone(result["attempted_explicit_collusion"])
        self.assertIsNone(result["successful_explicit_collusion"])
        self.assertEqual(len(result["api_events"]), 6)
        self.assertEqual(result["api_events"][0]["served_model"], "served-model")
        self.assertEqual(result["api_events"][0]["raw_output"], '{"message":"planning"}')
        json.dumps(result)

    def test_inference_failure_is_traced_before_reraising(self):
        def failing_chat(system, prompt):
            raise vb.InferenceError("simulated outage", details={
                "requested_model": "m",
                "api_settings": {"location": "global"},
                "api_attempts": [{"attempt": 1, "outcome": "error", "status_code": 503}],
                "last_error": {"type": "ServerError", "status_code": 503},
            })

        events = []
        with self.assertRaises(vb.InferenceError):
            run_episode(failing_chat, mode="no-chat", rounds=0, callback=events.append)

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["agent"], "A")
        self.assertEqual(event["error"]["type"], "InferenceError")
        self.assertEqual(event["error"]["requested_model"], "m")
        self.assertEqual(event["error"]["api_attempts"][0]["status_code"], 503)
        self.assertNotIn("raw_output", event)
        self.assertGreaterEqual(event["latency_seconds"], 0)
        json.dumps(event)


if __name__ == "__main__":
    unittest.main()
