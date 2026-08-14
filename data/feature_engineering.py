import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os

CLEAN_DATA_PATH = os.path.join("data", "processed", "cleaned_supply_chain_data.csv")
PROCESSED_DIR = os.path.join("data", "processed")

def engineer_features_and_split():
    if not os.path.exists(CLEAN_DATA_PATH):
        raise FileNotFoundError(f"Cleaned dataset not found at {CLEAN_DATA_PATH}. Run clean_data.py first.")

    print("--- Starting Feature Engineering Pipeline ---")
    df = pd.read_csv(CLEAN_DATA_PATH)
    print(f"Loaded {len(df):,} records.")

    # 1. Select relevant feature columns for delay prediction
    feature_cols = [
        'shipping_mode',
        'type',
        'market',
        'order_region',
        'customer_segment',
        'category_name',
        'days_for_shipment_scheduled',
        'order_item_quantity',
        'order_item_product_price',
        'sales'
    ]
    
    # Keep only available features
    available_features = [c for c in feature_cols if c in df.columns]
    
    # Target variable: 'is_delayed' (binary classification) or 'delay_days' (regression)
    target_col = 'is_delayed' if 'is_delayed' in df.columns else 'late_delivery_risk'
    
    X = df[available_features].copy()
    y = df[target_col].copy()

    # 2. Encode categorical variables using LabelEncoder
    label_encoders = {}
    cat_cols = X.select_dtypes(include=['object']).columns
    
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

    print(f"Transformed {len(cat_cols)} categorical columns into numeric encodings.")

    # 3. Train/Test Split (80% Train, 20% Test) with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Train Set Shape: {X_train.shape}")
    print(f"Test Set Shape: {X_test.shape}")

    # 4. Combine and save datasets
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)

    train_path = os.path.join(PROCESSED_DIR, "train.csv")
    test_path = os.path.join(PROCESSED_DIR, "test.csv")

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    print("\n--- Feature Engineering & Split Complete ---")
    print(f"Train dataset saved to: {train_path}")
    print(f"Test dataset saved to: {test_path}")

if __name__ == "__main__":
    engineer_features_and_split()