import unittest
from models.m4_optimization_solver import M4OptimizationSolver

class TestM4OptimizationSkeleton(unittest.TestCase):
    def setUp(self):
        self.solver = M4OptimizationSolver()
        self.dummy_shipments = [
            {"shipment_id": "SHIP-001", "order_value_usd": 150.0, "estimated_delay_days": 5, "predicted_delay_risk": 0.85},
            {"shipment_id": "SHIP-002", "order_value_usd": 200.0, "estimated_delay_days": 3, "predicted_delay_risk": 0.70},
            {"shipment_id": "SHIP-003", "order_value_usd": 120.0, "estimated_delay_days": 1, "predicted_delay_risk": 0.35},
            {"shipment_id": "SHIP-004", "order_value_usd": 380.0, "estimated_delay_days": 4, "predicted_delay_risk": 0.80},
            {"shipment_id": "SHIP-005", "order_value_usd": 210.0, "estimated_delay_days": 2, "predicted_delay_risk": 0.40}
        ]

    def test_dummy_batch_assignment_and_schema(self):
        results = self.solver.solve_batch(self.dummy_shipments)
        self.assertEqual(len(results), 5)

        opt_a_count = 0
        opt_b_count = 0

        for item in results:
            self.assertIn("prescribed_options", item)
            self.assertEqual(len(item["prescribed_options"]), 3)

            # Exactly one option must be optimal per shipment
            optimal_flags = [opt["optimal_assigned"] for opt in item["prescribed_options"]]
            self.assertEqual(sum(optimal_flags), 1, f"Failed assignment uniqueness for {item['shipment_id']}")

            if item["prescribed_options"][0]["optimal_assigned"]:
                opt_a_count += 1
            if item["prescribed_options"][1]["optimal_assigned"]:
                opt_b_count += 1

        # Check capacity bounds (N=5 -> ceil(0.2*5)=1 for A, ceil(0.35*5)=2 for B)
        self.assertLessEqual(opt_a_count, 1)
        self.assertLessEqual(opt_b_count, 2)

if __name__ == "__main__":
    unittest.main()
