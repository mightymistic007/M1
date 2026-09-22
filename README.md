
# SupplyPrescript — ML & Optimization Engine

## Role

**M1 — Data Sourcing, Cleaning & Pipeline Engineering**

## Objectives

* Sourcing and downloading raw supply chain data (Kaggle DataCo Smart Supply Chain dataset).
* Data cleaning, handling missing values, standardizing schemas, and data type formatting.
* Feature engineering, categorical encoding, and stratified dataset partitioning.
* Constructing model-to-solver inference pipelines and defining API contract schemas.

---

## Progress Summary

### Week 1 — Foundation: Data & Baseline Model (Aug 8 – Aug 15)

* **Days 1–2 (Data Sourcing & Ingestion)**: Integrated the Kaggle DataCo Smart Supply Chain dataset (~180k records) and verified raw schema integrity.
* **Day 3 (Data Cleaning)**: Handled missing values, deduplicated records, standardized column names to snake_case, and calculated target variables (`delay_days`, `is_delayed`).
* **Day 4 (Exploratory Data Analysis)**: Analyzed delay distributions, producing visual reports across shipping modes and product categories.
* **Day 5 (Feature Engineering)**: Encoded categorical features and generated stratified 80/20 train/test splits.
* **Days 6–7 (Model Baseline & Evaluation)**: Trained a baseline XGBoost classifier achieving ~70% accuracy and 0.745 ROC-AUC; diagnosed false positive/negative distributions via confusion matrix.
* **Day 8 (Week 1 Wrap-up)**: Consolidated data documentation and merged the baseline foundation.

### Week 2 — Constraints, Solver & Ranked Options (Aug 16 – Aug 22)

* **Day 9 (Numeric Range Extraction)**: Extracted real-world numeric bounds (costs, delivery windows, expedite multipliers) into `solver_constraints_config.json`.
* **Day 10 (Model Improvement & Feature Importance)**: Tuned XGBoost hyperparameters and generated feature importance rankings highlighting shipping mode and scheduled shipment days as primary drivers.
* **Day 11 (Cross-Validation)**: Executed 5-fold stratified cross-validation confirming model stability across folds (Mean Accuracy: ~69.83%, Mean ROC-AUC: ~0.7469).
* **Day 12 (Model-to-Solver Pipeline)**: Implemented `SupplyChainPipeline` to transform raw shipment records into structured delay risk predictions.
* **Day 13 (Prescriptive Solver & JSON Contract)**: Built `PrescriptiveSolver` generating 3 ranked actions (Air Freight, Alternate Supplier, Delay Acceptance) matching the Application Team JSON schema contract.
* **Day 14 (Testing & Validation)**: Created and validated an automated unit test suite (`tests/test_pipeline.py`) verifying inference, option generation, and constraint bounds.
* **Day 15 (Mid Review Preparation)**: Packaged the full pipeline end-to-end for the Mid Review milestone.
  
### Week 3 — Retraining Pipeline Architecture & Telemetry Drift Logic (Aug 23 – Aug 29)

* **Day 16 (Telemetry Ingestion & Retraining Architecture)**: Designed the automated retraining workflow, defining schema contracts for ingesting downstream delivery actuals and setting up candidate model evaluation protocols.
* **Day 17 (Performance Drift Monitoring)**: Built the drift detection logic to evaluate operational discrepancy rates ($\vert{}D_{\text{actual}} - D_{\text{predicted}}\vert{} \ge 2\text{ days}$) and flag critical false negatives on high-penalty delays.
* **Day 18 (Retraining Trigger Orchestrator)**: Implemented the automated pipeline trigger skeleton to handle data ingestion, feature re-engineering, and candidate model re-fitting workflows.
* **Day 19 (Unit Testing Retrain Triggers)**: Constructed automated test suites verifying model drift trip thresholds, boundary conditions, and telemetry payload validation.
* **Day 20 (Drift Diagnostics & Edge Cases)**: Built diagnostic tools to inspect delivery variance distributions, identify systematic prediction skew, and isolate root causes for delay misclassifications.
* **Day 21 (Data Aggregation & Integration Harness)**: Tested the end-to-end data feedback pipeline, validating that accumulated historical telemetry seamlessly combines with new delivery actuals.
* **Day 22 (Outcome Write-Back Contract Sync)**: Validated write-back schemas to guarantee that operational telemetry delivered by downstream services strictly complies with feature pipeline expectations.

### Week 4 — Automated Pipeline Testing, Promotion Gates & Production Packaging (Aug 30 – Sep 5)

