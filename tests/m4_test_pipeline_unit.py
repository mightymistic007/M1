import os
import sys
import unittest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.m4_pipeline_bridge import M4PipelineBridge

class TestM4PipelineUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bridge = M4PipelineBridge()

    def test_pipeline_empty_dataframe(self):
        """Pipeline should return an empty list without failing when passed an empty DataFrame."""
        empty_df = pd.DataFrame()
        result = self.bridge.predict_and_prescribe_batch(empty_df)
        self.assertEqual(result, [])

    def test_single_shipment_contract_integrity(self):
        """Verify strict adherence to schema keys and data types for a single shipment record."""
        df_single = pd.DataFrame([{
            "shipping_mode": 0, "type": 1, "market": 2, "order_region": 1,
            "customer_segment": 0, "category_name": 10, "days_for_shipment_scheduled": 3,
            "order_item_quantity": 1, "order_item_product_price": 140.0, "sales": 140.0,
            "order_item_id": "UNIT-TEST-SINGLE"
        }])
        
        prescriptions = self.bridge.predict_and_prescribe_batch(df_single)
        self.assertEqual(len(prescriptions), 1)
        record = prescriptions[0]
        
        self.assertEqual(record["shipment_id"], "UNIT-TEST-SINGLE")
        self.assertIsInstance(record["predicted_delay_risk"], float)
        self.assertGreaterEqual(record["predicted_delay_risk"], 0.0)
        self.assertLessEqual(record["predicted_delay_risk"], 1.0)
        self.assertIsInstance(record["initial_delay_estimate_days"], int)
        
        # Verify prescribed options structure
        options = record["prescribed_options"]
        self.assertEqual(len(options), 3)
        self.assertEqual([opt["option_id"] for opt in options], ["OPT-A", "OPT-B", "OPT-C"])

    def test_pipeline_missing_noncritical_column_resilience(self):
        """Verify pipeline handles DataFrames using fallback defaults when sales column is missing."""
        df_no_sales = pd.DataFrame([{
            "shipping_mode": 2, "type": 0, "market": 3, "order_region": 4,
            "customer_segment": 2, "category_name": 8, "days_for_shipment_scheduled": 2,
            "order_item_quantity": 2, "order_item_product_price": 95.0,
            "order_item_id": "UNIT-TEST-NO-SALES"
        }])
        
        prescriptions = self.bridge.predict_and_prescribe_batch(df_no_sales)
        self.assertEqual(len(prescriptions), 1)
        self.assertGreater(prescriptions[0]["prescribed_options"][0]["cost_usd"], 0.0)

    def test_synthetic_stress_batch_uniqueness(self):
        """Validate assignment uniqueness and capacity upper bounds on a 50-record batch."""
        records = []
        for i in range(50):
            records.append({
                "shipping_mode": i % 4, "type": i % 2, "market": i % 5, "order_region": i % 8,
                "customer_segment": i % 3, "category_name": (i * 2) % 25, "days_for_shipment_scheduled": (i % 4) + 1,
                "order_item_quantity": (i % 3) + 1, "order_item_product_price": 40.0 + (i * 5.0),
                "sales": (40.0 + (i * 5.0)) * ((i % 3) + 1), "order_item_id": f"BATCH-TEST-{i:03d}"
            })
        
        df_batch = pd.DataFrame(records)
        prescriptions = self.bridge.predict_and_prescribe_batch(df_batch)
        self.assertEqual(len(prescriptions), 50)
        
        opt_a_count = 0
        opt_b_count = 0
        for item in prescriptions:
            assigned = [opt["optimal_assigned"] for opt in item["prescribed_options"]]
            self.assertEqual(sum(assigned), 1, f"Shipment {item['shipment_id']} must have exactly 1 assigned option")
            if item["prescribed_options"][0]["optimal_assigned"]:
                opt_a_count += 1
            if item["prescribed_options"][1]["optimal_assigned"]:
                opt_b_count += 1
                
        # Air Freight limit <= ceil(0.20 * 50) = 10; Alternate Supplier limit <= ceil(0.35 * 50) = 18
        self.assertLessEqual(opt_a_count, 10)
        self.assertLessEqual(opt_b_count, 18)

if __name__ == "__main__":
    unittest.main()
    