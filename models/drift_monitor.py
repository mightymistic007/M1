import json
import os

DISCREPANCY_PATH = os.path.join("notebooks", "evaluation_reports", "discrepancy_metrics.json")
DRIFT_STATUS_PATH = os.path.join("notebooks", "evaluation_reports", "drift_status.json")

# Tolerance Thresholds for Production Monitoring
THRESHOLDS = {
    "max_acceptable_delay_mae_days": 1.25,        # Trigger if delay MAE exceeds 1.25 days
    "max_acceptable_cost_pct_error": 6.0,          # Trigger if cost error exceeds 6.0%
    "max_acceptable_underestimate_rate_pct": 25.0  # Trigger if missed delays exceed 25%
}

def monitor_drift_and_evaluate_retraining():
    if not os.path.exists(DISCREPANCY_PATH):
        raise FileNotFoundError(f"Metrics file not found at {DISCREPANCY_PATH}. Run evaluate_discrepancy.py first.")

    with open(DISCREPANCY_PATH, "r") as f:
        metrics = json.load(f)

    print("--- Evaluating System Drift & Retraining Conditions ---")
    
    current_cost_pct = metrics["cost_metrics"]["mean_cost_percentage_error"]
    current_delay_mae = metrics["delay_metrics"]["mean_absolute_error_delay_days"]
    current_underestimate_rate = metrics["delay_metrics"]["underestimated_delay_frequency_pct"]

    # Evaluate against thresholds
    cost_drift_flag = current_cost_pct > THRESHOLDS["max_acceptable_cost_pct_error"]
    delay_drift_flag = current_delay_mae > THRESHOLDS["max_acceptable_delay_mae_days"]
    underestimate_flag = current_underestimate_rate > THRESHOLDS["max_acceptable_underestimate_rate_pct"]

    requires_retraining = cost_drift_flag or delay_drift_flag or underestimate_flag

    drift_report = {
        "timestamp_evaluated": "2026-08-28T10:00:00Z",
        "retraining_required": requires_retraining,
        "triggers_activated": {
            "cost_drift": cost_drift_flag,
            "delay_duration_drift": delay_drift_flag,
            "high_underestimate_frequency": underestimate_flag
        },
        "observed_metrics": {
            "cost_percentage_error": current_cost_pct,
            "delay_mae_days": current_delay_mae,
            "underestimated_delay_rate_pct": current_underestimate_rate
        },
        "thresholds_configured": THRESHOLDS,
        "recommended_action": "TRIGGER_AUTOMATED_RETRAIN" if requires_retraining else "MAINTAIN_CURRENT_MODEL"
    }

    os.makedirs(os.path.dirname(DRIFT_STATUS_PATH), exist_ok=True)
    with open(DRIFT_STATUS_PATH, "w") as f:
        json.dump(drift_report, f, indent=4)

    print(f"Cost Error:              {current_cost_pct:.2f}% (Limit: {THRESHOLDS['max_acceptable_cost_pct_error']}%) -> {'FAIL' if cost_drift_flag else 'PASS'}")
    print(f"Delay MAE:               {current_delay_mae:.2f} Days (Limit: {THRESHOLDS['max_acceptable_delay_mae_days']} Days) -> {'FAIL' if delay_drift_flag else 'PASS'}")
    print(f"Underestimate Rate:      {current_underestimate_rate:.2f}% (Limit: {THRESHOLDS['max_acceptable_underestimate_rate_pct']}%) -> {'FAIL' if underestimate_flag else 'PASS'}")
    print(f"\nSystem Retraining Status: {'[ACTION REQUIRED: RETRAIN]' if requires_retraining else '[STATUS OK: STABLE]'}")
    print(f"Saved drift status to: {DRIFT_STATUS_PATH}")

if __name__ == "__main__":
    monitor_drift_and_evaluate_retraining()

