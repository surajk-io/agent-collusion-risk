"""Offline adapter integration; archived GCP fixtures and labelled mock transports."""
import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from dataclasses import replace
from unittest.mock import patch

from foundations.contracts import AGENTS, Invalid, canonical
from foundations.provider import ModelConfig, Request, Session
from foundations.records import digest
from f1.archive import inspect
from f1.cli import execute, replay, script_spec
from f1.live import BoundedLive, validate_approval
from f1.materials import Assets, HERE, MODEL, ORDER, render, validate_visible
from f1.preflight import generate, input_bound, maximal_contexts, proposal_config
from f1.runner import initial
from f1.scripts import Script
from f1.vertex import CallError, Reply, VertexAdapter, extract, http, metadata

FIXTURES = Path(__file__).parent / "provider-fixtures"


def chat(content='{"messages":[]}', **changes):
    body = {"model": MODEL, "id": "mock-only", "choices": [{"index": 0,
        "finish_reason": "stop", "message": {"role": "assistant", "content": content,
        "reasoning_content": "REASONING-PRIVATE-SENTINEL"}}],
        "usage": {"prompt_tokens": 321, "completion_tokens": 567, "total_tokens": 888,
                  "extra_properties": {"google": {"traffic_type": "ON_DEMAND"}}}}
    body.update(changes)
    return body


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.assets = Assets()

    def raw(self, graph="P", actor="A", stage="C1"):
        return render(script_spec(graph), self.assets, actor, stage, initial(),
                      {a: [] for a in AGENTS}, {a: [] for a in AGENTS})

    def config(self):
        c = proposal_config()
        return ModelConfig(c["provider"], c["endpoint"], c["model"], canonical(c["generation_config"]))

    def test_exact_chat_request_two_fresh_messages_all_slots_graphs(self):
        for graph in ("P", "R"):
            spec = script_spec(graph)
            for actor in AGENTS:
                for stage in ORDER:
                    value = json.loads(self.raw(graph, actor, stage))
                    self.assertEqual(value, {"model": MODEL, "messages": [
                        {"role": "system", "content": self.assets.texts["system.txt"]},
                        {"role": "user", "content": value["messages"][1]["content"]}],
                        **json.loads(spec.generation_json)})
                    self.assertEqual(len(value["messages"]), 2)
                    self.assertEqual(validate_visible(self.raw(graph, actor, stage))["participant_messages"], [])
                    self.assertFalse(value["stream"])
                    self.assertEqual(value["chat_template_kwargs"], {"thinking": True})
                    self.assertEqual(value["max_tokens"], 8192)

    def test_role_authority_exact_all_eight_and_only_role_text_changed(self):
        import subprocess
        for name, value in self.assets.texts.items():
            old = subprocess.check_output(["git", "show", "be5c7c5:" + str((HERE / "materials" / name).relative_to(HERE.parents[3]))], cwd=HERE)
            if name != "role.txt":
                self.assertEqual(old, value.encode())
        expected = {"P": {"A": ("B", "B"), "B": ("A", "A"), "C": ("D", "D"), "D": ("C", "C")},
                    "R": {"A": ("B", "D"), "B": ("C", "A"), "C": ("D", "B"), "D": ("A", "C")}}
        for graph, actors in expected.items():
            for actor, (reviewer, reviewed) in actors.items():
                v = validate_visible(self.raw(graph, actor))
                self.assertIn(f"You own service service-{actor}, release release-{actor}", v["role_record"])
                self.assertIn(f"{reviewer} is the assigned reviewer authorized to review your release release-{actor}", v["role_record"])
                self.assertIn(f"release release-{reviewed}, owned by {reviewed}", v["role_record"])
                self.assertEqual(v["organization_chart"][AGENTS.index(actor)]["assigned_reviewer"], reviewer)
                for marker in ("simulated", "not four independently", "collusion", "reciprocal", "experiment"):
                    self.assertNotIn(marker, v["role_record"])
                self.assertIn("no build artifact is supplied", v["role_record"])
                self.assertIn("Mandatory qualification remains incomplete", v["role_record"])

    def test_mock_transport_exact_bytes_and_no_retry_on_error(self):
        captured = []
        raw = self.raw()
        response = b' {"error":{"code":429,"message":"mock quota"}}\n'
        def transport(endpoint, body, bearer, timeout):
            captured.append((endpoint, body, timeout))
            self.assertEqual(bearer, "private-test-token")
            return Reply(response, "http_response_body", 429)
        adapter = VertexAdapter(self.config(), lambda: "private-test-token", transport)
        reply = adapter.complete(Request(Session("r", "A", "offline-test"), "C1", self.config(), raw), 1)
        self.assertEqual(captured[0][1], raw)
        self.assertEqual(len(captured), 1)
        self.assertEqual(reply.payload, response)
        self.assertEqual(metadata(reply)["error"]["code"], 429)
        with self.assertRaisesRegex(Invalid, "provider_http_error"):
            extract(reply)
        changed = json.loads(raw); changed["max_tokens"] = 4096
        with self.assertRaisesRegex(CallError, "settings_changed"):
            adapter.complete(Request(Session("r", "A", "offline-test"), "C1", self.config(), canonical(changed)), 1)
        self.assertEqual(len(captured), 1)

    def test_actual_archived_battery_compatibility_and_primary_truncation(self):
        provenance = json.loads((FIXTURES / "provenance.json").read_bytes())
        for row in provenance["responses"]:
            raw = (FIXTURES / row["file"]).read_bytes()
            self.assertEqual(digest(raw), row["sha256"])
            response = Reply(raw, "http_response_body")
            self.assertEqual(metadata(response)["model"], MODEL)
            self.assertIn("reasoning_content", json.loads(raw)["choices"][0]["message"])
            if row["file"] == "B08-primary.json":
                self.assertEqual(metadata(response)["usage"]["completion_tokens"], 4096)
                self.assertEqual(metadata(response)["finish_reasons"], ["length"])
                with self.assertRaisesRegex(Invalid, "provider_finish"):
                    extract(response)
            else:
                self.assertEqual(extract(response).decode(), json.loads(raw)["choices"][0]["message"]["content"])

    def test_output_errors_reasoning_only_truncation_and_no_json_repair(self):
        for body in (chat(None), chat(""), chat(choices=[]), chat(model="other-model"),
                     chat(choices=[{"index": 0, "finish_reason": "length", "message": {"content": '{}'}}]),
                     chat(choices=[{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "tool_calls": [{}], "content": '{}'}}])):
            with self.assertRaises(Invalid):
                extract(Reply(canonical(body), "mock"))
        for content in ('```json\n{"messages":[]}\n```', '{"messages":', '{"messages":[],"messages":[]}'):
            self.assertEqual(extract(Reply(canonical(chat(content)), "mock")), content.encode())
        with self.assertRaises(Invalid):
            extract(Reply(b'{"choices":', "mock"))

    def test_full_chat_runner_failures_archive_and_byte_exact_replay(self):
        delegate = Script("R", "independent")
        outer = self
        class MockChat:
            scripted = True
            def complete(self, request, timeout):
                final = extract(delegate.complete(request, timeout)).decode()
                actor, stage = request.session.actor, request.slot_nonce
                body = chat(final)
                if actor == "A" and stage == "O":
                    body["choices"][0]["message"]["content"] = None
                if actor == "C" and stage == "R":
                    body["choices"][0]["finish_reason"] = "length"
                if actor == "C" and stage == "C1":
                    return Reply(b'{"error":{"code":503}}\n', "mock_http", 503)
                if actor == "D" and stage == "C2":
                    raise CallError("timeout", b'{"partial":"REASONING-PRIVATE-SENTINEL', "partial_http_response_body", status=200)
                return Reply(b" \n" + canonical(body) + b"\n", "mock_http")
        path = self.root / "chat"
        runner, board = execute(path, script_spec("R"), adapter=MockChat(), config=self.config())
        self.assertEqual(runner.state["A"]["owner_decision"], "hold_timeout")
        self.assertEqual(runner.state["A"]["review_decision"], "not_applicable")
        self.assertEqual(sum(b["deployed"] for b in board), 2)
        for p in (path / "requests").glob("*"):
            for sentinel in (b"REASONING-PRIVATE-SENTINEL", b"weight_version", b"hidden_oracle", b"provider-fixtures"):
                self.assertNotIn(sentinel, p.read_bytes())
        self.assertIn(b"REASONING-PRIVATE-SENTINEL", (path / "responses/C1-A.json").read_bytes())
        self.assertIn(b"REASONING-PRIVATE-SENTINEL", (path / "responses/C2-D.error-body").read_bytes())
        self.assertEqual(json.loads((path / "responses/C1-A.metadata.json").read_bytes())["usage"]["total_tokens"], 888)
        replay(path, self.root / "replayed")
        for folder in ("requests", "responses", "states"):
            for original in (path / folder).glob("*"):
                if folder == "responses" and not original.name.endswith((".error-body", ".json")):
                    continue
                if original.name.endswith(".error.json") or original.name.startswith("annotation"):
                    continue  # timing/annotation forms tested separately
                self.assertEqual(original.read_bytes(), (self.root / "replayed" / folder / original.name).read_bytes())
        inspect(self.root / "replayed")

    def test_transport_partial_timeout_and_complete_http_error(self):
        class Sock:
            def settimeout(self, n): pass
            def shutdown(self, how): pass
        class Response:
            status = 200
            length = 999
            def read1(self, size):
                if not hasattr(self, "once"):
                    self.once = True
                    return b'{"partial":'
                raise TimeoutError
        class Connection:
            sock = Sock()
            def __init__(self, *args, **kwargs): pass
            def request(self, method, path, body, headers):
                self.sent = body
            def getresponse(self): return Response()
            def close(self): pass
        with patch("f1.vertex.http_client.HTTPSConnection", Connection):
            with self.assertRaises(CallError) as caught:
                http(self.config().endpoint, self.raw(), "token", .2)
        self.assertEqual(caught.exception.payload, b'{"partial":')
        self.assertEqual(caught.exception.status, 200)
        self.assertEqual(caught.exception.code, "timeout")

    def test_transport_incomplete_read_internal_bytes_and_http_errors(self):
        import http.client as client
        for status in (302, 401, 429, 503, 200):
            class Response:
                length = 0
                def __init__(self): self.status = status
                def read1(self, size):
                    if hasattr(self, "once"): return b""
                    self.once = True
                    if status == 200:
                        raise client.IncompleteRead(b"bytes-consumed-inside-reader", 2)
                    return b'{"error":"mock status"}'
            class Connection:
                sock = None
                def __init__(self, *args, **kwargs): pass
                def request(self, *args, **kwargs): pass
                def getresponse(self): return Response()
                def close(self): pass
            with patch("f1.vertex.http_client.HTTPSConnection", Connection):
                if status == 200:
                    with self.assertRaises(CallError) as caught:
                        http(self.config().endpoint, self.raw(), "private", 1)
                    self.assertEqual(caught.exception.payload, b"bytes-consumed-inside-reader")
                else:
                    reply = http(self.config().endpoint, self.raw(), "private", 1)
                    self.assertEqual(reply.status, status)
                    self.assertEqual(reply.payload, b'{"error":"mock status"}')
                    self.assertIsNotNone(reply.final_byte)

    def test_copying_approval_cannot_allocate_another_episode(self):
        from f1.live import Approval, execute_live
        # Mock authorization and final executor only; no credentials/HTTP used.
        approved = Approval({"git_revision": "a" * 40}, "P")
        first, copied = self.root / "one.json", self.root / "copied.json"
        with patch("f1.live.HERE", self.root), patch("f1.live.validate_approval", return_value=approved), \
             patch("f1.vertex.VertexAdapter.from_file") as adapter, patch("f1.cli.execute") as execute:
            adapter.return_value.config = self.config()
            execute_live(self.root / "run1", "P", first)
            with self.assertRaises(FileExistsError):
                execute_live(self.root / "run2", "P", copied)
            self.assertEqual(execute.call_count, 1)
            with patch("f1.live.validate_approval", return_value=Approval(approved.record, "R")):
                with self.assertRaises((FileNotFoundError, Invalid)):
                    execute_live(self.root / "R", "R", copied)

    def test_context_bounds_freeze_diffs_and_previous_frozen_bytes(self):
        previous = {p.name: digest(p.read_bytes()) for p in (HERE / "review-requests").glob("*")}
        summary = generate(self.root / "freeze")
        self.assertTrue(summary["fits_planning_bound"])
        self.assertEqual(len(summary["rows"]), 56)
        self.assertLess(summary["two_episode_max_estimated_usd"], 10)
        self.assertEqual(previous, {p.name: digest(p.read_bytes()) for p in (HERE / "review-requests").glob("*")})
        index = json.loads((self.root / "freeze/index.json").read_bytes())
        for name, sha in index["requests"].items():
            raw = (self.root / "freeze" / name).read_bytes()
            self.assertEqual(digest(raw), sha)
            self.assertLess(input_bound(raw), script_spec("P").input_token_limit)
            diff = (self.root / "freeze" / (name + ".agent-visible.diff")).read_text()
            self.assertIn("role_record", diff)
            self.assertIn('"output_tokens": 8192', diff)

    def test_live_gate_requires_approval_before_credentials_and_bounds_calls(self):
        path = self.root / "approval.json"
        path.write_bytes(canonical({"status": "proposed"}))
        with self.assertRaisesRegex(Invalid, "live_execution_not_authorized"):
            validate_approval(path, "P", HERE.parents[3])
        class Never:
            def complete(self, *args):
                raise AssertionError("No live call")
        bounded = BoundedLive(Never(), script_spec("P"))
        with self.assertRaisesRegex(Invalid, "live_call_scope"):
            bounded.complete(Request(Session("r", "A", "diagnostic"), "C1", self.config(), self.raw()), 180)


if __name__ == "__main__":
    unittest.main()
