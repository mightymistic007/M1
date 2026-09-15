import os
import sys
import json
import pandas as pd
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.m4_retrain_trigger_skeleton import M4RetrainTriggerSkeleton
from models.m4_threshold_checker import M4ThresholdChecker

def run_drift_debug_session(batch_df: pd.DataFrame) -> Dict[str, Any]:
    print("=== [M4 Track] Day 21: Retraining Integration Debug Session ===")
    checker = M4ThresholdChecker()
    trigger = M4RetrainTriggerSkeleton(checker=checker)
    
    # Run audit
    result = trigger.process_telemetry_and_evaluate(batch_df)
    summary = result.get("audit_summary", {})
    
    print(f"Audit Status: {summary.get('status')}")
    print(f"Total Evaluated: {summary.get('total_records')}")
    print(f"Discrepancy Rate: {summary.get('discrepancy_rate', 0) * 100:.2f}%")
    print(f"False Negative Rate: {summary.get('false_negative_rate', 0) * 100:.2f}%")
    print(f"Mean Squared Error: {summary.get('mean_squared_delay_error', 0):.4f}")
    print(f"Retrain Triggered: {result.get('retrain_initiated')}")
    
    if summary.get("trigger_reasons"):
        print("Triggers Tripped:")
        for r in summary["trigger_reasons"]:
            print(f"  - {r}")
            
    return result

if __name__ == "__main__":
    # Test batch with boundary condition
    test_batch = pd.DataFrame([
        {"shipment_id": f"DBG-{i:03d}", "predicted_delay_days": 1, "actual_delay_days": 3 if i < 3 else 1}
        for i in range(15)
    ])
    run_drift_debug_session(test_batch)
    