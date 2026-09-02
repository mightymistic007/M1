import pandas as pd
import numpy as np
import time
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from models.pipeline import SupplyChainPipeline
    from models.prescriptive_solver import PrescriptiveSolver
except ModuleNotFoundError:
    from pipeline import SupplyChainPipeline
    from prescriptive_solver import PrescriptiveSolver

REPORT_PATH = os.path.join("notebooks", "evaluation_reports", "latency_benchmark.json")

def run_latency_benchmark():
    print("--- Running Inference & Solver Latency Benchmark ---")
    test_path = os.path.join("data", "processed", "test.csv")
    test_df = pd.read_csv(test_path)

    pipeline = SupplyChainPipeline()
    solver = PrescriptiveSolver()

    batch_sizes = [1, 10, 50, 100, 500]
    benchmark_results = []

    for size in batch_sizes:
        batch = test_df.head(size)
        
        # Warmup
        _ = pipeline.predict_delay_risk(batch)
        
        # Benchmark timing
        t0 = time.perf_counter()
        predictions = pipeline.predict_delay_risk(batch)
        _ = [solver.solve_shipment(p) for p in predictions]
        t1 = time.perf_counter()

        elapsed_ms = (t1 - t0) * 1000
        per_record_ms = elapsed_ms / size

        benchmark_results.append({
            "batch_size": size,
            "total_latency_ms": round(elapsed_ms, 2),
            "latency_per_record_ms": round(per_record_ms, 4)
        })
        print(f"Batch Size: {size:3d} | Total: {elapsed_ms:6.2f} ms | Per Record: {per_record_ms:.4f} ms")

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(benchmark_results, f, indent=4)
        
    print(f"\nSaved benchmark metrics to: {REPORT_PATH}")

if __name__ == "__main__":
    run_latency_benchmark()

