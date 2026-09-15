import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "test.csv")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "solver_constraints_config.json")

def extract_ranges():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Processed test data not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    
    # Calculate real data distributions
    cost_col = "sales" if "sales" in df.columns else "order_item_product_price"
    delay_sched_col = "days_for_shipment_scheduled"

    stats = {
        "cost_min": float(df[cost_col].min()),
        "cost_p25": float(df[cost_col].quantile(0.25)),
        "cost_median": float(df[cost_col].median()),
        "cost_p75": float(df[cost_col].quantile(0.75)),
        "cost_p95": float(df[cost_col].quantile(0.95)),
        "cost_max": float(df[cost_col].max()),
        "scheduled_days_avg": float(df[delay_sched_col].mean()) if delay_sched_col in df.columns else 2.9,
        "sample_size": int(len(df))
    }

    print("=== [M4 Track] Real Dataset Operational Statistics ===")
    for k, v in stats.items():
        print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")

    # Ensure constraints config records the verified 95th percentile budget cap
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        config["real_data_ranges"] = stats
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Updated {CONFIG_PATH} with real data ranges.")

if __name__ == "__main__":
    extract_ranges()
