import unittest
import pandas as pd
from models.m4_threshold_checker import M4ThresholdChecker

class TestM4ThresholdChecker(unittest.TestCase):
    def setUp(self):
        self.checker = M4ThresholdChecker(
            delay_discrepancy_limit=2,
            discrepancy_rate_threshold=0.15,
            false_negative_threshold=0.05
        )

    def test_nominal_within_thresholds(self):
        df_nominal = pd.DataFrame([
            {"shipment_id": f"NOM-{i}", "predicted_delay_days": 2, "actual_delay_days": 2}
            for i in range(20)
        ])
        result = self.checker.evaluate_outcomes(df_nominal)
        self.assertFalse(result["retrain_triggered"])
        self.assertEqual(result["discrepancy_rate"], 0.0)
        self.assertEqual(len(result["trigger_reasons"]), 0)

    def test_discrepancy_trigger_exceeded(self):
        records = []
        for i in range(20):
            # 5 out of 20 (25%) have a gap of 3 days (>= 2 threshold)
            actual = 5 if i < 5 else 2
            records.append({
                "shipment_id": f"DISC-{i}",
                "predicted_delay_days": 2,
                "actual_delay_days": actual
            })
        df_disc = pd.DataFrame(records)
        result = self.checker.evaluate_outcomes(df_disc)
        self.assertTrue(result["retrain_triggered"])
        self.assertGreaterEqual(result["discrepancy_rate"], 0.15)

    def test_severe_false_negative_trigger(self):
        records = []
        for i in range(20):
            # 2 out of 20 (10%) predicted 0 delay but suffered 4 days delay
            pred = 0 if i < 2 else 2
            actual = 4 if i < 2 else 2
            records.append({
                "shipment_id": f"FN-{i}",
                "predicted_delay_days": pred,
                "actual_delay_days": actual
            })
        df_fn = pd.DataFrame(records)
        result = self.checker.evaluate_outcomes(df_fn)
        self.assertTrue(result["retrain_triggered"])
        self.assertGreaterEqual(result["false_negative_rate"], 0.05)

if __name__ == "__main__":
    unittest.main()