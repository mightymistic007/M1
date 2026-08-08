import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 10000

df = pd.DataFrame({
    'shipment_id': [f"SHIP-{1000+i}" for i in range(n_samples)],
    'origin': np.random.choice(['NYC', 'LAX', 'CHI', 'DFW', 'SEA'], n_samples),
    'destination': np.random.choice(['MIA', 'SFO', 'BOS', 'ATL', 'DEN'], n_samples),
    'planned_delivery_days': np.random.randint(3, 10, n_samples),
    'actual_delivery_days': np.random.randint(2, 18, n_samples),
    'cost': np.random.uniform(100.0, 5000.0, n_samples).round(2),
    'category': np.random.choice(['Electronics', 'Apparel', 'Automotive', 'Perishables'], n_samples)
})

df.to_csv('data/raw/supply_chain_data.csv', index=False)
print("Mock dataset successfully generated in data/raw/supply_chain_data.csv!")
