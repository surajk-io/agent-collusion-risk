import json
from pathlib import Path
import tempfile
import unittest
from dataclasses import replace

from foundations.contracts import AGENTS, canonical, Invalid
from mainstudy.fixtures import inventory, verify
from mainstudy.contracts import Spec, ORDER
from mainstudy.materials import visible
from mainstudy.runner import execute
from mainstudy.scripts import Script


class CorrectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_actual_requests_no_research_cues_and_policy_matched(self):
        policies = set()
        for graph in ("P", "R"):
            for condition in AGENTS:
                r = execute(self.root / f"{graph}-{condition}", Spec(graph=graph, condition=condition), Script("independent"))
                for path in (r.archive.root / "requests").glob("*.json"):
                    raw = path.read_bytes().decode().lower()
                    for marker in ("fictional", "simulated", "research fixture", "research template", "study-defined", "not modeled"):
                        self.assertNotIn(marker, raw)
                    policies.add(visible(path.read_bytes())["company_policy"])
                self.assertIn("research_provenance", json.loads(r.releases[1, "A"].oracle_json))
        self.assertEqual(len(policies), 1)

    def test_S_instructions_delivery_and_no_signature(self):
        for condition in AGENTS:
            spec = Spec(condition=condition)
            r = execute(self.root / condition, spec, Script("independent"))
            for actor in AGENTS:
                s = visible((r.archive.root / f"requests/Q2-S-{actor}.json").read_bytes())
                instruction = s["slot"]["instruction"]
                if condition == "A":
                    self.assertIn("assigned reviewer " + spec.reviewers[actor], instruction)
                    self.assertIn("available from C3", instruction)
                else:
                    self.assertIn("not delivered to any reviewer", instruction)
                state = json.loads((r.archive.root / "states/Q2-S.json").read_bytes())["state"]
                self.assertTrue(all(x["owner_signature"] is None for x in state.values()))
                review = visible((r.archive.root / f"requests/Q2-C3-{actor}.json").read_bytes())["assigned_review"]
                self.assertEqual("owner_authored_summary" in review, condition == "A")
            self.assertEqual(any(m["stage"] == "S" for m in r.messages), condition == "A")

    def test_real_before_after_regression_and_no_residual_trigger_leak(self):
        for block in (1, 2):
            for r in inventory(block).values():
                self.assertTrue(verify(r))
                p = r.packet()["evidence"]["patch_evidence"]
                self.assertFalse(p["before"]["pass"])
                self.assertEqual(p["before"]["observed"]["exception_type"], "KeyError")
                self.assertTrue(p["after"]["pass"])
                self.assertEqual(p["after"]["candidate_hash"], r.candidate_hash)
                self.assertIn("-    return dependency.", p["unified_diff"])
                self.assertIn("+    if not isinstance", p["unified_diff"])
                self.assertNotIn("bulk:monthly", canonical(r.packet()).decode())
                self.assertNotIn('if resume else', canonical(r.packet()).decode())
                forged = json.loads(r.evidence_json)
                forged["patch_evidence"]["before"]["pass"] = True
                with self.assertRaisesRegex(Invalid, "evidence_integrity"):
                    verify(replace(r, evidence_json=canonical(forged)))


if __name__ == "__main__":
    unittest.main()
