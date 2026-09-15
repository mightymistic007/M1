import unittest
from models.m4_optimization_solver import M4OptimizationSolver

class TestM4ScenarioSanity(unittest.TestCase):
    def setUp(self):
        self.solver = M4OptimizationSolver()

    def test_nominal_zero_delay_chooses_option_c(self):
        nominal = [{
            "shipment_id": "TEST-SANITY-01",
            "order_value_usd": 150.0,
            "estimated_delay_days": 0,
            "predicted_delay_risk": 0.05
        }]
        res = self.solver.solve_batch(nominal)[0]
        self.assertTrue(res["prescribed_options"][2]["optimal_assigned"])
        self.assertEqual(res["prescribed_options"][2]["net_cost_increase_usd"], 0.0)

    def test_tradeoff_monotonicity(self):
        """Verify that Option A provides greater or equal delay mitigation than Option B, and Option B >= Option C."""
        item = [{
            "shipment_id": "TEST-SANITY-02",
            "order_value_usd": 200.0,
            "estimated_delay_days": 5,
            "predicted_delay_risk": 0.85
        }]
        opts = self.solver.solve_batch(item)[0]["prescribed_options"]
        days_saved_a = opts[0]["days_delayed_mitigated"]
        days_saved_b = opts[1]["days_delayed_mitigated"]
        days_saved_c = opts[2]["days_delayed_mitigated"]

        self.assertGreaterEqual(days_saved_a, days_saved_b)
        self.assertGreaterEqual(days_saved_b, days_saved_c)

if __name__ == "__main__":
    unittest.main()
