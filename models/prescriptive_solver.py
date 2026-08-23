import json
import os

CONFIG_PATH = os.path.join("data", "processed", "solver_constraints_config.json")

class PrescriptiveSolver:
    def __init__(self):
        with open(CONFIG_PATH, "r") as f:
            self.config = json.load(f)
            
    def solve_shipment(self, shipment_record: dict) -> dict:
        """
        Generates 3 ranked prescriptive options matching the Application Team's schema.
        Option 1: Airfreight Expedited
        Option 2: Alternate Supplier Sourcing
        Option 3: Standard Delivery / Delay Acceptance
        """
        base_cost = shipment_record.get("order_value_usd", 200.0)
        delay_days = shipment_record.get("estimated_delay_days", 0)
        
        # 1. Option A: Air Freight
        air_cost = round(base_cost * self.config["prescriptive_options"]["air_freight"]["expedite_cost_multiplier"], 2)
        air_saved = min(delay_days, self.config["prescriptive_options"]["air_freight"]["days_saved"])
        option_a = {
            "option_id": "OPT-A",
            "name": "Air Freight Expedited",
            "cost_usd": air_cost,
            "net_cost_increase_usd": round(air_cost - base_cost, 2),
            "days_delayed_mitigated": air_saved,
            "final_estimated_delay": max(0, delay_days - air_saved),
            "tradeoff": f"Eliminates up to {air_saved} delay days with a 45% expedite fee."
        }

        # 2. Option B: Alternate Supplier
        alt_cost = round(base_cost * self.config["prescriptive_options"]["alternate_supplier"]["cost_premium_rate"], 2)
        alt_saved = min(delay_days, self.config["prescriptive_options"]["alternate_supplier"]["days_saved"])
        option_b = {
            "option_id": "OPT-B",
            "name": "Alternate Regional Supplier",
            "cost_usd": alt_cost,
            "net_cost_increase_usd": round(alt_cost - base_cost, 2),
            "days_delayed_mitigated": alt_saved,
            "final_estimated_delay": max(0, delay_days - alt_saved),
            "tradeoff": f"Recovers {alt_saved} delay days at a 15% procurement premium."
        }

        # 3. Option C: Accept Delay
        option_c = {
            "option_id": "OPT-C",
            "name": "Accept Delay & Reallocate Buffer",
            "cost_usd": base_cost,
            "net_cost_increase_usd": 0.00,
            "days_delayed_mitigated": 0,
            "final_estimated_delay": delay_days,
            "tradeoff": f"Zero additional cost; absorbs the full {delay_days}-day delay."
        }

        # Assemble JSON Contract payload for App Team
        payload = {
            "shipment_id": shipment_record.get("shipment_id", "UNKNOWN"),
            "predicted_delay_risk": shipment_record.get("predicted_delay_risk", 0.0),
            "initial_delay_estimate_days": delay_days,
            "prescribed_options": [option_a, option_b, option_c]
        }
        return payload

if __name__ == "__main__":
    from pipeline import SupplyChainPipeline
    import pandas as pd

    test_df = pd.read_csv(os.path.join("data", "processed", "test.csv")).head(2)
    pipeline = SupplyChainPipeline()
    sample_inputs = pipeline.predict_delay_risk(test_df)

    solver = PrescriptiveSolver()
    contract_outputs = [solver.solve_shipment(item) for item in sample_inputs]

    OUTPUT_SAMPLE = os.path.join("notebooks", "evaluation_reports", "app_contract_sample.json")
    with open(OUTPUT_SAMPLE, "w") as f:
        json.dump(contract_outputs, f, indent=2)

    print("--- Prescriptive Solver JSON Contract Sample (App Team Handshake) ---")
    print(json.dumps(contract_outputs, indent=2))
    print(f"\nSaved JSON contract payload to: {OUTPUT_SAMPLE}")

