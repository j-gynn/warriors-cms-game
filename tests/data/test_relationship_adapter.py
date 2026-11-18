import unittest

from simulation.social.relationship_adapter import get_derived_interaction_affinity


class TestDerivedAffinity(unittest.TestCase):
    def test_derived_interaction_affinity(self):
        # confirm that the maximum value returns 100
        self.assertEqual(get_derived_interaction_affinity(100, 100), 100)
        self.assertEqual(get_derived_interaction_affinity(-100, -100), 100)

        # confirm that a neutral value returns 0
        self.assertEqual(get_derived_interaction_affinity(0, 0), 0)


if __name__ == "__main__":
    unittest.main()
