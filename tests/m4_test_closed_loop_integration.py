import unittest
import pandas as pd
from models.m4_retrain_trigger_skeleton import M4RetrainTriggerSkeleton
from models.m4_threshold_checker import M4ThresholdChecker

class TestM4ClosedLoopIntegration(unittest.TestCase):
    def setUp(self):
        self.checker = M4ThresholdChecker(
            delay_discrepancy_limit=2,
            discrepancy_rate_threshold=0.15,
            false_negative_threshold=0.05,
            min_batch_size=10
        )
        self.orchestrator = M4RetrainTriggerSkeleton(checker=self.checker)

    def test_end_to_end_closed_loop_boundary_pass(self):
        """Discrepancy rate just below 15% threshold must not trigger retraining."""
        # 1 discrepant out of 10 = 10% (< 15%)
        records = [
            {"shipment_id": f"BOUND-{i:02d}", "predicted_delay_days": 2, "actual_delay_days": 4 if i == 0 else 2}
            for i in range(10)
        ]
        df = pd.DataFrame(records)
        res = self.orchestrator.process_telemetry_and_evaluate(df)
        self.assertFalse(res["retrain_initiated"])
        self.assertEqual(res["pipeline_status"], "PASSED_NOMINAL")

    def test_end_to_end_closed_loop_boundary_fail(self):
        """Discrepancy rate at or above 15% threshold must trigger retraining."""
        # 2 discrepant out of 10 = 20% (>= 15%)
        records = [
            {"shipment_id": f"BOUND-TRIP-{i:02d}", "predicted_delay_days": 2, "actual_delay_days": 4 if i < 2 else 2}
            for i in range(10)
        ]
        df = pd.DataFrame(records)
        res = self.orchestrator.process_telemetry_and_evaluate(df)
        self.assertTrue(res["retrain_initiated"])
        self.assertEqual(res["pipeline_status"], "TRIGGERED")

    def test_resilience_to_missing_shipment_ids(self):
        """Telemetry missing shipment_id column should evaluate gracefully."""
        df = pd.DataFrame([
            {"predicted_delay_days": 1, "actual_delay_days": 1}
            for _ in range(12)
        ])
        res = self.orchestrator.process_telemetry_and_evaluate(df)
        self.assertFalse(res["retrain_initiated"])
        self.assertEqual(res["audit_summary"]["status"], "EVALUATED")

if __name__ == "__main__":
    unittest.main()
    