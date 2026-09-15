import unittest
import pandas as pd
import numpy as np
from models.m4_pipeline_bridge import M4PipelineBridge

class TestM4ConstraintHarness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bridge = M4PipelineBridge()
        
        # Build a 20-record batch mimicking realistic supply chain variations
        np.random.seed(42)
        records = []
        for i in range(20):
            records.append({
                "shipping_mode": int(np.random.choice([0, 1, 2, 3])),
                "type": int(np.random.choice([0, 1])),
                "market": int(np.random.randint(0, 5)),
                "order_region": int(np.random.randint(0, 15)),
                "customer_segment": int(np.random.randint(0, 3)),
                "category_name": int(np.random.randint(0, 30)),
                "days_for_shipment_scheduled": int(np.random.randint(1, 5)),
                "order_item_quantity": int(np.random.randint(1, 4)),
                "order_item_product_price": float(np.random.uniform(25.0, 350.0)),
                "sales": float(np.random.uniform(25.0, 350.0)),
                "order_item_id": f"HARNESS-SHIP-{i+1:04d}"
            })
        cls.batch_df = pd.DataFrame(records)

    def test_capacity_and_budget_constraints_on_sample_batch(self):
        prescriptions = self.bridge.predict_and_prescribe_batch(self.batch_df)
        self.assertEqual(len(prescriptions), 20)

        opt_a_count = 0
        opt_b_count = 0
        budget_cap = self.bridge.solver.max_cap

        for item in prescriptions:
            options = item["prescribed_options"]
            self.assertEqual(len(options), 3)

            # Constraint 1: Exactly 1 optimal assignment per shipment
            assigned = [opt["optimal_assigned"] for opt in options]
            self.assertEqual(sum(assigned), 1, f"Assignment violation for {item['shipment_id']}")

            # Constraint 2: Budget ceiling violation check
            for opt in options:
                if opt["optimal_assigned"]:
                    self.assertLessEqual(
                        opt["cost_usd"], 
                        budget_cap + 1.0, 
                        f"Budget cap violation: {opt['cost_usd']} > {budget_cap}"
                    )

            if options[0]["optimal_assigned"]:
                opt_a_count += 1
            if options[1]["optimal_assigned"]:
                opt_b_count += 1

        # Constraint 3: Capacity bounds (N=20 -> ceil(0.2*20) = 4, ceil(0.35*20) = 7)
        self.assertLessEqual(opt_a_count, 4, f"Option A exceeded 20% limit: {opt_a_count}/20")
        self.assertLessEqual(opt_b_count, 7, f"Option B exceeded 35% limit: {opt_b_count}/20")

if __name__ == "__main__":
    unittest.main()
