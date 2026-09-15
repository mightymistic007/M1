

# M4 Track — Day 23: Operational Guide — Closed-Loop Retraining Trigger

## 1. Overview

The Retraining Trigger Engine acts as an automated quality gate between incoming delivery actuals and model re-fitting. It guarantees that the XGBoost classifier is retrained only when real operational drift or critical delay errors exceed acceptable thresholds.

---

## 2. Trigger Conditions & Guardrails

| Metric Key                 | Operational Threshold | Description / Impact                                                                                                   |
| :------------------------- | :-------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| `min_batch_size`         | $\ge 10$ records    | Prevents erratic triggers on sparse micro-batches.                                                                     |
| `discrepancy_rate`       | $\ge 15.0\%$        | Tripped if$\ge 15\%$ of shipments have $\vert{}D_{\text{actual}} - D_{\text{predicted}}\vert{} \ge 2\text{ days}$. |
| `false_negative_rate`    | $\ge 5.0\%$         | High penalty: predicted$\le 1\text{ day}$ delay, but actual was $\ge 3\text{ days}$.                               |
| `severe_disruption_rate` | $> 2.0\%$           | Critical disruption:$\vert{}D_{\text{actual}} - D_{\text{predicted}}\vert{} \ge 4\text{ days}$.                      |
| `cost_drift_rate`        | $\ge 20.0\%$        | Realized customer SLA penalties exceed predicted penalty totals by$\ge 20\%$.                                        |

---

## 3. How to Run the Retraining Trigger

### A. Manual CLI Trigger Run

You can evaluate a CSV payload containing delivery actuals directly from the terminal:

```bash
python models/m4_retrain_trigger_runner.py --input-csv data/processed/sample_outcomes.csv


```



### B. Automated Programmatic Invocation

```python
from models.m4_retrain_trigger_runner import run_retraining_pipeline_eval

decision = run_retraining_pipeline_eval(outcomes_df)
if decision["retrain_initiated"]:
    print("New model training workflow launched.")
```
