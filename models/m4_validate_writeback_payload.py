import os
import sys
import pandas as pd
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

REQUIRED_WRITEBACK_FIELDS = {
    "shipment_id": str,
    "assigned_option_id": str,
    "predicted_delay_days": int,
    "actual_delay_days": int,
    "realized_penalty_usd": (float, int),
    "predicted_penalty_usd": (float, int)
}

VALID_OPTIONS = {"OPT-A", "OPT-B", "OPT-C"}

def validate_writeback_batch(records: List[Dict[str, Any]]) -> bool:
    """Validates the schema and value integrity of the App Team write-back payload."""
    if not records:
        raise ValueError("Write-back payload cannot be empty.")

    for idx, rec in enumerate(records):
        for field, expected_type in REQUIRED_WRITEBACK_FIELDS.items():
            if field not in rec:
                raise KeyError(f"Record {idx} missing required field '{field}'")
            if not isinstance(rec[field], expected_type):
                raise TypeError(
                    f"Record {idx} field '{field}' must be {expected_type}, got {type(rec[field])}"
                )

        if rec["assigned_option_id"] not in VALID_OPTIONS:
            raise ValueError(
                f"Record {idx} invalid assigned_option_id: {rec['assigned_option_id']}"
            )

        if rec["actual_delay_days"] < 0 or rec["predicted_delay_days"] < 0:
            raise ValueError(f"Record {idx} delay values cannot be negative")

    return True

if __name__ == "__main__":
    sample_batch = [
        {
            "shipment_id": "SHIP-001",
            "assigned_option_id": "OPT-A",
            "predicted_delay_days": 1,
            "actual_delay_days": 2,
            "realized_penalty_usd": 45.0,
            "predicted_penalty_usd": 0.0
        },
        {
            "shipment_id": "SHIP-002",
            "assigned_option_id": "OPT-C",
            "predicted_delay_days": 0,
            "actual_delay_days": 0,
            "realized_penalty_usd": 0.0,
            "predicted_penalty_usd": 0.0
        }
    ]
    validate_writeback_batch(sample_batch)
    print("=== [M4 Track] Day 22: App Team Write-back Schema Validation Passed Successfully ===")