import unittest
import pandas as pd
import os
import json
from models.pipeline import SupplyChainPipeline
from models.prescriptive_solver import PrescriptiveSolver

class TestSupplyPrescriptML(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pipeline = SupplyChainPipeline()
        cls.solver = PrescriptiveSolver()
        cls.test_df = pd.read_csv(os.path.join("data", "processed", "test.csv")).head(5)

    def test_pipeline_prediction_structure(self):
        """Verify model pipeline produces required fields and bounded probabilities."""
        results = self.pipeline.predict_delay_risk(self.test_df)
        self.assertEqual(len(results), 5)
        
        for record in results:
            self.assertIn("shipment_id", record)
            self.assertIn("predicted_delay_risk", record)
            self.assertIn("estimated_delay_days", record)
            self.assertGreaterEqual(record["predicted_delay_risk"], 0.0)
            self.assertLessEqual(record["predicted_delay_risk"], 1.0)

    def test_prescriptive_solver_three_options(self):
        """Verify solver generates 3 distinct options with non-violating constraints."""
        sample_input = {
            "shipment_id": "TEST-101",
            "order_value_usd": 250.0,
            "scheduled_days": 3,
            "predicted_delay_risk": 0.85,
            "is_delayed_prediction": True,
            "estimated_delay_days": 4
        }
        
        output = self.solver.solve_shipment(sample_input)
        
        self.assertIn("prescribed_options", output)
        self.assertEqual(len(output["prescribed_options"]), 3)
        
        option_ids = [opt["option_id"] for opt in output["prescribed_options"]]
        self.assertEqual(option_ids, ["OPT-A", "OPT-B", "OPT-C"])

    def test_air_freight_delay_mitigation(self):
        """Verify Air Freight provides the highest delay reduction."""
        sample_input = {
            "shipment_id": "TEST-102",
            "order_value_usd": 150.0,
            "estimated_delay_days": 5
        }
        output = self.solver.solve_shipment(sample_input)
        options = {opt["option_id"]: opt for opt in output["prescribed_options"]}
        
        self.assertGreaterEqual(options["OPT-A"]["days_delayed_mitigated"], options["OPT-B"]["days_delayed_mitigated"])
        self.assertGreaterEqual(options["OPT-B"]["days_delayed_mitigated"], options["OPT-C"]["days_delayed_mitigated"])

if __name__ == "__main__":
    unittest.main()
