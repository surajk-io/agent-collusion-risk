import unittest
from itertools import product

from finite_game import evaluate, opportunities, all_coalitions, BASELINE


class TestToyGame(unittest.TestCase):
    def test_only_one_harmful_profile(self):
        harmful = [a for a in product((0, 1), repeat=3) if evaluate(a)[1] < 0]
        self.assertEqual(harmful, [(1, 1, 0)])

    def test_reference(self):
        self.assertEqual(evaluate(BASELINE), ((0, 0, 0), 0))

    def test_unilateral_deviations_cannot_harm(self):
        self.assertTrue(all(not opportunities((i,)) for i in range(3)))

    def test_strict_coalitions(self):
        c = all_coalitions()
        self.assertEqual(c["AB"], [((1, 1, 0), (3, 2), 5)])
        self.assertEqual(c["AC"], [])
        self.assertEqual(c["BC"], [])
        self.assertEqual(c["ABC"], [])

    def test_weak_superset_double_count(self):
        self.assertEqual(all_coalitions(strict=False)["ABC"], [((1, 1, 0), (3, 2, 0), 5)])


if __name__ == "__main__":
    unittest.main()
