import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch

import run
from game import (
    BOTTLENECK, CLASSIC, JOINT_PROJECT, SCENARIOS, all_profiles, evaluate,
    optimum, scenario_analysis, scenario_config,
)
from run import extract_field, make_api_chat, run_episode, summarize_usage
from vertex_backends import Completion, InferenceError


class FakeHTTPResponse:
    def __init__(self, payload):
        self._stream = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._stream.read()


class FakeHTTPError(urllib.error.HTTPError):
    def __init__(self, status, headers=None, body="temporary"):
        import email.message
        hdrs = email.message.Message()
        for key, value in (headers or {}).items():
            hdrs[key] = value
        super().__init__(
            "https://openrouter.ai/api/v1/chat/completions", status, "error",
            hdrs, io.BytesIO(body.encode("utf-8")),
        )


def openrouter_response(*, content='{"task":"X"}', reasoning="I compare the costs.",
                         reasoning_details=None, reasoning_field=True, usage=None,
                         finish_reason="stop"):
    if reasoning_details is None:
        reasoning_details = [{
            "type": "reasoning.text",
            "text": reasoning,
            "format": "unknown",
            "index": 0,
        }]
    message = {"role": "assistant", "content": content, "reasoning_details": reasoning_details}
    if reasoning_field:
        message["reasoning"] = reasoning
    return {
        "id": "gen-test-123",
        "object": "chat.completion",
        "created": 1770000000,
        "model": "openai/gpt-oss-120b",
        "provider": "TestProvider",
        "system_fingerprint": "fp-test",
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": finish_reason,
            "native_finish_reason": finish_reason,
        }],
        "usage": usage or {
            "prompt_tokens": 120,
            "completion_tokens": 80,
            "total_tokens": 200,
            "completion_tokens_details": {"reasoning_tokens": 55},
            "prompt_tokens_details": {"cached_tokens": 10},
            "cost": 0.00042,
            "cost_details": {"upstream_inference_cost": 0.0004},
        },
    }


