
# M4 Track — Day 1: Constraints Specification & Objective Outline

## 1. M4 Role & Objective

Integration, mathematical constraint formulation, and testing between the XGBoost predictive model and prescriptive optimization engine.

## 2. Core Constraints to Model

* **Budget Limit**: Baseline order benchmark is $203.77, with a hard shipment budget cap of $399.98.
* **Delivery Deadlines**: Standard delivery average is 2.9 days; maximum allowable delivery window is 4 days.
* **Disruption Baseline**: Maximum historical delay window ceiling is 6 days.
* **Carrier Capacity**:
  * Option A (Air Freight Expedited): Max 20% of concurrent shipment volume (1.45x cost, up to 4 days saved).
  * Option B (Alternate Supplier): Max 35% of concurrent shipment volume (1.15x cost, up to 2 days saved).
  * Option C (Standard Delay Acceptance): Unconstrained baseline (1.0x cost, 0 days saved).

## 3. Downstream JSON Contract

Preserve the schema of `app_contract_sample.json`:

* `shipment_id`, `predicted_delay_risk`, `initial_delay_estimate_days`, and array of 3 `prescribed_options`.
