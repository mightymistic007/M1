import os
import sys
import json
import pandas as pd

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import pipeline and solver (handles both direct execution and module import)
try:
    from models.pipeline import SupplyChainPipeline
    from models.prescriptive_solver import PrescriptiveSolver
except ModuleNotFoundError:
    from pipeline import SupplyChainPipeline
    from prescriptive_solver import PrescriptiveSolver

def run_mid_review_demo():
    print("=" * 65)
    print(" SupplyPrescript — Mid Review Pipeline Demo (Days 1–15)")
    print("=" * 65)

    test_path = os.path.join("data", "processed", "test.csv")
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Test data not found at {test_path}")

    # Load 3 sample test shipments representing different risk profiles
    test_df = pd.read_csv(test_path).head(3)

    pipeline = SupplyChainPipeline()
    solver = PrescriptiveSolver()

    print("\n[Step 1] Ingesting Shipment Data & Generating XGBoost Delay Predictions...")
    predictions = pipeline.predict_delay_risk(test_df)

    for i, pred in enumerate(predictions, 1):
        print(f"\n--- Shipment Record #{i}: {pred['shipment_id']} ---")
        print(f"  • Order Value:           ${pred['order_value_usd']:,.2f}")
        print(f"  • Scheduled Window:      {pred['scheduled_days']} Days")
        print(f"  • Predicted Delay Risk:  {pred['predicted_delay_risk'] * 100:.2f}%")
        print(f"  • Delay Flag:            {'DELAY EXPECTED' if pred['is_delayed_prediction'] else 'ON TIME'}")
        print(f"  • Estimated Disruption:  {pred['estimated_delay_days']} Days")

        print("\n[Step 2] Executing Prescriptive Solver...")
        solution = solver.solve_shipment(pred)

        print("  Prescribed Business Actions (App Team Contract):")
        for opt in solution["prescribed_options"]:
            print(f"    [{opt['option_id']}] {opt['name']}")
            print(f"         Total Cost: ${opt['cost_usd']:,.2f} (Delta: +${opt['net_cost_increase_usd']:,.2f})")
            print(f"         Delay Mitigated: {opt['days_delayed_mitigated']} Days | Final Expected Delay: {opt['final_estimated_delay']} Days")
            print(f"         Tradeoff: {opt['tradeoff']}")

    print("\n" + "=" * 65)
    print(" Mid Review Demo Flow Completed Successfully")
    print("=" * 65)

if __name__ == "__main__":
    run_mid_review_demo()