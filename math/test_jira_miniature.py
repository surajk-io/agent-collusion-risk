"""Unit tests for the illustrative Colosseum/Jira scoring extraction.

Run from repository root:
    python -m unittest discover -s math -p 'test_jira_miniature.py'
"""
import unittest
from jira_miniature import evaluate, optima, enumerate_profiles, profitable_deviations


class MiniatureTests(unittest.TestCase):
    def test_profiles(self):
        self.assertEqual(len(enumerate_profiles()), 64)

    def test_optimum(self):
        self.assertEqual(optima(), [(("X", "Z", "Y"), 51., (21., 20., 10.))])

    def test_strict_two_agent_opportunity(self):
        candidates = profitable_deviations(("X", "Z", "Y"))
        self.assertIn((("X", "Y", "X"), (1., 1.5), 5.), candidates["BC"])

    def test_unilateral_opportunity_also_exists(self):
        candidates = profitable_deviations(("X", "Z", "Y"))
        self.assertIn((("X", "Z", "X"), (1.5,), 6.), candidates["C"])

    def test_org_welfare_additive(self):
        for welfare, utilities in enumerate_profiles().values():
            self.assertAlmostEqual(welfare, sum(utilities))

    def test_duplicate_penalty_split(self):
        welfare, utilities = evaluate(("X", "X", "Y"))
        self.assertEqual(utilities, (13.5, 8.5, 10.))
        self.assertEqual(welfare, 32.)


if __name__ == "__main__":
    unittest.main()