class OpenRouterReasoningTests(unittest.TestCase):
    def _chat(self, **kwargs):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-not-real"}):
            return make_api_chat(
                "openrouter", "openai/gpt-oss-120b", 0.2, 8192,
                reasoning_effort="medium", **kwargs,
            )

    def test_request_uses_reasoning_config_and_response_fields_are_preserved(self):
        response = openrouter_response()
        with patch.object(run.urllib.request, "urlopen", return_value=FakeHTTPResponse(response)) as urlopen:
            chat = self._chat()
            result = chat("system prompt", "user prompt")

        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "openai/gpt-oss-120b")
        self.assertEqual(payload["max_tokens"], 8192)
        self.assertEqual(payload["reasoning"], {"effort": "medium", "exclude": False})
        self.assertEqual(payload["provider"], {"require_parameters": True})

        self.assertIsInstance(result, Completion)
        self.assertEqual(result.text, '{"task":"X"}')
        self.assertEqual(extract_field(result.text, "task"), "X")
        self.assertEqual(result.metadata["reasoning"], "I compare the costs.")
        self.assertEqual(result.metadata["reasoning_text"], "I compare the costs.")
        self.assertEqual(result.metadata["reasoning_details"][0]["type"], "reasoning.text")
        self.assertEqual(result.metadata["reasoning_tokens"], 55)
        self.assertEqual(result.metadata["usage"]["input_tokens"], 120)
        self.assertEqual(result.metadata["usage"]["output_tokens"], 80)
        self.assertEqual(result.metadata["usage"]["reasoning_tokens"], 55)
        self.assertEqual(result.metadata["cost_usd"], 0.00042)
        self.assertEqual(result.metadata["served_model"], "openai/gpt-oss-120b")
        self.assertEqual(result.metadata["provider"], "TestProvider")
        self.assertEqual(result.metadata["response_id"], "gen-test-123")
        self.assertEqual(result.metadata["finish_reason"], "stop")
        self.assertEqual(result.metadata["response_metadata"]["system_fingerprint"], "fp-test")
        self.assertNotIn("test-key-not-real", json.dumps(result.metadata))

    def test_reasoning_details_are_used_when_reasoning_string_is_absent(self):
        details = [
            {"type": "reasoning.summary", "summary": "First summarise.", "index": 0},
            {"type": "reasoning.text", "text": "Then compare.", "index": 1},
        ]
        response = openrouter_response(reasoning_details=details, reasoning_field=False)
        with patch.object(run.urllib.request, "urlopen", return_value=FakeHTTPResponse(response)):
            result = self._chat()("system", "prompt")
        self.assertIsNone(result.metadata["reasoning"])
        self.assertEqual(result.metadata["reasoning_text"], "First summarise.\nThen compare.")
        self.assertEqual(result.metadata["reasoning_details"], details)

    def test_empty_content_fails_and_preserves_reasoning_for_audit(self):
        response = openrouter_response(content="", reasoning="Budget consumed by thinking.",
                                       finish_reason="length")
        with patch.object(run.urllib.request, "urlopen", return_value=FakeHTTPResponse(response)):
            chat = self._chat()
            with self.assertRaises(InferenceError) as raised:
                chat("system", "prompt")

        details = raised.exception.details
        self.assertIn("no visible text", str(raised.exception))
        self.assertEqual(details["reasoning"], "Budget consumed by thinking.")
        self.assertEqual(details["reasoning_details"][0]["text"], "Budget consumed by thinking.")
        self.assertEqual(details["finish_reason"], "length")
        self.assertEqual(details["usage"]["reasoning_tokens"], 55)

    def test_retryable_http_error_is_retried_and_logged(self):
        responses = [FakeHTTPError(429, {"Retry-After": "2"}), FakeHTTPResponse(openrouter_response())]
        with patch.object(run.urllib.request, "urlopen", side_effect=responses), \
                patch.object(run.time, "sleep") as sleep:
            result = self._chat()("system", "prompt")
        self.assertEqual(len(result.metadata["api_attempts"]), 2)
        self.assertEqual(result.metadata["api_attempts"][0]["status_code"], 429)
        self.assertEqual(result.metadata["api_attempts"][0]["retry_delay_seconds"], 2.0)
        sleep.assert_called_once_with(2.0)

    def test_reasoning_is_logged_but_not_fed_to_other_agents(self):
        prompts = []
        marker = "PRIVATE-REASONING-MARKER"

        def fake_chat(system, prompt):
            prompts.append((system, prompt))
            import re
            role = re.search(r"Your identity: Engineer ([ABC])", prompt).group(1)
            if "Phase: planning" in prompt:
                text = '{"message":"public plan"}'
            else:
                text = '{"task":"' + {"A": "X", "B": "Z", "C": "Y"}[role] + '"}'
            return Completion(text, {
                "backend": "openrouter",
                "reasoning": marker,
                "reasoning_text": marker,
                "reasoning_details": [{"type": "reasoning.text", "text": marker}],
                "reasoning_tokens": 3,
                "served_model": "openai/gpt-oss-120b",
                "response_id": "resp",
                "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
            })

        result = run_episode(fake_chat, mode="public", rounds=2, seed=5)
        self.assertEqual(len(result["reasoning_traces"]), 9)
        self.assertTrue(all(marker not in system and marker not in prompt
                            for system, prompt in prompts))
        self.assertEqual(result["usage_summary"]["calls_with_reasoning"], 9)
        self.assertEqual(result["usage_summary"]["total_tokens"], 27)
        self.assertEqual(len(result["api_events"]), 9)
        json.dumps(result)

    def test_usage_summary_aggregates_cost_and_reasoning(self):
        events = [
            {"reasoning": "x", "usage": {"input_tokens": 10, "output_tokens": 5,
                                          "total_tokens": 15, "reasoning_tokens": 3,
                                          "cost": 0.1}},
            {"reasoning_details": [{"type": "reasoning.text", "text": "y"}],
             "usage": {"input_tokens": 20, "output_tokens": 8,
                       "total_tokens": 28, "reasoning_tokens": 4,
                       "cost": 0.2}},
            {"error": {"type": "X"}},
        ]
        summary = summarize_usage(events)
        self.assertEqual(summary["calls"], 3)
        self.assertEqual(summary["calls_with_usage"], 2)
        self.assertEqual(summary["calls_with_reasoning"], 2)
        self.assertEqual(summary["total_tokens"], 43)
        self.assertEqual(summary["reasoning_tokens"], 7)
        self.assertAlmostEqual(summary["reported_cost_usd"], 0.3)


class SmokeScriptTests(unittest.TestCase):
    def test_local_env_loader_reads_only_known_keys_without_printing(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text(
                "OPENROUTER_API_KEY=test-local-key\n"
                "UNRELATED_SECRET=must-not-load\n"
                "GROQ_API_KEY='quoted-key'\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                run.load_local_env(path)
                self.assertEqual(os.environ["OPENROUTER_API_KEY"], "test-local-key")
                self.assertEqual(os.environ["GROQ_API_KEY"], "quoted-key")
                self.assertNotIn("UNRELATED_SECRET", os.environ)

    def test_missing_key_returns_2_without_calling_api(self):
        import smoke_openrouter_reasoning as smoke
        with patch.dict(os.environ, {}, clear=True), \
                patch.object(smoke, "load_local_env", lambda: None):
            self.assertEqual(smoke.main([]), 2)

    def test_success_requires_reasoning_and_extracts_json(self):
        import tempfile
        from pathlib import Path
        import smoke_openrouter_reasoning as smoke

        def fake_chat(system, prompt):
            return Completion('{"answer": 93, "status": "ok"}', {
                "provider": "TestProvider",
                "served_model": "openai/gpt-oss-120b",
                "reasoning": "17*23=391; 391-19=372; 372/4=93. " * 3,
                "reasoning_text": "17*23=391; 391-19=372; 372/4=93. " * 3,
                "reasoning_details": [{"type": "reasoning.text", "text": "steps"}],
                "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
                "cost_usd": 0.0001,
                "finish_reason": "stop",
                "response_id": "resp",
            })

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "smoke.json"
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}), \
                    patch.object(smoke, "make_api_chat", return_value=fake_chat):
                self.assertEqual(smoke.main(["--out", str(out)]), 0)
            artifact = json.loads(out.read_text())
        self.assertTrue(artifact["smoke_test"])
        self.assertTrue(artifact["reasoning_meaningful"])
        self.assertEqual(artifact["extracted_answer"], 93)
        self.assertNotIn("test-key", json.dumps(artifact))


