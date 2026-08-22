
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
