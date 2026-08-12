import pandas as pd
import numpy as np
import os

RAW_DATA_PATH = os.path.join("data", "raw", "DataCoSupplyChainDataset.csv")
CLEAN_DATA_PATH = os.path.join("data", "processed", "cleaned_supply_chain_data.csv")

def clean_supply_chain_data():
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data not found at {RAW_DATA_PATH}")

    print("--- Starting Data Cleaning Process ---")
    df = pd.read_csv(RAW_DATA_PATH, encoding='latin1')
    initial_rows = len(df)
    print(f"Initial record count: {initial_rows:,}")

    # 1. Remove duplicate records
    df = df.drop_duplicates()
    print(f"Rows after removing duplicates: {len(df):,} (Removed {initial_rows - len(df):,})")

    # 2. Standardize all column names to snake_case first
    df.columns = [
        col.lower()
           .replace(' ', '_')
           .replace('(', '')
           .replace(')', '')
        for col in df.columns
    ]

    # 3. Filter for existing core features
    desired_cols = [
        'order_item_id', 'order_id', 'type', 'days_for_shipping_real', 
        'days_for_shipment_scheduled', 'delivery_status', 'late_delivery_risk',
        'category_name', 'customer_city', 'customer_country', 'customer_segment',
        'order_city', 'order_country', 'order_region', 'order_state',
        'market', 'order_item_quantity', 'order_item_product_price',
        'sales', 'order_profit_per_order', 'shipping_mode'
    ]
    
    # Safely select only columns that exist in the dataframe
    available_cols = [col for col in desired_cols if col in df.columns]
    df = df[available_cols].copy()

    # 4. Handle missing values
    text_cols = df.select_dtypes(include=['object']).columns
    df[text_cols] = df[text_cols].fillna('Unknown')

    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    # 5. Fix/cast data types where available
    if 'order_item_id' in df.columns:
        df['order_item_id'] = df['order_item_id'].astype(str)
    if 'order_id' in df.columns:
        df['order_id'] = df['order_id'].astype(str)
    if 'days_for_shipping_real' in df.columns:
        df['days_for_shipping_real'] = df['days_for_shipping_real'].astype(int)
    if 'days_for_shipment_scheduled' in df.columns:
        df['days_for_shipment_scheduled'] = df['days_for_shipment_scheduled'].astype(int)

    # 6. Create target target calculation fields (delay in days)
    if 'days_for_shipping_real' in df.columns and 'days_for_shipment_scheduled' in df.columns:
        df['delay_days'] = df['days_for_shipping_real'] - df['days_for_shipment_scheduled']
        df['is_delayed'] = (df['delay_days'] > 0).astype(int)

    # 7. Save cleaned dataset
    os.makedirs(os.path.dirname(CLEAN_DATA_PATH), exist_ok=True)
    df.to_csv(CLEAN_DATA_PATH, index=False)
    
    print("\n--- Cleaning Complete ---")
    print(f"Final Cleaned Dataset Rows: {len(df):,}")
    print(f"Cleaned columns count: {len(df.columns)}")
    print(f"Saved to: {CLEAN_DATA_PATH}")

if __name__ == "__main__":
    clean_supply_chain_data()

