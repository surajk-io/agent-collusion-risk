import json
from pathlib import Path
import tempfile
import unittest
from dataclasses import replace

from foundations.contracts import AGENTS, Invalid, canonical
from mainstudy.contracts import Spec, ORDER
from mainstudy.fixtures import inventory, verify
from mainstudy.materials import visible
from mainstudy.runner import execute, mechanically_valid, audit_uniform
from mainstudy.scripts import Script


class MainStudyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.index = 0

    def run_episode(self, spec=Spec(), trace="positive", adapter=None):
        self.index += 1
        path = self.root / str(self.index)
        return execute(path, spec, adapter or Script(trace), trace), path

    def test_evidence_ground_truth_and_exact_qualification(self):
        for block in (1, 2):
            cases = inventory(block)
            for q in range(1, 5):
                self.assertEqual(sum(cases[q, a].vulnerable for a in AGENTS), 0 if q == 1 else 2)
                for a in AGENTS:
                    r = cases[q, a]
                    self.assertTrue(verify(r))
                    self.assertEqual(r.qualified, q == 1)
                    self.assertTrue(all(x["pass"] for x in r.packet()["evidence"]["limited_checks"]))
                    self.assertEqual(r.packet()["evidence"]["mandatory_verification"]["record"] is not None, q == 1)
                    self.assertNotIn("dependency.py", canonical(r.packet()).decode())

    def test_four_quarter_atomic_signatures_and_policy_bypass(self):
        for graph in ("P", "R"):
            runner, path = self.run_episode(Spec(graph=graph))
            self.assertEqual(len(runner.quarters), 4)
            self.assertEqual(len(list((path / "requests").glob("*.json"))), 112)
            for q in range(1, 5):
                s = json.loads((path / f"states/Q{q}-S.json").read_bytes())["state"]
                self.assertTrue(all(x["owner_signature"] is None for x in s.values()))
                self.assertTrue(all(x["deployed"] for x in runner.quarters[q - 1]["state"].values()))
                for a in AGENTS:
                    r = runner.releases[q, a]
                    item = runner.quarters[q - 1]["state"][a]
                    self.assertTrue(mechanically_valid(runner.spec, r, item))
                    item["reviewer_signature"]["signer"] = "invalid"
                    self.assertFalse(mechanically_valid(runner.spec, r, item))
            with self.assertRaisesRegex(Invalid, "already_started"):
                runner.run()

    def test_whole_slot_and_individual_field_fallback(self):
        for trace in ("invalid", "timeout", "stale", "hold", "withhold"):
            runner, path = self.run_episode(trace=trace)
            s = json.loads((path / "states/Q2-D.json").read_bytes())
            if trace in ("invalid", "timeout"):
                self.assertEqual(s["state"]["A"]["owner_decision"], "withhold_timeout")
                self.assertEqual(s["state"]["B"]["review_decision"], "reject_timeout")
                self.assertEqual(s["state"]["A"]["request"], "hold_timeout")
            elif trace == "stale":
                self.assertEqual(s["state"]["A"]["owner_decision"], "authorize")
                self.assertEqual(s["state"]["B"]["review_decision"], "reject_timeout")
            else:
                self.assertFalse(any(x["deployed"] for q in runner.quarters for x in q["board"]))

    def test_controls_serialized_privacy_and_role_memory(self):
        for condition in AGENTS:
            runner, path = self.run_episode(Spec(condition=condition))
            for q in range(1, 5):
                for a in AGENTS:
                    for stage in ORDER:
                        raw = (path / f"requests/Q{q}-{stage}-{a}.json").read_bytes()
                        v = visible(raw)
                        for forbidden in ("oracle_json", "source_json", "vulnerable", "audit_uniforms", "Script-only private", "finding_id"):
                            # A sampled finding legitimately appears later; seed here has none for early slots.
                            if forbidden != "finding_id":
                                self.assertNotIn(forbidden, raw.decode())
                        self.assertTrue(all(m["sender"] == a or a in m["recipients"] for m in v["participant_messages"]))
                        if condition != "A":
                            self.assertEqual(v["participant_messages"], [])
                        if condition in ("C", "D"):
                            self.assertIsNone(v["public_board_history"])
                        if condition == "D":
                            self.assertIsNone(v["organization_chart"])
                            self.assertEqual(set(v["role_record"]), {"owner", "owned_release_id"})
                            def identities(value, key=None):
                                if isinstance(value, dict):
                                    return [x for k, item in value.items() for x in identities(item, k)]
                                if isinstance(value, list):
                                    return [x for item in value for x in identities(item)]
                                return [value] if isinstance(value, str) and key not in ("phase", "stage") else []
                            for other in set(AGENTS) - {a}:
                                self.assertNotIn(other, identities(v))
                        if stage in ("C1", "C2", "S"):
                            self.assertIsNone(v["assigned_review"])
                        self.assertEqual(len(v["retained_memory"]), q - 1)

    def test_audit_coupling_private_findings_and_positive_productivity(self):
        # Find a seed with a procedural audit before Q4, deterministically, no behavioral selection.
        seed = next(s for s in range(1000) if audit_uniform(Spec(seed=s), 2, "A") < .05)
        for condition in ("A", "D"):
            runner, path = self.run_episode(Spec(condition=condition, seed=seed))
            finding = next(f for f in runner.quarters[1]["findings"] if f["owner"] == "A")
            for a in AGENTS:
                retained = runner.memory[a][1]["findings"]
                self.assertEqual(any(x["finding_id"] == finding["finding_id"] for x in retained), a in ("A", "B"))
                if condition == "D":
                    self.assertTrue(all("owner" not in x and "reviewer" not in x for x in retained))
            self.assertEqual(runner.quarters[0]["findings"], [])
        for graph in ("P", "R"):
            runner, _ = self.run_episode(Spec(graph=graph, seed=seed), "cooperation")
            self.assertTrue(all(x["deployed"] for x in runner.quarters[0]["board"]))
            self.assertFalse(any(x["deployed"] for q in runner.quarters[1:] for x in q["board"]))
            self.assertFalse(any(q["findings"] for q in runner.quarters))

    def test_forged_evidence_and_reused_dependency_fingerprints_rejected(self):
        cases = inventory(1)
        self.assertEqual(len({r.packet()["evidence"]["dependency_artifact_sha256"] for r in cases.values()}), 16)
        release = cases[2, "A"]
        for field in ("status", "limited", "gate"):
            e = json.loads(release.evidence_json)
            if field == "status":
                e["mandatory_verification"]["status"] = "complete_accepted"
            elif field == "limited":
                e["limited_checks"] = [{"check": "invented", "pass": True}]
            changed = replace(release, evidence_json=canonical(e), ordinary_gate=field != "gate")
            with self.assertRaisesRegex(Invalid, "evidence_integrity"):
                verify(changed)


if __name__ == "__main__":
    unittest.main()
