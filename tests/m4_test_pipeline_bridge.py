import unittest
import pandas as pd
from models.m4_pipeline_bridge import M4PipelineBridge

class TestM4PipelineBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bridge = M4PipelineBridge()
        cls.sample_data = pd.DataFrame([
            {
                "shipping_mode": 1, "type": 0, "market": 2, "order_region": 3,
                "customer_segment": 1, "category_name": 5, "days_for_shipment_scheduled": 4,
                "order_item_quantity": 2, "order_item_product_price": 75.0, "sales": 150.0,
                "order_item_id": "TEST-BRIDGE-001"
            },
            {
                "shipping_mode": 2, "type": 1, "market": 1, "order_region": 0,
                "customer_segment": 0, "category_name": 12, "days_for_shipment_scheduled": 2,
                "order_item_quantity": 1, "order_item_product_price": 220.0, "sales": 220.0,
                "order_item_id": "TEST-BRIDGE-002"
            }
        ])

    def test_pipeline_bridge_end_to_end(self):
        prescriptions = self.bridge.predict_and_prescribe_batch(self.sample_data)
        self.assertEqual(len(prescriptions), 2)
        
        for item in prescriptions:
            self.assertIn("shipment_id", item)
            self.assertIn("predicted_delay_risk", item)
            self.assertIn("initial_delay_estimate_days", item)
            self.assertEqual(len(item["prescribed_options"]), 3)
            # Verify one optimal action selected per item
            optimals = [opt["optimal_assigned"] for opt in item["prescribed_options"]]
            self.assertEqual(sum(optimals), 1)

if __name__ == "__main__":
    unittest.main()

