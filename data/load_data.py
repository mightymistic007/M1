import pandas as pd
import os

# Point to the real Kaggle CSV file
DATA_PATH = os.path.join("data", "raw", "DataCoSupplyChainDataset.csv")

def load_and_validate_dataco_data():
    """Loads the real DataCo dataset and performs an initial schema check."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. "
            f"Please ensure DataCoSupplyChainDataset.csv is placed inside data/raw/"
        )
    
    print("--- Loading DataCo Supply Chain Dataset ---")
    # Encoding latin1 is required for the DataCo CSV
    df = pd.read_csv(DATA_PATH, encoding='latin1')
    
    print(f"Total Rows: {df.shape[0]:,}")
    print(f"Total Columns: {df.shape[1]}\n")
    
    # Key columns needed for downstream delay prediction & optimization
    key_cols = [
        'Order Item Id', 
        'Days for shipping (real)', 
        'Days for shipment (scheduled)', 
        'Delivery Status', 
        'Late_risk', 
        'Category Name', 
        'Order City', 
        'Order Country', 
        'Order Item Product Price'
    ]
    
    print("--- Verifying Key Columns for ML Pipeline ---")
    available_keys = [c for c in key_cols if c in df.columns]
    print(f"Found {len(available_keys)} out of {len(key_cols)} key analytical features.")
    
    print("\n--- Missing Value Count in Key Columns ---")
    print(df[available_keys].isnull().sum())
    
    print("\n--- Sample Delivery Status Distribution ---")
    print(df['Delivery Status'].value_counts())
    
    return df

if __name__ == "__main__":
    load_and_validate_dataco_data()

