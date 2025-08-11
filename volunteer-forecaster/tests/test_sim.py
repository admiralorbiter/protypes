
import unittest, numpy as np
import pandas as pd
from forecaster.data import load_csv, summarize_segments
from forecaster.model import simulate_shows, probability_metrics

class TestSim(unittest.TestCase):
    def test_simulate_positive(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_volunteer_history.csv")
        df = load_csv(path)
        seg = summarize_segments(df)
        plan = [{"event_type":"career_day","industry":"Education","reachouts":200}]
        res = simulate_shows(plan, seg, iters=2000, seed=1)
        self.assertGreater(res["expected"], 1.0)
        pm = probability_metrics(res["totals"], target=10)
        self.assertTrue(0.0 <= pm["p_hit"] <= 1.0)

if __name__ == "__main__":
    unittest.main()
