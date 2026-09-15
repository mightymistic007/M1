import os
import sys
import json
import argparse
import pandas as pd
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.m4_threshold_checker import M4ThresholdChecker
from models.m4_retrain_trigger_skeleton import M4RetrainTriggerSkeleton

def run_retraining_pipeline_eval(df_outcomes: pd.DataFrame) -> Dict[str, Any]:
    """Evaluates outcomes DataFrame and triggers retraining if drift is detected."""
    checker = M4ThresholdChecker()
    orchestrator = M4RetrainTriggerSkeleton(checker=checker)
    return orchestrator.process_telemetry_and_evaluate(df_outcomes)

def main():
    parser = argparse.ArgumentParser(description="M4 Retraining Trigger Runner")
    parser.add_argument("--input-csv", type=str, help="Path to actual outcomes CSV file")
    args = parser.parse_args()

    if args.input_csv and os.path.exists(args.input_csv):
        df = pd.read_csv(args.input_csv)
    else:
        print("No CSV provided or file not found. Generating default validation batch...")
        df = pd.DataFrame([
            {
                "shipment_id": f"RUNNER-SHIP-{i:03d}",
                "predicted_delay_days": 1,
                "actual_delay_days": 1,
                "predicted_penalty_usd": 0.0,
                "realized_penalty_usd": 0.0
            }
            for i in range(12)
        ])

    result = run_retraining_pipeline_eval(df)
    print("\n=== [M4 Track] Retraining Evaluation Results ===")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()