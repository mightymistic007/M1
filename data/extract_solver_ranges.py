import pandas as pd
import json
import os

PROCESSED_DATA_PATH = os.path.join("data", "processed", "cleaned_supply_chain_data.csv")
OUTPUT_PATH = os.path.join("data", "processed", "solver_constraints_config.json")

def extract_solver_ranges():
    if not os.path.exists(PROCESSED_DATA_PATH):
        raise FileNotFoundError("Cleaned dataset not found. Run clean_data.py first.")

    df = pd.read_csv(PROCESSED_DATA_PATH)
    print("--- Extracting Numeric Ranges for Solver Constraints ---")

    # 1. Cost and price bounds
    avg_order_value = float(df['sales'].mean())
    max_order_value = float(df['sales'].quantile(0.95))
    avg_item_price = float(df['order_item_product_price'].mean())
    
    # 2. Shipping durations (Days)
    avg_scheduled_days = float(df['days_for_shipment_scheduled'].mean())
    max_scheduled_days = int(df['days_for_shipment_scheduled'].max())
    avg_real_days = float(df['days_for_shipping_real'].mean())
    max_real_days = int(df['days_for_shipping_real'].max())

    # 3. Solver Parameter Config
    # Used by the LP formulation for option trade-offs (Airfreight, Alt Supplier, Delay Launch)
    solver_config = {
        "budget_baseline_usd": round(avg_order_value, 2),
        "budget_max_cap_usd": round(max_order_value, 2),
        "average_item_price_usd": round(avg_item_price, 2),
        "scheduled_delivery_avg_days": round(avg_scheduled_days, 1),
        "max_shipping_window_days": max_scheduled_days,
        "max_historical_delay_days": max_real_days,
        "prescriptive_options": {
            "air_freight": {
                "expedite_cost_multiplier": 1.45,
                "days_saved": 4
            },
            "alternate_supplier": {
                "cost_premium_rate": 1.15,
                "days_saved": 2
            },
            "standard_delay": {
                "cost_premium_rate": 1.00,
                "days_saved": 0
            }
        }
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(solver_config, f, indent=4)

    print(f"Extracted config successfully:")
    print(json.dumps(solver_config, indent=2))
    print(f"\nSaved config to: {OUTPUT_PATH}")

if __name__ == "__main__":
    extract_solver_ranges()


