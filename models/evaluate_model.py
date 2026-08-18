import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import os

TEST_PATH = os.path.join("data", "processed", "test.csv")
MODEL_PATH = os.path.join("models", "baseline_xgboost.json")
REPORT_DIR = os.path.join("notebooks", "evaluation_reports")

def evaluate_and_diagnose():
    if not os.path.exists(TEST_PATH) or not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Missing test.csv or baseline_xgboost.json. Run previous steps first.")

    os.makedirs(REPORT_DIR, exist_ok=True)
    test_df = pd.read_csv(TEST_PATH)
    
    target_col = 'is_delayed' if 'is_delayed' in test_df.columns else 'late_delivery_risk'
    X_test = test_df.drop(columns=[target_col])
    y_test = test_df[target_col]

    # Load trained model
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)

    # Predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # 1. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['On-Time (0)', 'Delayed (1)'],
                yticklabels=['On-Time (0)', 'Delayed (1)'])
    plt.title('Baseline Model - Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('Actual Label')
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "confusion_matrix.png"))
    plt.close()

    # 2. ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC)')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "roc_curve.png"))
    plt.close()

    # 3. Weak-Spot Error Analysis
    test_df['predicted'] = y_pred
    test_df['error'] = (test_df['predicted'] != y_test).astype(int)
    
    print("--- Detailed Evaluation Summary ---")
    print(classification_report(y_test, y_pred, target_names=['On-Time', 'Delayed']))
    print(f"Total Test Samples: {len(test_df):,}")
    print(f"False Negatives (Missed Delays): {cm[1][0]:,}")
    print(f"False Positives (False Alarms): {cm[0][1]:,}")
    print(f"Reports & plots saved to: {REPORT_DIR}")

if __name__ == "__main__":
    evaluate_and_diagnose()

