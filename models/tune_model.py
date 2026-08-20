import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import json
import os

TRAIN_PATH = os.path.join("data", "processed", "train.csv")
TEST_PATH = os.path.join("data", "processed", "test.csv")
MODEL_OUTPUT = os.path.join("models", "improved_xgboost.json")
REPORT_DIR = os.path.join("notebooks", "evaluation_reports")

def tune_and_analyze_features():
    if not os.path.exists(TRAIN_PATH) or not os.path.exists(TEST_PATH):
        raise FileNotFoundError("Processed datasets not found. Run feature_engineering.py first.")

    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    target_col = 'is_delayed' if 'is_delayed' in train_df.columns else 'late_delivery_risk'
    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]
    X_test = test_df.drop(columns=[target_col])
    y_test = test_df[target_col]

    print("--- Training Tuned XGBoost Model ---")
    
    # Tuned hyperparameters (increased tree depth, regularization, subsampling)
    tuned_model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=0.2,
        random_state=42,
        eval_metric='logloss'
    )

    tuned_model.fit(X_train, y_train)

    # 1. Feature Importance Analysis
    importance = tuned_model.feature_importances_
    features = X_train.columns
    feat_df = pd.DataFrame({'feature': features, 'importance': importance}).sort_values('importance', ascending=False)

    print("\n--- Feature Importance Rankings ---")
    print(feat_df.to_string(index=False))

    # Plot Feature Importance
    os.makedirs(REPORT_DIR, exist_ok=True)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=feat_df, x='importance', y='feature', palette='viridis')
    plt.title('XGBoost Delay Prediction - Feature Importance')
    plt.xlabel('Normalized Importance Score')
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "feature_importance.png"))
    plt.close()

    # 2. Evaluation
    y_pred = tuned_model.predict(X_test)
    y_proba = tuned_model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_proba)

    print("\n--- Tuned Model Metrics ---")
    print(f"Improved Accuracy: {acc * 100:.2f}%")
    print(f"Improved ROC-AUC:  {roc:.4f}")
    print("\n" + classification_report(y_test, y_pred, target_names=['On-Time', 'Delayed']))

    # 3. Save Model Artifact
    tuned_model.save_model(MODEL_OUTPUT)
    print(f"Tuned model artifact saved to: {MODEL_OUTPUT}")

if __name__ == "__main__":
    tune_and_analyze_features()

