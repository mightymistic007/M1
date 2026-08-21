import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, cross_validate
import json
import os

TRAIN_PATH = os.path.join("data", "processed", "train.csv")
REPORT_PATH = os.path.join("notebooks", "evaluation_reports", "cv_metrics.json")

def perform_cross_validation():
    if not os.path.exists(TRAIN_PATH):
        raise FileNotFoundError("Train data not found. Run feature_engineering.py first.")

    print("--- Starting 5-Fold Stratified Cross-Validation ---")
    train_df = pd.read_csv(TRAIN_PATH)
    
    target_col = 'is_delayed' if 'is_delayed' in train_df.columns else 'late_delivery_risk'
    X = train_df.drop(columns=[target_col])
    y = train_df[target_col]

    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )

    scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    cv_results = cross_validate(model, X, y, cv=skf, scoring=scoring, return_train_score=False)

    summary = {
        "k_folds": 5,
        "mean_accuracy": float(np.mean(cv_results['test_accuracy'])),
        "std_accuracy": float(np.std(cv_results['test_accuracy'])),
        "mean_f1": float(np.mean(cv_results['test_f1'])),
        "mean_roc_auc": float(np.mean(cv_results['test_roc_auc'])),
        "fold_accuracies": [float(score) for score in cv_results['test_accuracy']]
    }

    print("\n--- Cross-Validation Results ---")
    print(f"Mean Accuracy: {summary['mean_accuracy'] * 100:.2f}% (+/- {summary['std_accuracy'] * 100:.2f}%)")
    print(f"Mean F1-Score: {summary['mean_f1'] * 100:.2f}%")
    print(f"Mean ROC-AUC:  {summary['mean_roc_auc']:.4f}")

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, 'w') as f:
        json.dump(summary, f, indent=4)
        
    print(f"\nSaved cross-validation logs to: {REPORT_PATH}")

if __name__ == "__main__":
    perform_cross_validation()

