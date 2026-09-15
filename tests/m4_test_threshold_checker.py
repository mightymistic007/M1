import unittest
import pandas as pd
from models.m4_threshold_checker import M4ThresholdChecker

class TestM4ThresholdCheckerRefined(unittest.TestCase):
    def setUp(self):
        self.checker = M4ThresholdChecker(
            delay_discrepancy_limit=2,
            discrepancy_rate_threshold=0.15,
            false_negative_threshold=0.05,
            min_batch_size=10
        )

    def test_min_batch_size_guard(self):
        """Micro-batches below 10 records must not trigger a false retrain."""
        micro_batch = pd.DataFrame([
            {"shipment_id": "MICRO-1", "predicted_delay_days": 0, "actual_delay_days": 5},
            {"shipment_id": "MICRO-2", "predicted_delay_days": 1, "actual_delay_days": 4}
        ])
        result = self.checker.evaluate_outcomes(micro_batch)
        self.assertFalse(result["retrain_triggered"])
        self.assertIn("INSUFFICIENT_SAMPLE_SIZE", result["status"])

    def test_refined_audit_trail_and_severe_drift(self):
        """Test detection of severe disruptions (>= 4 days) and presence of shipment IDs in audit trail."""
        records = []
        for i in range(25):
            pred = 1
            # 1 outlier with severe 5-day disruption (gap = 4 days)
            actual = 5 if i == 0 else 1
            records.append({
                "shipment_id": f"SHIP-AUDIT-{i:03d}",
                "predicted_delay_days": pred,
                "actual_delay_days": actual
            })
        
        df = pd.DataFrame(records)
        result = self.checker.evaluate_outcomes(df)
        self.assertTrue(result["retrain_triggered"])
        self.assertIn("SHIP-AUDIT-000", result["discrepant_shipment_ids"])
        self.assertEqual(result["severe_disruption_count"], 1)

if __name__ == "__main__":
    unittest.main()