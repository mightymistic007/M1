import os
import sys
import time
import pandas as pd

# Guarantee project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.m4_pipeline_bridge import M4PipelineBridge

def run_week1_audit():
    print("=== [M4 Track] Week 1 Pipeline Audit ===")
    bridge = M4PipelineBridge()
    
    # Generate a realistic mini-batch of 10 candidate shipments
    mock_batch = []
    for i in range(10):
        mock_batch.append({
            "shipping_mode": i % 4,
            "type": i % 2,
            "market": i % 5,
            "order_region": i % 10,
            "customer_segment": i % 3,
            "category_name": (i * 3) % 20,
            "days_for_shipment_scheduled": (i % 4) + 1,
            "order_item_quantity": (i % 3) + 1,
            "order_item_product_price": 50.0 + (i * 25.0),
            "sales": (50.0 + (i * 25.0)) * ((i % 3) + 1),
            "order_item_id": f"AUDIT-SHIP-{i+1:04d}"
        })
    
    df = pd.DataFrame(mock_batch)
    
    start_time = time.time()
    results = bridge.predict_and_prescribe_batch(df)
    elapsed_ms = (time.time() - start_time) * 1000
    
    print(f"Audit completed in: {elapsed_ms:.2f} ms for {len(df)} records")
    
    # Verification assertions
    assert len(results) == 10, "Failed: Output length mismatch"
    opt_a_count = 0
    opt_b_count = 0
    
    for r in results:
        assert "shipment_id" in r
        assert "prescribed_options" in r
        assert len(r["prescribed_options"]) == 3
        
        assigned = [opt["optimal_assigned"] for opt in r["prescribed_options"]]
        assert sum(assigned) == 1, f"Failed: Exactly one option must be selected for {r['shipment_id']}"
        
        if r["prescribed_options"][0]["optimal_assigned"]:
            opt_a_count += 1
        if r["prescribed_options"][1]["optimal_assigned"]:
            opt_b_count += 1
            
    print(f"Capacity allocations -> Option A (Air): {opt_a_count}/10, Option B (Alt Supplier): {opt_b_count}/10")
    print("All contract schema checks and mathematical bounds passed successfully!")

if __name__ == "__main__":
    run_week1_audit()
