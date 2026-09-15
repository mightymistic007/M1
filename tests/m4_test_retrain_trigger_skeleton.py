import unittest
import pandas as pd
from models.m4_retrain_trigger_skeleton import M4RetrainTriggerSkeleton

class TestM4RetrainTriggerSkeleton(unittest.TestCase):
    def setUp(self):
        self.trigger = M4RetrainTriggerSkeleton()

    def test_nominal_telemetry_does_not_trigger_retrain(self):
        df_nominal = pd.DataFrame([
            {"shipment_id": f"NOM-{i:03d}", "predicted_delay_days": 2, "actual_delay_days": 2}
            for i in range(15)
        ])
        result = self.trigger.process_telemetry_and_evaluate(df_nominal)
        self.assertFalse(result["retrain_initiated"])
        self.assertEqual(result["pipeline_status"], "PASSED_NOMINAL")

    def test_discrepant_telemetry_triggers_pipeline(self):
        records = []
        for i in range(20):
            # 6 records with 3-day discrepancy
            records.append({
                "shipment_id": f"DISC-{i:03d}",
                "predicted_delay_days": 1,
                "actual_delay_days": 4 if i < 6 else 1
            })
        df_disc = pd.DataFrame(records)
        result = self.trigger.process_telemetry_and_evaluate(df_disc)
        self.assertTrue(result["retrain_initiated"])
        self.assertEqual(result["pipeline_status"], "TRIGGERED")

if __name__ == "__main__":
    unittest.main()
    