import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.m4_optimization_solver import M4OptimizationSolver

def run_scenario_validation():
    print("=== [M4 Track] Day 10: Prescriptive Scenario Sanity Checks ===")
    solver = M4OptimizationSolver()

    scenarios = [
        {
            "name": "Scenario 1: Critical Delay High-Value Shipment",
            "payload": [{
                "shipment_id": "SCENARIO-CRITICAL-01",
                "order_value_usd": 250.0,
                "estimated_delay_days": 5,
                "predicted_delay_risk": 0.92
            }]
        },
        {
            "name": "Scenario 2: Low-Risk Nominal Shipment",
            "payload": [{
                "shipment_id": "SCENARIO-NOMINAL-02",
                "order_value_usd": 120.0,
                "estimated_delay_days": 0,
                "predicted_delay_risk": 0.08
            }]
        },
        {
            "name": "Scenario 3: High-Cost Near-Budget Cap Shipment",
            "payload": [{
                "shipment_id": "SCENARIO-BUDGET-03",
                "order_value_usd": 380.0,
                "estimated_delay_days": 4,
                "predicted_delay_risk": 0.78
            }]
        },
        {
            "name": "Scenario 4: Moderate Delay Balanced Tradeoff",
            "payload": [{
                "shipment_id": "SCENARIO-MODERATE-04",
                "order_value_usd": 180.0,
                "estimated_delay_days": 2,
                "predicted_delay_risk": 0.45
            }]
        }
    ]

    all_passed = True

    for item in scenarios:
        name = item["name"]
        records = item["payload"]
        res = solver.solve_batch(records)[0]
        options = res["prescribed_options"]

        print(f"\nEvaluating -> {name}")
        print(f"  Shipment ID: {res['shipment_id']} | Risk: {res['predicted_delay_risk']} | Delay Est: {res['initial_delay_estimate_days']}d")

        for opt in options:
            opt_tag = " [OPTIMAL]" if opt["optimal_assigned"] else ""
            print(f"    - {opt['option_id']} ({opt['name']}): Cost=${opt['cost_usd']:.2f}, Saved={opt['days_delayed_mitigated']}d, Rem={opt['final_estimated_delay']}d{opt_tag}")

        # Sanity Rule 1: Always exactly 3 options
        if len(options) != 3:
            print("  ❌ Failed: Prescribed options count is not 3")
            all_passed = False

        # Sanity Rule 2: Non-negative cost and valid delay
        for opt in options:
            if opt["cost_usd"] < 0 or opt["final_estimated_delay"] < 0:
                print("  ❌ Failed: Cost or remaining delay is negative")
                all_passed = False

        # Sanity Rule 3: For zero-delay shipments, Option C must be selected (no surcharge needed)
        if res["initial_delay_estimate_days"] == 0:
            if not options[2]["optimal_assigned"]:
                print("  ❌ Failed: Nominal zero-delay shipment did not default to Option C")
                all_passed = False

    if all_passed:
        print("\nAll scenario sanity checks passed with valid tradeoff allocations!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_scenario_validation()
