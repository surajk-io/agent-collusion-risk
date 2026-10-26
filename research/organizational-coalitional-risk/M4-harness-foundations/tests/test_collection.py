"""Offline provider-shaped responses only: no credentials or network."""
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

from foundations.contracts import Invalid, canonical, strict_json
from foundations.provider import ModelConfig
from mainstudy.budget import BudgetLedger, NANO, slot_bound
from mainstudy.collection import run_one_pair, resume_proposal, invocation_lock, claims_directory
from mainstudy.live import LaunchApproval
from mainstudy.preflight import launch_proposal
from mainstudy.scripts import Script
from f1.vertex import Reply, extract


class MeteredScript:
    def __init__(self, mode="normal"):
        config = launch_proposal("offline-test")["provider_config"]
        self.config = ModelConfig(config["provider"], config["endpoint"], config["model"], canonical(config["generation_config"]))
        self.mode, self.calls, self.lock = mode, set(), threading.Lock()

    def complete(self, request, timeout):
        key = request.session.episode, request.slot_nonce, request.session.actor
        with self.lock:
            if key in self.calls:
                raise AssertionError("repeated model call")
            self.calls.add(key)
        raw = extract(Script("independent").complete(request, timeout)).decode()
        inp, out = 100, 200
        if self.mode == "expensive":
            from mainstudy.materials import visible
            from mainstudy.contracts import Spec
            d = visible(request.input_bytes)
            b = slot_bound(Spec(), d["quarter"], d["slot"]["phase"])
            inp, out = b["input_tokens"], b["output_tokens"]
        body = {"model": self.config.model, "choices": [{"index": 0, "finish_reason": "stop",
            "message": {"role": "assistant", "content": raw}}]}
        if self.mode != "unknown":
            body["usage"] = {"prompt_tokens": inp, "completion_tokens": out, "total_tokens": inp + out}
        return Reply(canonical(body), "openai_chat_completions")


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root, self.claims = self.base / "collection", self.base / "claims"
        a = launch_proposal("offline-only-no-real-approval")
        a.update(status="explicitly_authorized", researcher_approval_reference="OFFLINE_TEST_ONLY",
                 collection_root=str(self.root), stop_new_pairs_at="2099-01-01T00:00:00+00:00",
                 git_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip())
        self.approval = LaunchApproval(a)
        self.adapter = MeteredScript()

    def start(self):
        return run_one_pair(self.root, self.claims, self.approval, self.adapter)

    def authorization(self, receipt):
        a = resume_proposal()
        for k in ("execution_mode", "git_revision", "package_sha256", "collection_approval_sha256",
                  "collection_root", "ledger_head_sha256", "next_pair"):
            a["prior_ledger_head_sha256" if k == "ledger_head_sha256" else k] = receipt[k]
        a.update(status="explicitly_authorized", researcher_approval_reference="OFFLINE_RESUME_ONLY")
        return a

    def resume(self, auth):
        return run_one_pair(self.root, self.claims, self.approval, self.adapter, resume_authorization=auth)

    def test_first_pair_then_explicit_resume_stale_and_duplicate_prevention(self):
        first = self.start()
        self.assertEqual(len(self.adapter.calls), 224)
        self.assertEqual(first["status"], "paused_requires_explicit_resume")
        self.assertEqual(first["settlement"]["usage"]["actual_prompt_tokens"], 22400)
        self.assertEqual(first["settlement"]["usage"]["actual_completion_tokens"], 44800)
        self.assertTrue(all(x["integrity"] == "hash_chain_and_exact_replay_verified" for x in first["archives"]))
        with self.assertRaisesRegex(Invalid, "collection_output_exists"):
            self.start()
        auth = self.authorization(first)
        second = self.resume(auth)
        self.assertEqual(second["pair"], 2)
        self.assertEqual(len(self.adapter.calls), 448)
        self.assertIn("R", Path(second["archives"][0]["path"]).name)
        with self.assertRaisesRegex(Invalid, "stale"):
            self.resume(auth)
        self.assertEqual(len(self.adapter.calls), 448)

    def test_archive_corruption_blocks_before_any_call(self):
        receipt = self.start()
        request = next((Path(receipt["archives"][0]["path"]) / "requests").glob("*.json"))
        request.write_bytes(b"corrupt")
        with self.assertRaises(Invalid):
            self.resume(self.authorization(receipt))
        self.assertEqual(len(self.adapter.calls), 224)

    def test_approval_claims_root_and_orphan_claim_fail_closed(self):
        receipt = self.start(); auth = self.authorization(receipt)
        self.approval.record["max_pairs"] = 7
        with self.assertRaisesRegex(Invalid, "incompatible_collection"):
            self.resume(auth)
        self.approval.record["max_pairs"] = 8
        (self.claims / "pair-2.json").write_bytes(b"{}")
        with self.assertRaisesRegex(Invalid, "orphan_pair_claim"):
            self.resume(auth)
        self.assertEqual(len(self.adapter.calls), 224)
        with self.assertRaisesRegex(Invalid, "configuration"):
            run_one_pair(self.base / "replacement", self.base / "otherclaims", self.approval, self.adapter)

    def test_unknown_usage_retains_entire_pair_and_cannot_resume(self):
        self.adapter = MeteredScript("unknown")
        receipt = self.start()
        self.assertEqual(receipt["status"], "blocked_unresolved_usage")
        self.assertIsNone(receipt["settlement"]["usage"]["actual_prompt_tokens"])
        self.assertEqual(receipt["budget"]["unresolved_reserved_usd"], 16.1)
        self.assertFalse(receipt["budget"]["can_reserve_next_pair"])
        with self.assertRaisesRegex(Invalid, "partial_or_unresolved"):
            self.resume(self.authorization(receipt))
        self.assertEqual(len(self.adapter.calls), 224)

    def test_partial_pair_retains_reservation_never_repeats(self):
        from mainstudy import runner
        original = runner.Runner.commit
        def interrupt(instance, quarter, stage, results):
            if instance.spec.graph == "R" and quarter == 1 and stage == "C1":
                raise RuntimeError("offline simulated process interruption")
            return original(instance, quarter, stage, results)
        with patch.object(runner.Runner, "commit", interrupt):
            with self.assertRaisesRegex(RuntimeError, "interruption"):
                self.start()
        self.assertEqual(len(self.adapter.calls), 116)
        ledger = BudgetLedger(self.claims / "budget.json", 20, resume=True)
        self.assertEqual(ledger.committed_liability(), round(16.1 * NANO))
        with self.assertRaisesRegex(Invalid, "partial_or_unresolved"):
            self.resume(resume_proposal())
        self.assertEqual(len(self.adapter.calls), 116)

    def test_inconsistent_usage_projection_cannot_release_reservation(self):
        from f1 import runner as original_runner
        from f1.vertex import metadata
        def incorrect(reply):
            result = metadata(reply)
            result["usage"] = {"prompt_tokens": 1, "completion_tokens": 0, "total_tokens": 1}
            return result
        with patch.object(original_runner, "metadata", incorrect):
            with self.assertRaisesRegex(Invalid, "usage_metadata_raw_response_mismatch"):
                self.start()
        ledger = BudgetLedger(self.claims / "budget.json", 20, resume=True)
        self.assertEqual(ledger.committed_liability(), round(16.1 * NANO))
        self.assertFalse(any(e["kind"] == "pair_settlement" for e in ledger.journal.events))

    def test_missing_receipt_or_ledger_corruption_cannot_resume(self):
        receipt = self.start()
        (self.root / "pair-001-receipt.json").unlink()
        with self.assertRaises(FileNotFoundError):
            self.resume(self.authorization(receipt))
        ledger = self.claims / "budget.json"
        data = strict_json(ledger.read_bytes())
        data[-1]["data"]["pair"] = 7
        ledger.write_bytes(canonical(data))
        with self.assertRaisesRegex(Invalid, "journal_integrity"):
            self.resume(self.authorization(receipt))
        self.assertEqual(len(self.adapter.calls), 224)

    def test_known_usage_insufficient_for_whole_next_pair(self):
        self.adapter = MeteredScript("expensive")
        receipt = self.start()
        self.assertAlmostEqual(receipt["settlement"]["charge_usd_upper"], 16.0137216)
        self.assertFalse(receipt["budget"]["can_reserve_next_pair"])
        with self.assertRaisesRegex(Invalid, "insufficient_whole_pair_budget"):
            self.resume(self.authorization(receipt))
        self.assertEqual(len(self.adapter.calls), 224)
        ledger = BudgetLedger(self.claims / "budget.json", 20, resume=True)
        self.assertEqual(sum(e["kind"] == "pair_reservation" for e in ledger.journal.events), 1)

    def test_existing_output_does_not_claim_budget_and_invocation_lock(self):
        self.root.mkdir()
        with self.assertRaisesRegex(Invalid, "collection_output_exists"):
            self.start()
        self.assertFalse((self.claims / "budget.json.lock").exists())
        with invocation_lock(self.claims / "invocation.lock"):
            with self.assertRaisesRegex(Invalid, "invocation_busy"):
                with invocation_lock(self.claims / "invocation.lock"):
                    self.fail("concurrent writer")

    def test_shared_git_common_claims_directory(self):
        a = claims_directory(Path(__file__).resolve().parents[1], self.approval.record["git_revision"])
        common = subprocess.check_output(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], text=True).strip()
        self.assertEqual(a, Path(common) / "mainstudy-collections" / self.approval.record["git_revision"])


if __name__ == "__main__":
    unittest.main()