* **Day 23 (Production Retraining Trigger Runner)**: Implemented the execution engine and CLI interface to trigger automated model retraining based on incoming batch telemetry.
* **Day 24 (End-to-End Retraining Test)**: Executed and verified the full retraining loop end-to-end—from live telemetry ingestion and drift detection to candidate model fitting and gate evaluation.
* **Day 25 (Data Pipeline Sanitization & Hardening)**: Hardened preprocessing pipelines against dirty inputs, malformed types, missing fields, and out-of-range numerical values.
* **Day 26 (Inference Latency & Batch Throughput Stress-Testing)**: Benchmarked batch inference throughput and execution latency across micro ($N=10$) and large ($N=500$) evaluation payloads.
* **Day 27 (Continuous Retraining Documentation)**: Authored comprehensive documentation detailing continuous learning architecture, trigger criteria, and model governance lifecycles.
* **Day 28 (End-to-End Pipeline Integration Verification)**: Led integration tests coordinating model predictions, feature engineering, and closed-loop feedback triggers.
* **Day 29 (Final Review & Repository Consolidation)**: Compiled technical presentation dossiers, verified all test suites passed cleanly, and finalized code consolidation into `main`.

* ### Week 3 — Closed-Loop Design & Retraining Trigger Logic (Aug 23 – Aug 29)

* **Days 16–17 (Retraining Architecture & Trigger Specifications)**: Designed the closed-loop retraining pipeline criteria, establishing error thresholds for model drift (flagging batches where discrepancy rates exceed 15% or severe false negatives exceed 5%).
* **Days 18–19 (Trigger Implementation & Discrepancy Auditing)**: Built and verified the retraining trigger core logic to continuously evaluate realized delivery actuals against initial XGBoost predictions.
* **Days 20–21 (Pipeline Integration & Drift Verification)**: Implemented automated unit and integration tests asserting that edge-case prediction failures and operational drift correctly initiate the retraining sequence.
* **Day 22 (Write-Back Data Ingestion & Contract Alignment)**: Coordinated with downstream services to standardize the delivery telemetry write-back schema, ensuring actual delivery durations feed back into the retraining dataset without schema mismatches.
* **M4 Add-on Collaboration (Mathematical Constraints & Schema Specs)**:
  * Formulated the canonical LP objective function balancing carrier surcharges against SLA delay penalties ($45/day) under strict capacity limits (Option A $\le 20\%$, Option B $\le 35\%$).
  * Built `models/m4_threshold_checker.py` and `models/m4_retrain_trigger_skeleton.py` to operationalize batch drift auditing and candidate retraining gates.
  * Authored `docs/m4_json_schema_contract.md` and `docs/m4_app_writeback_schema_sync.md` to lock in JSON Draft-07 compliance with the Application Team.

### Week 4 — End-to-End Retraining, Production Hardening & Final Merge (Aug 30 – Sep 5)

* **Day 23 (Retraining Logic Finalization & Execution Guide)**: Completed the end-to-end retraining orchestration runner and documented operational execution flows for automated model updates.
* **Days 24–25 (Retraining Pipeline Testing & Edge-Case Hardening)**: Validated the end-to-end retraining flow (ingestion → evaluation → candidate model fitting → performance gate check), hardening feature pipelines against null or corrupt operational telemetry.
* **Day 26 (Performance & Scalability Benchmarking)**: Benchmarked inference latency and retraining data aggregation to verify stable execution under operational batch loads.
* **Day 27 (Continuous Retraining Documentation)**: Authored comprehensive technical documentation covering the end-to-end ML lifecycle, drift thresholds, and model promotion criteria.
* **Days 28–29 (Integration Testing & Final Review Consolidation)**: Executed full-loop integration tests with live-style telemetry payloads, verified test coverage across all suites, and merged the finalized pipeline into `main` for the final review milestone.
* **M4 Add-on Collaboration (HiGHS Solver Hardening & E2E Integration)**:
  * Hardened the prescriptive solver (`models/m4_optimization_solver.py`) against borderline $399.98 budget caps and defensive input sanitization (corrupt/null fields, zero-delay shipments).
  * Executed performance scaling benchmarks in `tests/m4_test_solver_performance.py`, proving sub-150ms execution times for stress batches of $N=500$ records.
  * Coordinated and delivered full-loop integration testing in `tests/m4_test_app_team_e2e_integration.py` and consolidated presentation materials in `docs/m4_final_review_presentation_materials.md`.
---

## Artifacts Created

* **Data Pipelines**: `data/load_data.py`, `data/clean_data.py`, `data/feature_engineering.py`, `data/extract_solver_ranges.py`
* **Datasets**: `data/processed/cleaned_supply_chain_data.csv`, `train.csv`, `test.csv`, `solver_constraints_config.json`
* **Models & Inference**: `models/train_baseline.py`, `models/tune_model.py`, `models/cross_validate.py`, `models/pipeline.py`, `models/prescriptive_solver.py`
* **Reports & Diagnostics**: `notebooks/plots/`, `notebooks/evaluation_reports/` (`confusion_matrix.png`, `roc_curve.png`, `feature_importance.png`, `cv_metrics.json`, `app_contract_sample.json`)
* **Test Suite**: `tests/test_pipeline.py`

---

## Running the Pipeline & Tests

```bash
# 1. Run full unit test suite
python -m unittest tests/test_pipeline.py

# 2. Run end-to-end model prediction to prescriptive solver execution
python models/prescriptive_solver.py
```
