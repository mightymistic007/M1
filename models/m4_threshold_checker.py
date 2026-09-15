import os
import sys
import json
import pandas as pd
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class M4ThresholdChecker:
    def __init__(
        self,
        delay_discrepancy_limit: int = 2,
        discrepancy_rate_threshold: float = 0.15,
        false_negative_threshold: float = 0.05,
        cost_drift_threshold: float = 0.20
    ):
        self.delay_discrepancy_limit = delay_discrepancy_limit
        self.discrepancy_rate_threshold = discrepancy_rate_threshold
        self.false_negative_threshold = false_negative_threshold
        self.cost_drift_threshold = cost_drift_threshold

    def evaluate_outcomes(self, outcomes_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluates a batch of delivered shipments with predicted vs. actual outcomes.
        Expected columns:
          - shipment_id
          - predicted_delay_days
          - actual_delay_days
          - predicted_delay_risk (optional, 0.0 - 1.0)
          - realized_penalty_usd (optional)
          - predicted_penalty_usd (optional)
        """
        if outcomes_df.empty:
            return {
                "total_records": 0,
                "discrepant_count": 0,
                "discrepancy_rate": 0.0,
                "false_negative_count": 0,
                "false_negative_rate": 0.0,
                "cost_drift_rate": 0.0,
                "retrain_triggered": False,
                "trigger_reasons": []
            }

        total_records = len(outcomes_df)
        
        # 1. Delay duration discrepancy: |actual - predicted| >= threshold
        delay_diff = (outcomes_df["actual_delay_days"] - outcomes_df["predicted_delay_days"]).abs()
        discrepant_mask = delay_diff >= self.delay_discrepancy_limit
        discrepant_count = int(discrepant_mask.sum())
        discrepancy_rate = round(discrepant_count / total_records, 4)

        # 2. Severe false negative check (predicted <= 1 day, actual >= 3 days)
        fn_mask = (outcomes_df["predicted_delay_days"] <= 1) & (outcomes_df["actual_delay_days"] >= 3)
        fn_count = int(fn_mask.sum())
        fn_rate = round(fn_count / total_records, 4)

        # 3. Penalty / cost drift check (if penalty columns provided)
        cost_drift_rate = 0.0
        if "realized_penalty_usd" in outcomes_df.columns and "predicted_penalty_usd" in outcomes_df.columns:
            sum_pred = outcomes_df["predicted_penalty_usd"].sum()
            sum_real = outcomes_df["realized_penalty_usd"].sum()
            if sum_pred > 0:
                cost_drift_rate = round(float((sum_real - sum_pred) / sum_pred), 4)

        trigger_reasons = []
        if discrepancy_rate >= self.discrepancy_rate_threshold:
            trigger_reasons.append(
                f"Discrepancy rate ({discrepancy_rate * 100:.1f}%) exceeds threshold ({self.discrepancy_rate_threshold * 100:.1f}%)"
            )

        if fn_rate >= self.false_negative_threshold:
            trigger_reasons.append(
                f"Severe false negative rate ({fn_rate * 100:.1f}%) exceeds threshold ({self.false_negative_threshold * 100:.1f}%)"
            )

        if cost_drift_rate >= self.cost_drift_threshold:
            trigger_reasons.append(
                f"Realized cost drift ({cost_drift_rate * 100:.1f}%) exceeds threshold ({self.cost_drift_threshold * 100:.1f}%)"
            )

        retrain_triggered = len(trigger_reasons) > 0

        return {
            "total_records": total_records,
            "discrepant_count": discrepant_count,
            "discrepancy_rate": discrepancy_rate,
            "false_negative_count": fn_count,
            "false_negative_rate": fn_rate,
            "cost_drift_rate": cost_drift_rate,
            "retrain_triggered": retrain_triggered,
            "trigger_reasons": trigger_reasons
        }