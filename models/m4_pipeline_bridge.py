import os
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from typing import List, Dict, Any
from models.m4_optimization_solver import M4OptimizationSolver

MODEL_PATH = os.path.join(os.path.dirname(__file__), "improved_xgboost.json")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "solver_constraints_config.json")

class M4PipelineBridge:
    def __init__(self, model_path: str = MODEL_PATH, config_path: str = CONFIG_PATH):
        self.model = xgb.XGBClassifier()
        if os.path.exists(model_path):
            self.model.load_model(model_path)
        else:
            raise FileNotFoundError(f"Trained model artifact not found at {model_path}")
        
        self.solver = M4OptimizationSolver(config_path=config_path)
        self.max_delay_days = self.solver.config.get("max_historical_delay_days", 6)

    def predict_and_prescribe_batch(self, df_records: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Takes raw/preprocessed feature rows, generates delay probabilities with XGBoost,
        scales them to estimated delay days, and executes the M4 optimization solver.
        """
        if df_records.empty:
            return []

        df = df_records.copy()

        # Handle fallback for sales if missing
        if "sales" not in df.columns:
            if "order_item_product_price" in df.columns:
                qty = df["order_item_quantity"] if "order_item_quantity" in df.columns else 1
                df["sales"] = df["order_item_product_price"] * qty
            else:
                df["sales"] = self.solver.config.get("budget_baseline_usd", 203.77)

        # Standard required feature columns for the XGBoost model
        feature_cols = [
            "shipping_mode", "type", "market", "order_region", "customer_segment",
            "category_name", "days_for_shipment_scheduled", "order_item_quantity",
            "order_item_product_price", "sales"
        ]

        # Ensure all required features exist with sensible neutral defaults
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0

        X = df[feature_cols].copy()
        pred_probs = self.model.predict_proba(X)[:, 1]

        shipment_candidates = []
        for idx, (_, row) in enumerate(df.iterrows()):
            prob = float(pred_probs[idx])
            estimated_delay = int(round(prob * self.max_delay_days))
            order_val = float(row.get("sales", row.get("order_item_product_price", self.solver.config["budget_baseline_usd"])))
            ship_id = str(row.get("order_item_id", f"SHIP-M4-{idx+1:04d}"))

            shipment_candidates.append({
                "shipment_id": ship_id,
                "order_value_usd": order_val,
                "estimated_delay_days": estimated_delay,
                "predicted_delay_risk": round(prob, 4)
            })

        return self.solver.solve_batch(shipment_candidates)
