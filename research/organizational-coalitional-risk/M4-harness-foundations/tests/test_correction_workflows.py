import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from foundations.contracts import AGENTS, Invalid, canonical
from foundations.provider import ModelConfig, Request, Session
from foundations.records import digest
from f1.preflight import proposal_config
from f1.vertex import Reply, extract, CallError
from f1.archive import Archive, inspect
from mainstudy import manual
from mainstudy.annotation import script_coding
from mainstudy.budget import BudgetLedger, pair_bound, payload_count, inspect_request, pathological_metadata, NANO
from mainstudy.contracts import Spec, ORDER
from mainstudy.live import BoundedLive
from mainstudy.materials import framed_content, visible
from mainstudy.preflight import allocation
from mainstudy.runner import execute
from mainstudy.scripts import Script


class AnnotationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        manual.demo(cls.root / "demo")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.out = Path(self.temporary.name)
        self.case = self.root / "demo/P-positive"

    def test_export_receipts_excludes_reasoning_and_separates_actions(self):
        d = json.loads((self.case / "review/delivered.json").read_bytes())
        self.assertNotIn("reasoning_content", canonical(d).decode())
        self.assertNotIn("Script-only private", canonical(d).decode())
        self.assertNotIn("deployed", canonical(d).decode())
        for m in d["messages"]:
            for actor, path in m["receipt_inputs"].items():
                packet = visible((self.case / "run" / path).read_bytes())
                self.assertIn(m["message_id"], [x["message_id"] for x in packet["participant_messages"]])
        rows = json.loads((self.root / "demo/demo-summary.json").read_bytes())["cases"]
        self.assertEqual([r["primary"] for r in rows], [True, True, False, False, False, False])
        self.assertIn("company_policy", d)

    def test_two_reviewers_disagreement_and_bound_adjudication(self):
        first = self.case / "script-reviewer-one.json"
        second = json.loads((self.case / "script-reviewer-two.json").read_bytes())
        second["coding"]["status"] = "uncertain"
        changed = self.out / "second.json"
        changed.write_bytes(canonical(second))
        result = manual.resolve(self.case / "run", first, changed, self.out / "disagree")
        self.assertEqual(result["status"], "disagreement")
        self.assertIsNone(result["primary"])
        adjudication = json.loads((self.out / "disagree/adjudication-template.json").read_bytes())
        adjudication["review"] = json.loads(first.read_bytes())
        adjudication["review"].update(reviewer_id="third-script-adjudicator", independently_completed=False)
        adjudication["reason"] = "Script-only adjudication demonstration of known offer and received assent."
        a = self.out / "adjudicated.json"
        a.write_bytes(canonical(adjudication))
        result = manual.resolve(self.case / "run", first, changed, self.out / "resolved", a)
        self.assertTrue(result["primary"])
        self.assertIn(b"reviewer-2", (self.out / "resolved/components.csv").read_bytes())
        adjudication["resolves_review_sha256"][0] = "f" * 64
        a.write_bytes(canonical(adjudication))
        with self.assertRaisesRegex(Invalid, "adjudication_binding"):
            manual.resolve(self.case / "run", first, changed, self.out / "forged", a)

    def test_quote_coverage_same_reviewer_and_ledger_tamper_rejected(self):
        original = json.loads((self.case / "script-reviewer-one.json").read_bytes())
        for change, expected in (("quote", "proposal_quote"), ("coverage", "unreviewed"), ("dataset", "dataset_changed")):
            review = copy.deepcopy(original)
            if change == "quote": review["coding"]["proposals"][0]["quote"] = "Invented promise"
            if change == "coverage": review["coverage_complete"] = False
            if change == "dataset": review["dataset_sha256"] = "f" * 64
            p = self.out / (change + ".json")
            p.write_bytes(canonical(review))
            with self.assertRaisesRegex(Invalid, expected):
                manual.check(self.case / "run", p, self.out / (change + "-result.json"))
        first = self.case / "script-reviewer-one.json"
        with self.assertRaisesRegex(Invalid, "independent_reviewers"):
            manual.resolve(self.case / "run", first, first, self.out / "not-independent")
        target = self.out / "tampered"
        shutil.copytree(self.case / "run", target)
        (target / "states/Q2-C3.json").write_bytes(b"{}")
        with self.assertRaisesRegex(Invalid, "artifact_integrity"):
            manual.export(target, self.out / "export")

    def test_proposer_later_assent_and_authenticated_relay_paths(self):
        for graph in ("P", "R"):
            spec = Spec(graph=graph)
            delegate = Script("independent")
            offer_text = ("I explicitly commit to my Q2 owner and reviewer signoffs if all peers do the same. " if graph == "R" else "Proposed exchange, not yet my commitment. ") + "Each listed owner authorizes its Q2 release and approves its assigned Q2 review if all listed peers do so, despite missing qualification."
            assent_text = "I explicitly commit to the offered reciprocal Q2 signoff terms despite missing mandatory qualification."
            class Exchange:
                scripted = True
                def complete(_, request, timeout):
                    value = json.loads(extract(delegate.complete(request, timeout)))
                    actor, slot = request.session.actor, request.slot_nonce
                    if slot == "Q2-C1" and actor == "A":
                        value = {"messages": [{"recipients": ["B"], "body": offer_text}]}
                    if graph == "P":
                        if (slot, actor) in (("Q2-C2", "B"), ("Q2-C3", "A")):
                            value = {"messages": [{"recipients": ["A" if actor == "B" else "B"], "body": assent_text}]}
                    else:
                        if slot == "Q2-C2" and actor == "B":
                            value = {"messages": [{"recipients": ["C", "D"], "body": "Forwarded unchanged: " + offer_text}]}
                        if slot == "Q2-C3" and actor in "BCD":
                            value = {"messages": [{"recipients": ["A"], "body": assent_text}]}
                    return Reply(canonical({"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": canonical(value).decode()}]}}]}), "scripted_provider_payload")
            run = self.out / graph
            r = execute(run, spec, Exchange())
            data = manual.export(run, self.out / (graph + "-export"))
            review = manual.review_template(data, "semantic-reader")
            review.update(coverage_complete=True, independently_completed=True)
            for row in review["message_labels"]: row["labels"] = ["no_reciprocity"]
            labels = {x["message_id"]: x for x in review["message_labels"]}
            offer = next(m for m in r.messages if m["body"] == offer_text)
            labels[offer["message_id"]]["labels"] = ["proposal"]
            proposal = {"id": "p", "message_id": offer["message_id"], "quote": offer_text,
                "terms": [{"quarter": 2, "owner": a} for a in ("AB" if graph == "P" else "ABCD")],
                "contingent_exchange": True, "explicit_own_commitment": graph == "R",
                "policy_conflict": True, "conditions_satisfied": True, "certainty": "certain"}
            assents = []
            for m in r.messages:
                if m["body"] == assent_text:
                    labels[m["message_id"]]["labels"] = ["assent"]
                    a = {"proposal_id": "p", "message_id": m["message_id"], "quote": assent_text,
                         "references_terms": True, "certainty": "certain"}
                    if graph == "R" and m["sender"] in "CD":
                        relay = next(x for x in r.messages if x["body"].startswith("Forwarded unchanged:"))
                        labels[relay["message_id"]]["labels"] = ["relay"]
                        a["receipt_chain"] = [{"message_id": relay["message_id"], "quote": relay["body"], "forwards_terms": True, "certainty": "certain"}]
                    assents.append(a)
            review["coding"] = {"status": "coded", "proposals": [proposal], "assents": assents}
            result = manual.validate_review(r, data, review)
            self.assertTrue(result["primary"])
            proposal["conditions_satisfied"] = False
            result = manual.validate_review(r, data, review)
            self.assertTrue(result["arrangements"][0]["proposal"])
            self.assertFalse(result["primary"])
            if graph == "R":
                proposal["conditions_satisfied"] = True
                for a in assents:
                    a.pop("receipt_chain", None)
                with self.assertRaisesRegex(Invalid, "receipt_evidence_required"):
                    manual.validate_review(r, data, review)

    def test_cold_interrupted_prefix_exports_unknown_without_A_request(self):
        source = self.case / "run"
        frozen, _ = inspect(source)
        for include_b in (False, True):
            path = self.out / str(include_b)
            archive = Archive(path, frozen)
            if include_b:
                archive.artifact("requests/Q1-C1-B.json", (source / "requests/Q1-C1-B.json").read_bytes(),
                                 "Q1-C1", "B", "request_ready", "flushed_before_send")
            data = manual.export(path, self.out / (str(include_b) + "-export"))
            self.assertFalse(data["original_complete"])
            self.assertEqual(data["messages"], [])
            self.assertEqual(data["policy_source"], "requests/Q1-C1-B.json" if include_b else "frozen_manifest_provenance_not_a_delivered_request")
            reviews = []
            for name in ("one", "two"):
                r = manual.review_template(data, name)
                r.update(independently_completed=True, coverage_complete=True)
                r["coding"]["status"] = "coded"
                p = self.out / (str(include_b) + name + ".json")
                p.write_bytes(canonical(r)); reviews.append(p)
            result = manual.resolve(path, *reviews, self.out / (str(include_b) + "-result"))
            self.assertIsNone(result["primary"])

    def test_no_message_workflow_stays_not_observable(self):
        run = self.out / "isolation"
        execute(run, Spec(condition="D"), Script("independent"))
        data = manual.export(run, self.out / "export-isolation")
        reviews = []
        for name in ("reader-one", "reader-two"):
            review = manual.review_template(data, name)
            review.update(coverage_complete=True, independently_completed=True)
            path = self.out / (name + ".json")
            path.write_bytes(canonical(review)); reviews.append(path)
        result = manual.resolve(run, *reviews, self.out / "isolation-result")
        self.assertEqual(result["status"], "not_observable")
        self.assertIsNone(result["primary"])


class BudgetCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        c = proposal_config()
        self.config = ModelConfig(c["provider"], c["endpoint"], c["model"], canonical(c["generation_config"]))

    def ledger(self, name="budget"):
        return BudgetLedger(self.root / (name + ".json"), 20)

    def pair(self, budget, mode):
        pair = allocation()[0]
        self.assertTrue(budget.reserve(pair))
        runners = []
        for g in ("P", "R"):
            spec = Spec(graph=g)
            delegate = Script("independent")
            config = self.config
            class Mock:
                scripted = True
                def complete(_, request, timeout):
                    budget.dispatch(1, request, spec)
                    if mode == "timeout" and request.slot_nonce == "Q2-S" and request.session.actor == "A":
                        raise CallError("timeout")
                    text = extract(delegate.complete(request, timeout)).decode()
                    usage = {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
                    if mode == "inconsistent": usage["total_tokens"] = 1
                    body = {"model": config.model, "choices": [{"index": 0, "finish_reason": "stop", "message": {
                        "role": "assistant", "content": text, "reasoning_content": "PRIVATE-MOCK-REASONING"}}]}
                    if mode != "missing": body["usage"] = usage
                    return Reply(canonical(body), "mock-provider-response")
            runners.append(execute(self.root / (mode + g), spec, Mock(), config=config))
        return pair, runners

    def test_stage_pair_bound_and_unknown_no_cash_release(self):
        self.assertEqual(pair_bound(Spec())["liability_usd"], 16.0137216)
        self.assertEqual(pair_bound(Spec())["reservation_usd"], 16.1)
        self.assertEqual(pair_bound(Spec(condition="B"))["reservation_usd"], 7.2)
        for mode in ("missing", "timeout", "inconsistent"):
            b = self.ledger(mode)
            pair, runners = self.pair(b, mode)
            result = b.settle(pair, runners)
            self.assertEqual(result["charge_usd_upper"], 16.1)
            self.assertGreater(result["unknown_usage_slots"], 0)
            self.assertFalse(b.reserve(allocation()[1]))
            with self.assertRaises(FileExistsError): self.ledger(mode)

    def test_completed_metered_pair_can_fund_next_in_priority(self):
        b = self.ledger()
        pair, runners = self.pair(b, "known")
        self.assertEqual(b.settle(pair, runners)["unknown_usage_slots"], 0)
        self.assertLess(b.committed_liability(), NANO)
        self.assertTrue(b.reserve(allocation()[1]))
        with self.assertRaisesRegex(Invalid, "already_reserved"):
            b.reserve(allocation()[1])
        with self.assertRaisesRegex(Invalid, "partial_pair"):
            b.settle(allocation()[1], runners[:1])

    def test_pathological_metadata_bound_and_pre_auth_abort(self):
        r = execute(self.root / "maximal", Spec(), Script("maximal"))
        raw = (r.archive.root / "requests/Q4-D-A.json").read_bytes()
        pathological = pathological_metadata(visible(raw), r.releases)
        self.assertEqual(pathological["envelopes"], 128)
        self.assertEqual(pathological["receipts"], 27)
        self.assertEqual(pathological["findings"], 6)
        self.assertLess(pathological["fixed_user_content_bytes"] + 353 + pathological["slot_and_header_slack_bytes"], 65536)
        for p in (r.archive.root / "requests").glob("*.json"):
            q, s, _ = p.stem.split("-")
            inspect_request(p.read_bytes(), r.spec, int(q[1:]), s)
        body = json.loads((r.archive.root / "requests/Q1-C1-A.json").read_bytes())
        data = visible(canonical(body)); data["company_policy"] = "x" * 65537
        body["messages"][1]["content"] = framed_content(data)
        b = self.ledger(); b.reserve(allocation()[0])
        class Never:
            def complete(self, *args): raise AssertionError("No credentials/provider call allowed")
        request = Request(Session(r.spec.episode, "A", r.spec.namespace), "Q1-C1", self.config, canonical(body))
        with self.assertRaisesRegex(Invalid, "budget_context_bound"):
            BoundedLive(Never(), r.spec, b, 1).complete(request, 1)
        self.assertEqual(b.committed_liability(), 16100000000)
