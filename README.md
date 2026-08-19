# SupplyPrescript — ML & Optimization

## Sub-Role

**M1 — Data Sourcing & Cleaning**

## Objectives

- Sourcing and downloading raw supply chain data (e.g., DataCo Smart Supply Chain or synthetic data).
- Data cleaning, missing value handling, and data type formatting[cite: 2, 3].
- Supporting pipeline feature extraction and downstream model integration[cite: 2, 3].



### Week 1 Progress Summary (Aug 8 – Aug 15)[cite: 3]

* **Data Sourcing (Days 1–2)**: Integrated Kaggle DataCo Smart Supply Chain dataset (~180k records).
* **Data Cleaning (Day 3)**: Handled missing values, standardized schemas into snake_case, eliminated duplicates, and extracted target delay variables (`delay_days`, `is_delayed`).
* **EDA (Day 4)**: Analyzed delay distributions and correlated late deliveries against shipping modes and product categories[cite: 2, 3].
* **Feature Engineering (Day 5)**: Categorical encoding applied, producing 80/20 train/test stratified splits[cite: 2, 3].
* **Model Baseline & Evaluation (Days 6–7)**: Trained baseline XGBoost classifier achieving ~70% accuracy, ROC-AUC of 0.745, and logged confusion matrix weak-spot diagnostics[cite: 2, 3].

### Artifacts Created

* `data/processed/cleaned_supply_chain_data.csv`[cite: 2, 3]
* `data/processed/train.csv` & `test.csv`[cite: 2, 3]
* `models/baseline_xgboost.json`[cite: 2, 3]
* `notebooks/evaluation_reports/`[cite: 2, 3]
