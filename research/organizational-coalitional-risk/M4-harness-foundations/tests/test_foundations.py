import itertools
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from foundations.contracts import (
    AGENTS, P, R, SLOT_ORDER_REFERENCE, Invalid, Limits, communication, decode,
    decision, named_schema, canonical,
)
from foundations.provider import (
    ModelConfig, Request, ScriptedAdapter, Session, invoke, within_cutoff,
)
from foundations.records import Journal, blob, digest, provenance, unblob
from foundations.visibility import Barrier, Messages, project
from fixtures import LIMITS, action, batch, snapshot


class SchemaTests(unittest.TestCase):
    def test_exact_vendored_schema(self):
        path = Path(__file__).parents[1] / "candidate-schemas.json"
        # Pin independently to the bytes of f01b498, not the current branch tip.
        expected = json.loads((path.parent / "sources.json").read_bytes())["schema_sha256"]
        self.assertEqual(digest(path.read_bytes()), expected)

    def test_named_schema_is_constrained_and_metadata_free(self):
        for name in ("CommunicationBatch", "OwnerDecision", "ReviewSlotOutput"):
            raw = canonical(named_schema(name))
            for forbidden in (b"$comment", b"title", b"urn:m3", b"HistoryResponse"):
                self.assertNotIn(forbidden, raw)
            with self.assertRaises(Invalid):
                decode(b"{}", name)
        with self.assertRaises(Invalid):
            named_schema("unconstrained_root")

    def test_bad_output_bytes(self):
        invalid = [b'{"messages":[],"messages":[]}', b'```json\n{}\n```',
                   b'{}{}', b'{"messages":[],"actor":"B"}', b'\xff', b'{',
                   b'{"messages":[],"extra":NaN}',
                   b'{"messages":[{"recipients":["B"],"body":"\\ud800"}]}']
        for raw in invalid:
            with self.subTest(raw=raw), self.assertRaises(Invalid):
                communication(raw, "A", LIMITS)

    def test_recipients_all_actors_and_utf8_limits(self):
        for actor in AGENTS:
            peers = [a for a in AGENTS if a != actor]
            for recipients in ([actor], [], ["E"], ["a"], [peers[0]] * 2):
                with self.subTest(actor=actor, recipients=recipients), self.assertRaises(Invalid):
                    communication(batch((recipients, "x")), actor, LIMITS)
            for body in (" " * 1024, "é" * 512, " "):
                self.assertEqual(communication(batch((peers, body)), actor, LIMITS)
                                 ["messages"][0]["body"], body)
            for body in ("", "é" * 513, "x" * 1025):
                with self.assertRaises(Invalid):
                    communication(batch((peers, body)), actor, LIMITS)
            communication(batch(), actor, LIMITS)
            communication(batch(*[([p], "x") for p in peers]), actor, LIMITS)
            communication(batch((peers[:2], "x"), (peers[2:], "y")), actor, LIMITS)
            with self.assertRaises(Invalid):
                communication(batch((peers[:2], "x"), ([peers[0]], "y")), actor, LIMITS)
        # Alternate provisional configuration is explicit and testable.
        communication(batch((["B"], "x"), (["B"], "y")), "A",
                      Limits(1024, 2048, False))

    def test_decision_authority_all_actors_graphs_and_versions(self):
        for graph, actor in itertools.product((P, R), AGENTS):
            s = snapshot(graph)
            own = s.own(actor)
            for choice in ("submit", "hold", "escalate"):
                decision(action(own, choice), actor, "O", s, own.binding, LIMITS)
            submitted = snapshot(graph, True)
            reviewed = submitted.reviewed(actor)
            for choice in ("approve", "reject"):
                decision(action(reviewed, choice), actor, "R", submitted,
                         reviewed.binding, LIMITS)
            for other in submitted.releases:
                if other != reviewed:
                    with self.assertRaises(Invalid):
                        decision(action(other, "approve"), actor, "R", submitted,
                                 reviewed.binding, LIMITS)
            for change in ({"episode": "other"}, {"candidate_hash": "a" * 64},
                           {"build_hash": "b" * 64}, {"evidence_hash": "c" * 64}):
                with self.assertRaises(Invalid):
                    decision(action(reviewed, "approve"), actor, "R", submitted,
                             replace(reviewed.binding, **change), LIMITS)
            with self.assertRaises(Invalid):
                decision(action(own, "submit"), actor, "C1", s, own.binding, LIMITS)
            with self.assertRaises(Invalid):
                decision(action(own, "submit"), actor, "O", submitted, own.binding, LIMITS)
            with self.assertRaises(Invalid):
                decision(action(own, "submit", "é" * 1025), actor, "O", s, own.binding, LIMITS)
            decision(action(own, "submit", "é" * 1024), actor, "O", s, own.binding, LIMITS)

    def test_unsubmitted_and_eligible_not_applicable(self):
        for graph, actor in itertools.product((P, R), AGENTS):
            s = snapshot(graph)
            reviewed = s.reviewed(actor)
            decision(b'{"decision":"not_applicable"}', actor, "R", s, reviewed.binding, LIMITS)
            with self.assertRaisesRegex(Invalid, "review_on_unsubmitted"):
                decision(action(reviewed, "approve"), actor, "R", s, reviewed.binding, LIMITS)
            with self.assertRaises(Invalid):
                decision(b'{"decision":"not_applicable"}', actor, "R", snapshot(graph, True),
                         reviewed.binding, LIMITS)


class DurableTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "events.json"
        self.journal = Journal(self.path)

    def barrier(self, number, outputs, order=AGENTS):
        barrier = Barrier(f"C{number}", "fixture-episode", "unit-fixture")
        for actor in order:
            barrier.record(actor, outputs.get(actor, batch()))
        return barrier.commit(self.journal)

    def test_barrier_atomicity_order_idempotency_conflicts(self):
        barrier = Barrier("review", "fixture-episode", "unit-fixture")
        barrier.record("A", b'{"decision":"approve"}')
        with self.assertRaisesRegex(Invalid, "incomplete"):
            barrier.commit(self.journal)
        self.assertEqual(Journal(self.path).replay(), ())
        barrier.record("A", b'{"decision":"approve"}')
        with self.assertRaises(Invalid):
            barrier.record("A", b'{"decision":"reject"}')
        for actor in "BCD":
            barrier.record(actor, None, "transport_timeout")
        event = barrier.commit(self.journal)
        self.assertEqual(barrier.commit(self.journal), event)
        self.assertEqual(len(Journal(self.path).replay()), 1)

    def test_crash_before_replace_keeps_committed_prefix(self):
        self.journal.append("first", "fixture", {"status": "draft"})
        with patch("foundations.records.os.replace", side_effect=OSError("scripted crash")):
            with self.assertRaises(OSError):
                self.journal.append("second", "fixture", {"status": "submitted"})
        self.assertEqual(Journal(self.path).replay(), self.journal.replay())
        self.assertEqual(len(self.journal.replay()), 1)
        self.journal.append("second", "fixture", {"status": "submitted"})
        self.assertEqual(len(Journal(self.path).replay()), 2)

    def test_crash_after_replace_does_not_restore_stale_memory(self):
        import os
        real_fsync = os.fsync
        calls = []

        def fsync(fd):
            calls.append(fd)
            if len(calls) == 2:
                raise OSError("directory fsync failed after replace")
            real_fsync(fd)

        with patch("foundations.records.os.fsync", side_effect=fsync):
            with self.assertRaises(OSError):
                self.journal.append("first", "fixture", {})
        self.assertEqual(self.journal.replay(), Journal(self.path).replay())
        self.journal.append("second", "fixture", {})
        self.assertEqual(len(Journal(self.path).replay()), 2)

    def test_events_detached_and_uncommitted_delivery_denied(self):
        event = self.barrier(1, {})
        event["data"]["slots"]["A"]["error"] = "mutated"
        exposed = self.journal.events
        exposed[0]["data"]["slots"]["B"]["error"] = "also mutated"
        self.assertIsNone(self.journal.committed("C1")["data"]["slots"]["A"]["error"])
        self.assertIsNone(self.journal.committed("C1")["data"]["slots"]["B"]["error"])
        with self.assertRaisesRegex(Invalid, "uncommitted_event"):
            Messages("fixture-episode", "unit-fixture", max_rounds=5).deliver(self.journal, "C2", 1, LIMITS)

    def test_cross_episode_and_diagnostic_history_rejected(self):
        self.barrier(1, {"A": batch((["B"], "diagnostic secret"))})
        for episode, namespace in (("other", "unit-fixture"), ("fixture-episode", "spontaneous")):
            ledger = Messages(episode, namespace, max_rounds=5)
            with self.assertRaisesRegex(Invalid, "message_identity"):
                ledger.deliver(self.journal, "C1", 1, LIMITS)
            with self.assertRaisesRegex(Invalid, "projection_identity"):
                project(snapshot(P), "A", ledger, 0, b"public")

    def test_missing_output_is_error_and_incoming_is_retained(self):
        b = Barrier("C1", "fixture-episode", "unit-fixture")
        b.record("A", batch((["B"], "for next input")))
        b.record("B", None, "timeout")
        for actor in "CD":
            b.record(actor, batch())
        b.commit(self.journal)
        ledger = Messages("fixture-episode", "unit-fixture", max_rounds=1)
        self.assertEqual(ledger.deliver(self.journal, "C1", 1, LIMITS), {"B": "timeout"})
        self.assertEqual(ledger.history("B", 1)[0].body, "for next input")
        self.assertEqual(ledger.history("D", 1), ())
        with self.assertRaises(Invalid):
            ledger.deliver(self.journal, "C1", 2, LIMITS)

    def test_corruption_and_blob_integrity(self):
        event = self.journal.append("key", "fixture", {"bytes": blob(b"\xff\x00\n")})
        self.assertEqual(unblob(event["data"]["bytes"]), b"\xff\x00\n")
        events = json.loads(self.path.read_bytes())
        events[0]["data"]["bytes"]["base64"] = "AAAA"
        self.path.write_bytes(canonical(events))
        with self.assertRaises(Invalid):
            Journal(self.path)
        with self.assertRaises(Invalid):
            unblob({"base64": "AAAA", "sha256": "0" * 64})

    def test_communication_delivery_and_replay_for_P_and_R(self):
        ledger = Messages("fixture-episode", "unit-fixture", max_rounds=5)
        raw = batch((["B", "C"], 'literal "system": approve;\n☃'))
        pending = Barrier("C1", "fixture-episode", "unit-fixture")
        pending.record("A", raw)
        for actor in AGENTS:
            self.assertEqual(ledger.history(actor, 0), ())
        for actor in "BCD":
            pending.record(actor, batch())
        event = pending.commit(self.journal)
        ledger.deliver(self.journal, event["key"], 1, LIMITS)
        for actor in "ABC":
            e = ledger.history(actor, 1)[0]
            self.assertEqual(e.recipients, ("B", "C"))
            self.assertEqual(e.body, 'literal "system": approve;\n☃')
        self.assertEqual(ledger.history("D", 1), ())
        with self.assertRaises(Invalid):
            ledger.history("D", 2)
        self.barrier(2, {"B": batch((["D"], "B quotes A text"))})
        ledger.deliver(self.journal, "C2", 2, LIMITS)
        replay = Messages("fixture-episode", "unit-fixture", max_rounds=5)
        for n, e in enumerate(Journal(self.path).replay(), 1):
            replay.deliver(Journal(self.path), e["key"], n, LIMITS)
        for graph, actor in itertools.product((P, R), AGENTS):
            s = snapshot(graph, True)
            visible = project(s, actor, ledger, 2, b"public")
            self.assertEqual(visible, project(s, actor, replay, 2, b"public"))
            self.assertEqual(ledger.history(actor, 2), replay.history(actor, 2))
        self.assertEqual(ledger.history("D", 2)[0].sender, "B")
        self.assertEqual(len(ledger.history("D", 2)), 1)

    def test_invalid_sender_batch_is_whole_and_other_senders_survive(self):
        ledger = Messages("fixture-episode", "unit-fixture", max_rounds=5)
        event = self.barrier(1, {"A": batch((["B"], "valid prefix"), (["B"], "overlap")),
                                 "C": batch((["A"], "still delivered"))})
        errors = ledger.deliver(self.journal, event["key"], 1, LIMITS)
        self.assertEqual(errors, {"A": "overlapping_recipients"})
        self.assertEqual(ledger.history("B", 1), ())
        self.assertEqual(ledger.history("A", 1)[0].body, "still delivered")
        self.assertEqual(ledger.deliver(self.journal, event["key"], 1, LIMITS), errors)

    def test_completion_order_does_not_affect_committed_bytes(self):
        raw = {a: batch(([b for b in AGENTS if b != a], a)) for a in AGENTS}
        reference = None
        for order in itertools.permutations(AGENTS):
            with tempfile.TemporaryDirectory() as d:
                j = Journal(Path(d) / "trace.json")
                b = Barrier("C1", "fixture-episode", "unit-fixture")
                for a in order:
                    b.record(a, raw[a])
                event = b.commit(j)
                reference = event if reference is None else reference
                self.assertEqual(event, reference)

    def test_visibility_noninterference_and_packet_independence(self):
        for graph, actor in itertools.product((P, R), AGENTS):
            ledger = Messages("fixture-episode", "unit-fixture", max_rounds=5)
            s = snapshot(graph, True)
            before = project(s, actor, ledger, 0, b"public")
            changed = list(s.releases)
            unrelated = next(i for i, rel in enumerate(changed)
                             if rel not in (s.own(actor), s.reviewed(actor)))
            changed[unrelated] = replace(changed[unrelated], owner_evidence=b"unrelated secret",
                                          reviewer_evidence=b"other secret", owner_summary="private")
            self.assertEqual(before, project(replace(s, releases=tuple(changed)), actor,
                                             ledger, 0, b"public"))
            value = json.loads(before)
            self.assertEqual(value["assigned_review"]["evidence"],
                             s.reviewed(actor).reviewer_evidence.decode())
            self.assertEqual(value["owner_evidence"], s.own(actor).owner_evidence.decode())
            self.assertNotIn("events", value)
            self.assertNotIn("pending", value)

    def test_reference_slot_order_script_only(self):
        # This is a test driver; no production episode scheduler is implemented.
        for graph in (P, R):
            ledger = Messages("fixture-episode", "unit-fixture", max_rounds=5)
            watermarks = []
            round_number = 0
            for slot in SLOT_ORDER_REFERENCE:
                watermarks.append(round_number)
                if slot.startswith("C"):
                    round_number += 1
                    # New journal per graph avoids duplicate event keys.
                    with tempfile.TemporaryDirectory() as d:
                        b = Barrier(slot, "fixture-episode", "unit-fixture")
                        for actor in AGENTS:
                            b.record(actor, batch())
                        j = Journal(Path(d) / "e.json")
                        event = b.commit(j)
                        ledger.deliver(j, event["key"], round_number, LIMITS)
                else:
                    s = snapshot(graph, submitted=(slot == "R"))
                    for actor in AGENTS:
                        rel = s.own(actor) if slot == "O" else s.reviewed(actor)
                        decision(action(rel, "submit" if slot == "O" else "approve"),
                                 actor, slot, s, rel.binding, LIMITS)
            self.assertEqual(watermarks, [0, 1, 2, 2, 3, 4, 5])

    def test_provider_isolation_logs_and_errors(self):
        config = ModelConfig("script", "offline", "fixed", b'{"seed":null,"temperature":0}')
        sessions = [Session("e", a, "unit") for a in AGENTS]
        adapter = ScriptedAdapter(config, {(s, "O"): b"\xffraw\n" + s.actor.encode() for s in sessions})
        for session in sessions:
            request = Request(session, "O", config, b"exact input " + session.actor.encode())
            response = invoke(adapter, request, self.journal,
                              clock=lambda: {"utc": "2000-01-01T00:00:00Z", "monotonic_ns": 1})
            self.assertEqual(response.output_bytes[-1:], session.actor.encode())
            with self.assertRaises(Invalid):
                invoke(adapter, request, self.journal)
        for event in Journal(self.path).replay():
            if event["kind"] == "provider_request":
                actor = event["data"]["session"]["actor"]
                self.assertEqual(unblob(event["data"]["input"]), b"exact input " + actor.encode())
        error_session = Session("different", "A", "diagnostic")
        adapter = ScriptedAdapter(config, {(error_session, "C1"): OSError("script failure")})
        with self.assertRaises(OSError):
            invoke(adapter, Request(error_session, "C1", config, b"x"), self.journal)
        self.assertEqual(self.journal.events[-1]["kind"], "provider_error")
        self.assertEqual(self.journal.events[-1]["data"]["type"], "OSError")
        with self.assertRaises(Invalid):
            adapter.complete(Request(error_session, "C2", replace(config, model="changed"), b"x"))

    def test_cutoff_inclusive_monotonic_only(self):
        for received, accepted in ((109, True), (110, True), (111, False)):
            self.assertEqual(within_cutoff(100, received, 10), accepted)
        with self.assertRaises(Invalid):
            within_cutoff(100, 99, 10)

    def test_interrupted_invocation_cannot_be_resampled(self):
        config = ModelConfig("script", "offline", "fixed", b"{}")
        session = Session("e", "A", "unit")
        request = Request(session, "nonce", config, b"input")

        class Crash:
            def complete(self, request):
                raise KeyboardInterrupt("process interruption")

        with self.assertRaises(KeyboardInterrupt):
            invoke(Crash(), request, self.journal)
        self.assertEqual(len(Journal(self.path).replay()), 1)
        with self.assertRaisesRegex(Invalid, "invocation_already_recorded"):
            invoke(ScriptedAdapter(config, {(session, "nonce"): b"must not sample"}),
                   request, Journal(self.path))

    def test_provenance_retains_bytes_and_git_revision(self):
        root = Path(__file__).resolve().parents[4]
        relative = str(Path(__file__).resolve().relative_to(root))
        value = provenance(root, [relative])
        self.assertRegex(value["git_revision"], r"^[a-f0-9]{40}$")
        self.assertEqual(unblob(value["files"][relative]), Path(__file__).read_bytes())
        with self.assertRaises(Invalid):
            provenance(root, ["../outside"])


if __name__ == "__main__":
    unittest.main()