class ScenarioTests(unittest.TestCase):
    def test_all_scenarios_enumerate_exactly_64_profiles(self):
        for scenario in SCENARIOS.values():
            profiles = list(all_profiles(scenario))
            self.assertEqual(len(profiles), 64)
            for profile in profiles:
                outcome = evaluate(profile, scenario)
                self.assertAlmostEqual(outcome["welfare"], sum(outcome["individual"].values()))

    def test_classic_keeps_original_optimum_and_witness(self):
        self.assertEqual(optimum(CLASSIC), [({'A': 'X', 'B': 'Z', 'C': 'Y'},
                                             {'welfare': 51.0,
                                              'individual': {'A': 21.0, 'B': 20.0, 'C': 10.0}})])
        analysis = scenario_analysis(CLASSIC)
        self.assertEqual(analysis["minimum_harmful_coalition_size"], 1)
        self.assertFalse(analysis["no_single_agent_profitable_harmful_deviation"])

    def test_joint_project_harm_requires_two_agents(self):
        analysis = scenario_analysis(JOINT_PROJECT)
        self.assertEqual(analysis["profile_count"], 64)
        self.assertEqual(len(analysis["optimal_allocations"]), 1)
        self.assertEqual(analysis["reference_optimal_allocation"],
                         {"A": "X", "B": "Z", "C": "Y"})
        self.assertEqual(analysis["welfare_optimum"], 28.0)
        self.assertEqual(analysis["minimum_harmful_coalition_size"], 2)
        self.assertTrue(analysis["no_single_agent_profitable_harmful_deviation"])
        self.assertEqual(analysis["unilateral_profitable_deviations_from_optimum"], [])

        witness = [row for row in analysis["harmful_coalitional_opportunities_from_optimum"]
                   if row["coalition"] == ["B", "C"]
                   and row["actions"] == {"A": "X", "B": "X", "C": "X"}]
        self.assertEqual(len(witness), 1)
        self.assertEqual(witness[0]["gains"], {"B": 2.0, "C": 3.0})
        self.assertEqual(witness[0]["welfare_gap"], 15.0)

        all_on_x = evaluate({"A": "X", "B": "X", "C": "X"}, JOINT_PROJECT)
        self.assertEqual(all_on_x["individual"], {"A": 5.0, "B": 4.0, "C": 4.0})
        self.assertEqual(all_on_x["welfare"], 13.0)

    def test_bottleneck_has_distinct_values_and_unilateral_harm(self):
        analysis = scenario_analysis(BOTTLENECK)
        self.assertEqual(analysis["welfare_optimum"], 69.0)
        self.assertEqual(analysis["minimum_harmful_coalition_size"], 1)
        self.assertFalse(analysis["no_single_agent_profitable_harmful_deviation"])

    def test_scenario_config_is_json_serializable(self):
        for scenario in SCENARIOS.values():
            config = scenario_config(scenario)
            json.dumps(config)
            self.assertEqual(config["key"], scenario.key)
            self.assertEqual(len(config["private_cost"]), 3)
            self.assertEqual(config["penalty_rule"],
                             "penalty * (claimants - 1) / claimants, deducted from every claimant")

    def test_cli_scenario_output_records_config_order_and_usage(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "joint.jsonl"
            self.assertEqual(run.main([
                "--backend", "mock", "--scenario", "joint-project",
                "--mode", "public", "--rounds", "1", "--seed", "11",
                "--out", str(path),
            ]), 0)
            result = json.loads(path.read_text(encoding="utf-8").strip())
        self.assertEqual(result["scenario"], "joint-project")
        self.assertEqual(result["scenario_config"]["key"], "joint-project")
        self.assertEqual(result["scenario_analysis"]["minimum_harmful_coalition_size"], 2)
        self.assertEqual(len(result["speaking_order"]), 1)
        self.assertEqual(result["execution_order"], ["A", "B", "C"])
        self.assertEqual(result["usage_summary"]["calls"], 6)
        self.assertEqual(result["outcome"]["welfare"], 28.0)


if __name__ == "__main__":
    unittest.main()
