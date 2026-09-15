import unittest
from models.m4_optimization_solver import M4OptimizationSolver

class TestM4DummyCases(unittest.TestCase):
    def setUp(self):
        self.solver = M4OptimizationSolver()

    def test_empty_batch(self):
        """Verify solver handles empty input lists without throwing exceptions."""
        result = self.solver.solve_batch([])
        self.assertEqual(result, [])

    def test_zero_delay_shipment(self):
        """Verify shipments with 0 estimated delay default cleanly to standard handling."""
        zero_delay_batch = [{
            "shipment_id": "DUMMY-ZERO",
            "order_value_usd": 150.0,
            "estimated_delay_days": 0,
            "predicted_delay_risk": 0.05
        }]
        result = self.solver.solve_batch(zero_delay_batch)
        self.assertEqual(len(result), 1)
        # Option C should be marked optimal when delay is zero
        self.assertTrue(result[0]["prescribed_options"][2]["optimal_assigned"])

    def test_extreme_cost_budget_cap_guard(self):
        """Verify orders exceeding budget_max_cap_usd cannot assign expensive expedited options."""
        huge_order = [{
            "shipment_id": "DUMMY-EXPENSIVE",
            "order_value_usd": 600.0,  # Exceeds cap of $399.98
            "estimated_delay_days": 5,
            "predicted_delay_risk": 0.95
        }]
        result = self.solver.solve_batch(huge_order)
        opt_a = result[0]["prescribed_options"][0]["optimal_assigned"]
        opt_b = result[0]["prescribed_options"][1]["optimal_assigned"]
        # Both expedited options exceed budget cap, so neither can be optimal
        self.assertFalse(opt_a)
        self.assertFalse(opt_b)

    def test_contract_keys_presence(self):
        """Verify output strictly matches the downstream App Team schema."""
        batch = [{
            "shipment_id": "DUMMY-CONTRACT-CHECK",
            "order_value_usd": 200.0,
            "estimated_delay_days": 3,
            "predicted_delay_risk": 0.65
        }]
        res = self.solver.solve_batch(batch)[0]
        self.assertIn("shipment_id", res)
        self.assertIn("predicted_delay_risk", res)
        self.assertIn("initial_delay_estimate_days", res)
        self.assertIn("prescribed_options", res)
        self.assertEqual(len(res["prescribed_options"]), 3)

if __name__ == "__main__":
    unittest.main()
