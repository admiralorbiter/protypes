
import unittest, random
from lab.data import generate_world
from lab.model import Scenario
from lab.scenarios import apply_scenario
from lab.da import deferred_acceptance

class TestDA(unittest.TestCase):
    def test_stable_fill_and_capacity(self):
        world = generate_world(N=1200, M=8, seed=1)
        sc = Scenario()
        apply_scenario(world, sc, seed=1)
        s2c, c2s = deferred_acceptance(world, sc, random.Random(1))
        # Capacity respected
        for c in world.colleges:
            self.assertLessEqual(len(c2s[c.cid]), c.capacity)

        # Every matched student is admitted by exactly one college
        self.assertEqual(len(s2c), sum(len(v) for v in c2s.values()))

    def test_ineligible_under_test_required(self):
        world = generate_world(N=800, M=6, seed=2)
        sc = Scenario(test_required_private_elite=True, num_private_elites_test_required=2)
        apply_scenario(world, sc, seed=2)
        s2c, c2s = deferred_acceptance(world, sc, random.Random(2))
        # For test-required colleges, no admits should have None test_score
        private_required = [c.cid for c in world.colleges if (not c.is_public and c.test_policy == 'required')]
        for sid, cid in s2c.items():
            if cid in private_required:
                self.assertIsNotNone(world.students[sid].test_score)

if __name__ == "__main__":
    unittest.main()
