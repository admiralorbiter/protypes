
import unittest
from trainer.cards import card_from_str
from trainer.odds import flop_set_prob_pocket_pair, flop_pair_or_better_unpaired, flop_flush_stats_suited, river_flush_prob_two_suited

class TestOdds(unittest.TestCase):
    def test_pocket_pair_set_probabilities(self):
        stats = flop_set_prob_pocket_pair()
        self.assertAlmostEqual(stats['set_or_better'], stats['set_only'] + stats['quads'], places=10)
        self.assertTrue(0.11 < stats['set_or_better'] < 0.12)

    def test_unpaired_pair_or_better(self):
        stats = flop_pair_or_better_unpaired()
        self.assertTrue(0.32 < stats['pair_or_better'] < 0.33)
        self.assertTrue(0.019 < stats['two_pair'] < 0.021)

    def test_flush_stats(self):
        stats = flop_flush_stats_suited()
        self.assertTrue(0.10 < stats['flush_draw'] < 0.11 + 0.01)  # around 10.9%
        self.assertTrue(0.008 < stats['flush_flop'] < 0.009)

    def test_flush_by_river_two_suited(self):
        p = river_flush_prob_two_suited()
        self.assertTrue(0.06 < p < 0.07)  # around 6.4%-6.5%

if __name__ == '__main__':
    unittest.main()
