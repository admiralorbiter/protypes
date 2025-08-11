import unittest, random
from cantstop.state import new_game
from cantstop.constants import COLUMN_HEIGHTS
from cantstop.engine import legal_pairings, apply_pairing, compute_turn_gain, can_play_sum
from cantstop.odds import bust_prob

class TestEngine(unittest.TestCase):
    def test_column_heights(self):
        self.assertEqual(COLUMN_HEIGHTS[2], 3)
        self.assertEqual(COLUMN_HEIGHTS[7], 13)
        self.assertEqual(COLUMN_HEIGHTS[12], 3)

    def test_start_of_turn_no_bust(self):
        s = new_game(2)
        # With all columns open and 3 free runners, bust prob should be 0
        self.assertEqual(bust_prob(s), 0.0)

    def test_legal_pairings_with_active_runner(self):
        s = new_game(2)
        # Simulate having started a runner on 7
        s.players[s.current].permanent_pos[7] = 0
        s.turn.active_runners[7] = 1
        roll = (1,2,3,6)  # possible sums: (3,9),(4,8),(7,7)
        pairs = legal_pairings(s, roll)
        self.assertIn((7,7), pairs)
        # Apply (7,7) should move 7 twice if possible
        apply_pairing(s, (7,7))
        self.assertEqual(s.turn.active_runners[7], 3)

if __name__ == '__main__':
    unittest.main()
