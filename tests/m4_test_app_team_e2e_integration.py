import os
import sys
import unittest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.m4_optimization_solver import M4OptimizationSolver
from models.m4_validate_writeback_payload import validate_writeback_batch
from models.m4_threshold_checker import M4ThresholdChecker
from models.m4_retrain_trigger_skeleton import M4RetrainTriggerSkeleton

def verify_json_contract(prescriptions):
    """Fallback in-line contract assertion matching JSON Draft-07 specs."""
    if not isinstance(prescriptions, list) or len(prescriptions) == 0:
        return False
    for item in prescriptions:
        if "shipment_id" not in item or "prescribed_options" not in item:
            return False
        opts = item["prescribed_options"]
        if not isinstance(opts, list) or len(opts) != 3:
            return False
        optimal_flags = [opt.get("optimal_assigned", False) for opt in opts]
        if sum(optimal_flags) != 1:
            return False
    return True

class TestAppTeamE2EIntegration(unittest.TestCase):
    def setUp(self):
        self.solver = M4OptimizationSolver()
        self.checker = M4ThresholdChecker(min_batch_size=10)
        self.orchestrator = M4RetrainTriggerSkeleton(checker=self.checker)

    def test_full_app_team_coordination_cycle(self):
        """
        Step 1: App Team dispatches batch of raw shipments.
        Step 2: M4 Solver prescribes optimal mitigation options matching JSON contract.
        Step 3: App Team sends back actual delivery telemetry matching write-back schema.
        Step 4: M4 Closed-Loop Monitor audits drift and handles retrain decisions.
        """
        # --- 1. Outgoing Prescription Request ---
        shipments_request = [
            {
                "shipment_id": f"APP-E2E-{i:03d}",
                "order_value_usd": 180.0 + (i * 10),
                "estimated_delay_days": 4 if i < 3 else 1,
                "predicted_delay_risk": 0.85 if i < 3 else 0.20
            }
            for i in range(12)
        ]

        # --- 2. Solver Prescription & JSON Draft-07 Compliance ---
        prescriptions = self.solver.solve_batch(shipments_request)
        self.assertEqual(len(prescriptions), 12)
        self.assertTrue(verify_json_contract(prescriptions))

        # --- 3. App Team Delivery Outcomes Write-Back ---
        writeback_payload = []
        for p in prescriptions:
            chosen = [opt for opt in p["prescribed_options"] if opt["optimal_assigned"]][0]
            actual_delay = chosen["final_estimated_delay"]
            writeback_payload.append({
                "shipment_id": p["shipment_id"],
                "assigned_option_id": chosen["option_id"],
                "predicted_delay_days": chosen["final_estimated_delay"],
                "actual_delay_days": actual_delay,
                "realized_penalty_usd": float(actual_delay * 45.0),
                "predicted_penalty_usd": float(chosen["final_estimated_delay"] * 45.0)
            })

        # Validate write-back payload adheres to schema contract
        self.assertTrue(validate_writeback_batch(writeback_payload))

        # --- 4. Closed-Loop Telemetry Ingestion & Drift Evaluation ---
        outcomes_df = pd.DataFrame(writeback_payload)
        decision = self.orchestrator.process_telemetry_and_evaluate(outcomes_df)

        self.assertEqual(decision["audit_summary"]["status"], "EVALUATED")
        self.assertFalse(decision["retrain_initiated"])
        self.assertEqual(decision["pipeline_status"], "PASSED_NOMINAL")

if __name__ == "__main__":
    unittest.main()