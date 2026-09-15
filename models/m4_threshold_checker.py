import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class M4ThresholdChecker:
    def __init__(
        self,
        delay_discrepancy_limit: int = 2,
        discrepancy_rate_threshold: float = 0.15,
        false_negative_threshold: float = 0.05,
        cost_drift_threshold: float = 0.20,
        min_batch_size: int = 10,
        severe_delay_threshold: int = 4
    ):
        self.delay_discrepancy_limit = delay_discrepancy_limit
        self.discrepancy_rate_threshold = discrepancy_rate_threshold
        self.false_negative_threshold = false_negative_threshold
        self.cost_drift_threshold = cost_drift_threshold
        self.min_batch_size = min_batch_size
        self.severe_delay_threshold = severe_delay_threshold

    def evaluate_outcomes(self, outcomes_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluates batch actuals vs predictions with sample size guards and severity weighting.
        """
        if outcomes_df.empty:
            return self._empty_result()

        df = outcomes_df.copy()
        total_records = len(df)

        # Guard: If batch size is smaller than minimum required, log observation without false retrain triggers
        if total_records < self.min_batch_size:
            return {
                **self._empty_result(),
                "total_records": total_records,
                "status": f"INSUFFICIENT_SAMPLE_SIZE (requires >= {self.min_batch_size}, got {total_records})"
            }

        # 1. Absolute Delay Discrepancy
        delay_diff = (df["actual_delay_days"] - df["predicted_delay_days"]).abs()
        discrepant_mask = delay_diff >= self.delay_discrepancy_limit
        discrepant_count = int(discrepant_mask.sum())
        discrepancy_rate = round(discrepant_count / total_records, 4)

        # 2. Critical False Negatives (Predicted <= 1 day, Actual >= 3 days)
        fn_mask = (df["predicted_delay_days"] <= 1) & (df["actual_delay_days"] >= 3)
        fn_count = int(fn_mask.sum())
        fn_rate = round(fn_count / total_records, 4)

        # 3. Severe Disruptions (|Actual - Predicted| >= severe_delay_threshold)
        severe_mask = delay_diff >= self.severe_delay_threshold
        severe_count = int(severe_mask.sum())
        severe_rate = round(severe_count / total_records, 4)

        # 4. Mean Squared Delay Discrepancy (Quadratic drift severity)
        mean_squared_delay_error = round(float((delay_diff ** 2).mean()), 4)

        # 5. Financial Cost / Penalty Drift
        cost_drift_rate = 0.0
        if "realized_penalty_usd" in df.columns and "predicted_penalty_usd" in df.columns:
            sum_pred = df["predicted_penalty_usd"].sum()
            sum_real = df["realized_penalty_usd"].sum()
            if sum_pred > 0:
                cost_drift_rate = round(float((sum_real - sum_pred) / sum_pred), 4)

        # Determine trigger conditions
        trigger_reasons = []
        if discrepancy_rate >= self.discrepancy_rate_threshold:
            trigger_reasons.append(
                f"Discrepancy rate ({discrepancy_rate * 100:.1f}%) exceeds threshold ({self.discrepancy_rate_threshold * 100:.1f}%)"
            )

        if fn_rate >= self.false_negative_threshold:
            trigger_reasons.append(
                f"Severe false negative rate ({fn_rate * 100:.1f}%) exceeds threshold ({self.false_negative_threshold * 100:.1f}%)"
            )

        if severe_rate > 0.02:  # Over 2% extreme disruptions (>=4 days drift)
            trigger_reasons.append(
                f"Severe delay drift ({severe_rate * 100:.1f}%) exceeds 2% critical limit"
            )

        if cost_drift_rate >= self.cost_drift_threshold:
            trigger_reasons.append(
                f"Realized cost drift ({cost_drift_rate * 100:.1f}%) exceeds threshold ({self.cost_drift_threshold * 100:.1f}%)"
            )

        retrain_triggered = len(trigger_reasons) > 0

        # Audit trail IDs that failed
        failed_shipment_ids = []
        if "shipment_id" in df.columns:
            failed_shipment_ids = df[discrepant_mask | fn_mask]["shipment_id"].astype(str).tolist()

        return {
            "status": "EVALUATED",
            "total_records": total_records,
            "discrepant_count": discrepant_count,
            "discrepancy_rate": discrepancy_rate,
            "false_negative_count": fn_count,
            "false_negative_rate": fn_rate,
            "severe_disruption_count": severe_count,
            "mean_squared_delay_error": mean_squared_delay_error,
            "cost_drift_rate": cost_drift_rate,
            "retrain_triggered": retrain_triggered,
            "trigger_reasons": trigger_reasons,
            "discrepant_shipment_ids": failed_shipment_ids[:10]  # Cap top 10 for log brevity
        }

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "status": "EMPTY_INPUT",
            "total_records": 0,
            "discrepant_count": 0,
            "discrepancy_rate": 0.0,
            "false_negative_count": 0,
            "false_negative_rate": 0.0,
            "severe_disruption_count": 0,
            "mean_squared_delay_error": 0.0,
            "cost_drift_rate": 0.0,
            "retrain_triggered": False,
            "trigger_reasons": [],
            "discrepant_shipment_ids": []
        }
