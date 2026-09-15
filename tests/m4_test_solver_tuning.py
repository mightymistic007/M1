import unittest
import pandas as pd
from models.m4_optimization_solver import M4OptimizationSolver

class TestM4SolverTuning(unittest.TestCase):
    def setUp(self):
        self.solver = M4OptimizationSolver()

    def test_micro_batch_capacity_ceiling(self):
        """Even with N=3 records, ceiling rounding should allow at least 1 Option A assignment if needed."""
        batch = [
            {"shipment_id": f"MICRO-{i}", "order_value_usd": 150.0, "estimated_delay_days": 5, "predicted_delay_risk": 0.9}
            for i in range(3)
        ]
        results = self.solver.solve_batch(batch)
        opt_a_assigned = sum(1 for r in results if r["prescribed_options"][0]["optimal_assigned"])
        # ceil(0.20 * 3) = 1
        self.assertEqual(opt_a_assigned, 1)

    def test_exact_budget_cap_boundary(self):
        """Shipment with baseline cost that produces an Option A cost slightly above the cap should safely fall back."""
        # Baseline $300 -> Option A (+45%) is $435.00, which breaches $399.98 cap
        # Option B (+15%) is $345.00, which satisfies the cap
        batch = [{
            "shipment_id": "BOUNDARY-CAP",
            "order_value_usd": 300.0,
            "estimated_delay_days": 4,
            "predicted_delay_risk": 0.85
        }]
        results = self.solver.solve_batch(batch)
        assigned = [opt for opt in results[0]["prescribed_options"] if opt["optimal_assigned"]][0]
        self.assertLessEqual(assigned["cost_usd"], 401.0)
        # Option A must NOT be assigned due to budget cap violation
        self.assertNotEqual(assigned["option_id"], "OPT-A")

    def test_high_delay_penalty_incentive(self):
        """Severe 5-day delay on reasonable order value must choose Option A when within limits."""
        batch = [{
            "shipment_id": "HIGH-PENALTY",
            "order_value_usd": 120.0,
            "estimated_delay_days": 5,
            "predicted_delay_risk": 0.95
        }]
        results = self.solver.solve_batch(batch)
        assigned = [opt for opt in results[0]["prescribed_options"] if opt["optimal_assigned"]][0]
        self.assertEqual(assigned["option_id"], "OPT-A")
        self.assertEqual(assigned["days_delayed_mitigated"], 4)

if __name__ == "__main__":
    unittest.main()
