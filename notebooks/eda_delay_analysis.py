import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

CLEAN_DATA_PATH = os.path.join("data", "processed", "cleaned_supply_chain_data.csv")
OUTPUT_DIR = os.path.join("notebooks", "plots")

def perform_eda():
    if not os.path.exists(CLEAN_DATA_PATH):
        raise FileNotFoundError(f"Cleaned dataset not found at {CLEAN_DATA_PATH}. Run clean_data.py first.")

    df = pd.read_csv(CLEAN_DATA_PATH)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("--- Starting Exploratory Data Analysis (EDA) ---")
    print(f"Total Records Analyzed: {len(df):,}")

    # 1. Overall Delay Rate
    delay_rate = (df['is_delayed'].sum() / len(df)) * 100
    print(f"Overall Delayed Shipments Rate: {delay_rate:.2f}%")

    # Set visualization style
    sns.set_theme(style="whitegrid")

    # 2. Plot 1: Delay Days Distribution
    plt.figure(figsize=(10, 5))
    sns.histplot(df['delay_days'], bins=15, kde=True, color='crimson')
    plt.title('Shipment Delay Distribution (Days)')
    plt.xlabel('Delay (Days)')
    plt.ylabel('Shipment Count')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'delay_days_distribution.png'))
    plt.close()

    # 3. Plot 2: Delay Rate by Shipping Mode
    if 'shipping_mode' in df.columns:
        plt.figure(figsize=(8, 5))
        mode_delay = df.groupby('shipping_mode')['is_delayed'].mean().reset_index()
        mode_delay['is_delayed'] *= 100
        sns.barplot(data=mode_delay, x='shipping_mode', y='is_delayed', palette='Blues_d')
        plt.title('Delay Percentage by Shipping Mode')
        plt.xlabel('Shipping Mode')
        plt.ylabel('Late Delivery Risk (%)')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'delay_by_shipping_mode.png'))
        plt.close()

    # 4. Plot 3: Delay Rate by Top 10 Product Categories
    if 'category_name' in df.columns:
        plt.figure(figsize=(12, 6))
        top_cats = df['category_name'].value_counts().head(10).index
        cat_df = df[df['category_name'].isin(top_cats)]
        cat_delay = cat_df.groupby('category_name')['is_delayed'].mean().reset_index()
        cat_delay['is_delayed'] *= 100
        sns.barplot(data=cat_delay.sort_values(by='is_delayed', ascending=False), 
                    y='category_name', x='is_delayed', palette='Reds_d')
        plt.title('Late Delivery Percentage for Top 10 Product Categories')
        plt.xlabel('Late Delivery Risk (%)')
        plt.ylabel('Category')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'delay_by_category.png'))
        plt.close()

    print("\n--- EDA Completed Successfully ---")
    print(f"Plots saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    perform_eda()

