import pandas as pd
import numpy as np
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from models.pipeline import SupplyChainPipeline
    from models.prescriptive_solver import PrescriptiveSolver
except ModuleNotFoundError:
    from pipeline import SupplyChainPipeline
    from prescriptive_solver import PrescriptiveSolver

OUTPUT_DIR = os.path.join("data", "processed")
OUTCOMES_PATH = os.path.join(OUTPUT_DIR, "logged_outcomes.csv")

def simulate_logged_outcomes(num_samples: int = 200):
    """
    Simulates operational write-back telemetry:
    Logs predicted risk, operator decision choice, actual incurred cost, and real transit days.
    """
    test_path = os.path.join(OUTPUT_DIR, "test.csv")
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Test dataset not found at {test_path}")

    test_df = pd.read_csv(test_path).head(num_samples)
    pipeline = SupplyChainPipeline()
    solver = PrescriptiveSolver()

    predictions = pipeline.predict_delay_risk(test_df)
    logged_records = []

    np.random.seed(42)

    for pred in predictions:
        solution = solver.solve_shipment(pred)
        options = solution["prescribed_options"]

        # Operator decision simulation:
        # High delay risk (>0.7) -> Choose Air Freight (OPT-A) or Alternate Supplier (OPT-B)
        # Low delay risk -> Choose Standard / Accept (OPT-C)
        if pred["predicted_delay_risk"] > 0.7:
            chosen_opt = np.random.choice(options[:2])
        else:
            chosen_opt = options[2]

        # Simulate real-world operational variance/noise (unforeseen weather, customs, minor variance)
        real_world_noise_days = np.random.choice([-1, 0, 1, 2], p=[0.2, 0.5, 0.2, 0.1])
        actual_delay_days = max(0, chosen_opt["final_estimated_delay"] + real_world_noise_days)
        actual_total_cost = round(chosen_opt["cost_usd"] * np.random.uniform(0.98, 1.05), 2)

        logged_entry = {
            "shipment_id": pred["shipment_id"],
            "base_order_value_usd": pred["order_value_usd"],
            "predicted_delay_risk": pred["predicted_delay_risk"],
            "predicted_delay_days": pred["estimated_delay_days"],
            "selected_option_id": chosen_opt["option_id"],
            "selected_option_name": chosen_opt["name"],
            "expected_option_cost_usd": chosen_opt["cost_usd"],
            "expected_option_delay_days": chosen_opt["final_estimated_delay"],
            "actual_incurred_cost_usd": actual_total_cost,
            "actual_delivered_delay_days": actual_delay_days,
            "outcome_logged_timestamp": "2026-08-25T14:30:00Z"
        }
        logged_records.append(logged_entry)

    outcomes_df = pd.DataFrame(logged_records)
    outcomes_df.to_csv(OUTCOMES_PATH, index=False)

    print(f"--- Logged Operational Outcomes Simulated ---")
    print(f"Total Outcomes Recorded: {len(outcomes_df)}")
    print(f"Columns: {list(outcomes_df.columns)}")
    print(f"Saved to: {OUTCOMES_PATH}")

if __name__ == "__main__":
    simulate_logged_outcomes()
    
