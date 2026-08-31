import unittest
import os
import json
import pandas as pd
from models.pipeline import SupplyChainPipeline
from models.prescriptive_solver import PrescriptiveSolver
from models.retrain_pipeline import execute_closed_loop_retraining

class TestClosedLoopIntegration(unittest.TestCase):

    def test_full_operational_cycle(self):
        """Validates end-to-end inference, solver contracts, and retraining triggers."""
        # 1. Pipeline Prediction Verification
        test_path = os.path.join("data", "processed", "test.csv")
        self.assertTrue(os.path.exists(test_path), "Test dataset missing.")
        
        test_df = pd.read_csv(test_path).head(3)
        pipeline = SupplyChainPipeline()
        predictions = pipeline.predict_delay_risk(test_df)
        
        self.assertEqual(len(predictions), 3)
        self.assertIn("predicted_delay_risk", predictions[0])

        # 2. Solver Option Contract Verification
        solver = PrescriptiveSolver()
        for pred in predictions:
            solution = solver.solve_shipment(pred)
            self.assertIn("prescribed_options", solution)
            self.assertEqual(len(solution["prescribed_options"]), 3)
            
            # Check schema field presence
            for opt in solution["prescribed_options"]:
                self.assertIn("option_id", opt)
                self.assertIn("cost_usd", opt)
                self.assertIn("days_delayed_mitigated", opt)
                self.assertIn("tradeoff", opt)

        # 3. Retraining Artifact Verification
        retrained_model_path = os.path.join("models", "retrained_xgboost.json")
        self.assertTrue(os.path.exists(retrained_model_path), "Retrained model artifact not found.")

if __name__ == "__main__":
    unittest.main()

