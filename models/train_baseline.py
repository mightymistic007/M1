import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
import joblib
import os

TRAIN_PATH = os.path.join("data", "processed", "train.csv")
TEST_PATH = os.path.join("data", "processed", "test.csv")
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "baseline_xgboost.json")

def train_baseline_model():
    if not os.path.exists(TRAIN_PATH) or not os.path.exists(TEST_PATH):
        raise FileNotFoundError("Train or Test data not found. Please run feature_engineering.py first.")

    print("--- Loading Processed Datasets ---")
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    # Determine target column
    target_col = 'is_delayed' if 'is_delayed' in train_df.columns else 'late_delivery_risk'

    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]

    X_test = test_df.drop(columns=[target_col])
    y_test = test_df[target_col]

    print(f"Features: {list(X_train.columns)}")
    print(f"Training on {X_train.shape[0]:,} samples, validating on {X_test.shape[0]:,} samples...")

    # 1. Initialize Baseline XGBoost Classifier
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False
    )

    # 2. Train the model
    print("\n--- Training XGBoost Baseline Model ---")
    model.fit(X_train, y_train)

    # 3. Model Evaluation
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc = roc_auc_score(y_test, y_proba)

    print("\n--- Evaluation Metrics ---")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print(f"ROC-AUC:   {roc:.4f}")

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred))

    # 4. Save the trained model artifact
    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save_model(MODEL_PATH)
    print(f"Trained model artifact saved to: {MODEL_PATH}")

if __name__ == "__main__":
    train_baseline_model()