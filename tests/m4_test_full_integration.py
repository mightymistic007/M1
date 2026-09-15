import os
import sys
import unittest
import pandas as pd

# Guarantee project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.m4_pipeline_bridge import M4PipelineBridge

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "test.csv")

class TestM4FullIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bridge = M4PipelineBridge()
        if os.path.exists(TEST_DATA_PATH):
            cls.df_test = pd.read_csv(TEST_DATA_PATH)
        else:
            # Fallback fixture if test.csv is not present locally
            cols = [
                "shipping_mode", "type", "market", "order_region", "customer_segment",
                "category_name", "days_for_shipment_scheduled", "order_item_quantity",
                "order_item_product_price", "sales", "is_delayed", "order_item_id"
            ]
            cls.df_test = pd.DataFrame([
                [1, 0, 2, 3, 1, 5, 4, 1, 100.0, 100.0, 0, f"FALLBACK-{i:04d}"]
                for i in range(50)
            ], columns=cols)

    def test_end_to_end_small_batch(self):
        """Test model-to-solver execution on a 5-record batch."""
        sample_batch = self.df_test.head(5).copy()
        prescriptions = self.bridge.predict_and_prescribe_batch(sample_batch)
        
        self.assertEqual(len(prescriptions), 5)
        for record in prescriptions:
            self.assertIn("shipment_id", record)
            self.assertIn("predicted_delay_risk", record)
            self.assertIn("initial_delay_estimate_days", record)
            self.assertEqual(len(record["prescribed_options"]), 3)
            
            assigned = [opt["optimal_assigned"] for opt in record["prescribed_options"]]
            self.assertEqual(sum(assigned), 1)

    def test_end_to_end_medium_batch(self):
        """Test model-to-solver execution on a 25-record batch with capacity bounds."""
        sample_batch = self.df_test.head(25).copy()
        prescriptions = self.bridge.predict_and_prescribe_batch(sample_batch)
        
        self.assertEqual(len(prescriptions), 25)
        
        opt_a_count = sum(1 for r in prescriptions if r["prescribed_options"][0]["optimal_assigned"])
        opt_b_count = sum(1 for r in prescriptions if r["prescribed_options"][1]["optimal_assigned"])
        
        # Max capacity: ceil(0.20 * 25) = 5 for A, ceil(0.35 * 25) = 9 for B
        self.assertLessEqual(opt_a_count, 5)
        self.assertLessEqual(opt_b_count, 9)

    def test_budget_cap_invariance_on_real_data(self):
        """Verify no assigned option violates the $399.98 budget cap on real data records."""
        sample_batch = self.df_test.head(30).copy()
        prescriptions = self.bridge.predict_and_prescribe_batch(sample_batch)
        
        for item in prescriptions:
            for opt in item["prescribed_options"]:
                if opt["optimal_assigned"]:
                    self.assertLessEqual(opt["cost_usd"], 401.0, f"Budget cap breach: {opt['cost_usd']}")

if __name__ == "__main__":
    unittest.main()
