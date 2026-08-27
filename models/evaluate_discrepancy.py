import pandas as pd
import numpy as np
import json
import os

OUTCOMES_PATH = os.path.join("data", "processed", "logged_outcomes.csv")
REPORT_PATH = os.path.join("notebooks", "evaluation_reports", "discrepancy_metrics.json")

def calculate_discrepancy_metrics():
    if not os.path.exists(OUTCOMES_PATH):
        raise FileNotFoundError(f"Logged outcomes file not found at {OUTCOMES_PATH}. Run simulate_outcomes.py first.")

    df = pd.read_csv(OUTCOMES_PATH)
    print("--- Starting Closed-Loop Discrepancy Evaluation ---")
    print(f"Analyzing {len(df):,} logged shipment outcomes...")

    # 1. Cost Discrepancy Calculations
    # Positive delta means incurred cost was higher than predicted/prescribed
    df['cost_discrepancy_usd'] = df['actual_incurred_cost_usd'] - df['expected_option_cost_usd']
    df['cost_error_pct'] = (np.abs(df['cost_discrepancy_usd']) / df['expected_option_cost_usd']) * 100

    # 2. Delay Days Discrepancy Calculations
    # Positive delta means real delivery arrived later than expected post-mitigation
    df['delay_discrepancy_days'] = df['actual_delivered_delay_days'] - df['expected_option_delay_days']
    df['delay_underestimated'] = (df['delay_discrepancy_days'] > 0).astype(int)

    # 3. Aggregate Statistical Metrics
    mean_cost_error_usd = float(df['cost_discrepancy_usd'].mean())
    mae_cost_usd = float(np.abs(df['cost_discrepancy_usd']).mean())
    mean_cost_error_pct = float(df['cost_error_pct'].mean())

    mean_delay_error_days = float(df['delay_discrepancy_days'].mean())
    mae_delay_days = float(np.abs(df['delay_discrepancy_days']).mean())
    underestimated_delay_rate = float(df['delay_underestimated'].mean()) * 100

    metrics_summary = {
        "total_evaluated_shipments": len(df),
        "cost_metrics": {
            "mean_cost_discrepancy_usd": round(mean_cost_error_usd, 2),
            "mean_absolute_error_cost_usd": round(mae_cost_usd, 2),
            "mean_cost_percentage_error": round(mean_cost_error_pct, 2)
        },
        "delay_metrics": {
            "mean_delay_discrepancy_days": round(mean_delay_error_days, 2),
            "mean_absolute_error_delay_days": round(mae_delay_days, 2),
            "underestimated_delay_frequency_pct": round(underestimated_delay_rate, 2)
        },
        "breakdown_by_option": df.groupby("selected_option_name").agg(
            total_cases=("shipment_id", "count"),
            avg_cost_delta_usd=("cost_discrepancy_usd", "mean"),
            avg_delay_delta_days=("delay_discrepancy_days", "mean")
        ).round(2).to_dict(orient="index")
    }

    # 4. Save and Print Results
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(metrics_summary, f, indent=4)

    print("\n--- Evaluation Summary ---")
    print(f"Cost MAE:               ${mae_cost_usd:.2f} ({mean_cost_error_pct:.2f}% avg error)")
    print(f"Delay Duration MAE:     {mae_delay_days:.2f} Days")
    print(f"Delay Underestimate %:  {underestimated_delay_rate:.1f}% of orders")
    print(f"\nSaved metrics summary to: {REPORT_PATH}")

if __name__ == "__main__":
    calculate_discrepancy_metrics()

