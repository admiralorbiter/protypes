
import unittest
from planner.formulas import OneGroupInput, sample_size_one_group, GroupRow, overall_moe_from_allocation, allocate, solve_total_n_for_overall_moe

class TestPlanner(unittest.TestCase):
    def test_classic_385(self):
        # Infinite pop approx (N very large), p=0.5, moe=5%, conf=95%
        res = sample_size_one_group(OneGroupInput(N=None, moe=0.05, n=None, conf=0.95, p_est=0.5, deff=1.0, response_rate=1.0))
        self.assertTrue(abs(res.n_required - 385) <= 1)

    def test_fpc_small_pop(self):
        res_inf = sample_size_one_group(OneGroupInput(N=None, moe=0.05, n=None, conf=0.95, p_est=0.5, deff=1.0, response_rate=1.0))
        res_fin = sample_size_one_group(OneGroupInput(N=1000, moe=0.05, n=None, conf=0.95, p_est=0.5, deff=1.0, response_rate=1.0))
        self.assertLessEqual(res_fin.n_required, res_inf.n_required)

    def test_overall_moe_binary_search(self):
        groups = [GroupRow("A", 800, 0.5, 1.0, 1.0), GroupRow("B", 1200, 0.5, 1.0, 1.0)]
        total_n, alloc = solve_total_n_for_overall_moe(groups, conf=0.95, target_moe=0.05, style="proportional")
        moe = overall_moe_from_allocation(groups, alloc, conf=0.95)
        self.assertLessEqual(moe, 0.051)

if __name__ == "__main__":
    unittest.main()
