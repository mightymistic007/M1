
# M4 Track — Day 19: Model Retraining Pipeline Plan

## 1. Overview & Objectives

This document establishes the operational retraining strategy for the SupplyPrescript delay prediction model (XGBoost) and its integration with the downstream M4 prescriptive solver. It details execution steps, trigger events, execution frequency, and deployment verification gates.

---

## 2. Trigger Hierarchy

### A. Performance Drift Triggers (Automated via Threshold Checker)

* **Discrepancy Rate Violation**: Over $15\%$ of deliveries show $\vert{}D_{\text{actual}} - D_{\text{predicted}}\vert{} \ge 2\text{ days}$.
* **Severe False Negative Rate**: Over $5\%$ of deliveries predict $\le 1\text{ day}$ delay but experience $\ge 3\text{ days}$ delay.
* **Severe Disruption Surge**: Over $2\%$ of batch deliveries show $\ge 4\text{ days}$ of absolute drift.
* **Realized Cost Drift**: Average SLA breach penalty exceeds predicted baseline by $\ge 20\%$.

### B. Temporal Cadence (Scheduled Fallback)

* **Bi-Weekly Scheduled Retrain**: Evaluates new completed delivery logs every 14 calendar days regardless of drift status.
* **Data Volume Cadence**: Triggers automatically once $N \ge 1,000$ newly labeled shipment outcomes accumulate.

---

## 3. Pipeline Execution Stages

```text
[Shipment DB Actuals]
         │
         ▼
[Stage 1: Ingestion & Threshold Audit (m4_threshold_checker.py)]
         │
         ├──► Thresholds OK ──► Log telemetry; exit
         │
         └──► Trigger Tripped
                   │
                   ▼
[Stage 2: Dataset Aggregation & Feature Preprocessing]
                   │
                   ▼
[Stage 3: Incremental / Full XGBoost Training]
                   │
                   ▼
[Stage 4: Validation Gates & Regression Guardrails]
                   │
                   ├──► Failed Gate ──► Abort; alert ML team; retain active model
                   │
                   └──► Passed Gate
                             │
                             ▼
[Stage 5: Atomic Artifact Hot-Swap (improved_xgboost.json)]
                             │
                             ▼
[Stage 6: Solver Pipeline End-to-End Regression Audit]
```
