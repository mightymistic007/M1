import pandas as pd
import numpy as np
import json
import os

OUTCOMES_PATH = os.path.join("data", "processed", "logged_outcomes.csv")
ROI_REPORT_PATH = os.path.join("notebooks", "evaluation_reports", "decision_roi_summary.json")

# Business penalty and buffer value assumptions
LATE_DELIVERY_PENALTY_PER_DAY_USD = 45.00  # Cost incurred per unmitigated late day (SLA breaches, churn risk)

def calculate_decision_roi():
    if not os.path.exists(OUTCOMES_PATH):
        raise FileNotFoundError(f"Logged outcomes file not found at {OUTCOMES_PATH}. Run simulate_outcomes.py first.")

    df = pd.read_csv(OUTCOMES_PATH)
    print("--- Calculating Decision ROI & Value Added ---")
    print(f"Evaluating ROI on {len(df):,} executed decisions...")

    # 1. Calculate Days Saved by Prescriptions
    # Days saved = Unmitigated predicted delay days - Actual delivered delay days
    df['delay_days_prevented'] = np.maximum(0, df['predicted_delay_days'] - df['actual_delivered_delay_days'])

    # 2. Financial Value Calculations
    # Gross penalty avoided
    df['penalty_cost_avoided_usd'] = df['delay_days_prevented'] * LATE_DELIVERY_PENALTY_PER_DAY_USD

    # Net extra cost spent on mitigation (Expedite/Alt supplier surcharge)
    df['mitigation_cost_spent_usd'] = np.maximum(0.0, df['actual_incurred_cost_usd'] - df['base_order_value_usd'])

    # Net ROI per shipment
    df['net_value_generated_usd'] = df['penalty_cost_avoided_usd'] - df['mitigation_cost_spent_usd']

    # 3. Overall Aggregate Metrics
    total_spent_mitigation = float(df['mitigation_cost_spent_usd'].sum())
    total_penalties_avoided = float(df['penalty_cost_avoided_usd'].sum())
    net_savings = float(df['net_value_generated_usd'].sum())
    total_days_prevented = int(df['delay_days_prevented'].sum())
    
    # Overall ROI percentage: (Net Value / Investment) * 100
    overall_roi_pct = round((net_savings / total_spent_mitigation * 100), 2) if total_spent_mitigation > 0 else 0.0

    roi_summary = {
        "summary_window": "Week 3 - Closed Loop Evaluation",
        "total_shipments_analyzed": len(df),
        "total_delay_days_prevented": total_days_prevented,
        "financial_summary": {
            "total_mitigation_cost_spent_usd": round(total_spent_mitigation, 2),
            "total_penalties_avoided_usd": round(total_penalties_avoided, 2),
            "net_business_savings_usd": round(net_savings, 2),
            "decision_roi_percentage": overall_roi_pct
        },
        "breakdown_by_option": df.groupby("selected_option_name").agg(
            total_orders=("shipment_id", "count"),
            days_saved=("delay_days_prevented", "sum"),
            mitigation_spend=("mitigation_cost_spent_usd", "sum"),
            net_savings=("net_value_generated_usd", "sum")
        ).round(2).to_dict(orient="index")
    }

    os.makedirs(os.path.dirname(ROI_REPORT_PATH), exist_ok=True)
    with open(ROI_REPORT_PATH, "w") as f:
        json.dump(roi_summary, f, indent=4)

    print("\n--- Decision ROI Results ---")
    print(f"Total Delay Days Prevented: {total_days_prevented:,} Days")
    print(f"Mitigation Surcharges Paid:  ${total_spent_mitigation:,.2f}")
    print(f"Late Penalties Avoided:      ${total_penalties_avoided:,.2f}")
    print(f"Net Value Generated:         ${net_savings:,.2f}")
    print(f"Overall Decision ROI:        {overall_roi_pct}%")
    print(f"\nSaved ROI summary to: {ROI_REPORT_PATH}")

if __name__ == "__main__":
    calculate_decision_roi()

