import pandas as pd
import numpy as np
import xgboost as xgb
import json
import os

MODEL_PATH = os.path.join("models", "improved_xgboost.json")
CONFIG_PATH = os.path.join("data", "processed", "solver_constraints_config.json")

class SupplyChainPipeline:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model artifact not found at {MODEL_PATH}")
        self.model = xgb.XGBClassifier()
        self.model.load_model(MODEL_PATH)
        
        with open(CONFIG_PATH, "r") as f:
            self.config = json.load(f)

    def predict_delay_risk(self, sample_df: pd.DataFrame) -> list:
        """Takes a DataFrame of shipment records and formats input for the optimization solver."""
        # Ensure correct column order matching the training dataset
        feature_cols = [
            'shipping_mode', 'type', 'market', 'order_region',
            'customer_segment', 'category_name', 'days_for_shipment_scheduled',
            'order_item_quantity', 'order_item_product_price', 'sales'
        ]
        
        # Keep features present in sample
        X = sample_df[feature_cols].copy()
        
        probs = self.model.predict_proba(X)[:, 1]
        preds = self.model.predict(X)

        solver_inputs = []
        for idx, row in sample_df.iterrows():
            is_delayed = bool(preds[idx])
            delay_prob = float(probs[idx])
            
            # Estimate expected delay days based on probability and max historical window
            estimated_delay_days = round(delay_prob * self.config["max_historical_delay_days"]) if is_delayed else 0

            solver_input = {
                "shipment_id": row.get("order_item_id", f"SHIP-{idx+1000}"),
                "order_value_usd": float(row.get("sales", self.config["budget_baseline_usd"])),
                "scheduled_days": int(row.get("days_for_shipment_scheduled", 3)),
                "predicted_delay_risk": delay_prob,
                "is_delayed_prediction": is_delayed,
                "estimated_delay_days": estimated_delay_days
            }
            solver_inputs.append(solver_input)

        return solver_inputs

if __name__ == "__main__":
    TEST_PATH = os.path.join("data", "processed", "test.csv")
    test_df = pd.read_csv(TEST_PATH).head(5)
    
    pipeline = SupplyChainPipeline()
    results = pipeline.predict_delay_risk(test_df)
    
    print("--- Model-to-Solver Pipeline Output (Sample 5 Records) ---")
    print(json.dumps(results, indent=2))

