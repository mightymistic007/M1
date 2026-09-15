import unittest
from models.m4_optimization_solver import M4OptimizationSolver

class TestM4SolverEdgeCases(unittest.TestCase):
    def setUp(self):
        self.solver = M4OptimizationSolver()

    def test_zero_delay_defaults_to_option_c(self):
        """When delay is 0, solver should pick Option C (zero additional cost)."""
        batch = [{
            "shipment_id": "EDGE-ZERO-DELAY",
            "order_value_usd": 150.0,
            "estimated_delay_days": 0,
            "predicted_delay_risk": 0.05
        }]
        res = self.solver.solve_batch(batch)
        assigned = [o for o in res[0]["prescribed_options"] if o["optimal_assigned"]][0]
        self.assertEqual(assigned["option_id"], "OPT-C")
        self.assertEqual(assigned["net_cost_increase_usd"], 0.0)

    def test_negative_and_corrupt_numeric_inputs(self):
        """Negative order values or malformed strings must sanitize to safe fallbacks."""
        batch = [
            {"shipment_id": "CORRUPT-1", "order_value_usd": -50.0, "estimated_delay_days": "bad_val"},
            {"order_value_usd": None, "estimated_delay_days": -4}
        ]
        res = self.solver.solve_batch(batch)
        self.assertEqual(len(res), 2)
        # Verify valid structure returned without unhandled exceptions
        self.assertTrue(res[0]["prescribed_options"][2]["optimal_assigned"])

    def test_empty_batch_returns_empty_list(self):
        res = self.solver.solve_batch([])
        self.assertEqual(res, [])

if __name__ == "__main__":
    unittest.main()
