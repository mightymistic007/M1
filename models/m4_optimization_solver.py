import os
import json
import numpy as np
from scipy.optimize import linprog
from typing import List, Dict, Any

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "solver_constraints_config.json")

class M4OptimizationSolver:
    def __init__(self, config_path: str = CONFIG_PATH):
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {
                "budget_baseline_usd": 203.77,
                "budget_max_cap_usd": 399.98,
                "max_historical_delay_days": 6,
                "prescriptive_options": {
                    "air_freight": {"expedite_cost_multiplier": 1.45, "days_saved": 4},
                    "alternate_supplier": {"cost_premium_rate": 1.15, "days_saved": 2},
                    "standard_delay": {"cost_premium_rate": 1.0, "days_saved": 0}
                }
            }
        self.penalty_per_day = 45.0
        self.max_cap = float(self.config.get("budget_max_cap_usd", 399.98))

    def solve_batch(self, shipments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Solves batch assignment using SciPy linprog.
        Minimizes total logistics cost + SLA delay breach penalties subject to:
          - Exactly 1 prescriptive option assigned per shipment
          - Air Freight (OPT-A) allocation <= 20%
          - Alternate Supplier (OPT-B) allocation <= 35%
          - Hard budget cap enforcement
        """
        N = len(shipments)
        if N == 0:
            return []

        num_vars = 3 * N

        # 1. Objective Vector c
        c = np.zeros(num_vars)
        for i, ship in enumerate(shipments):
            base_cost = float(ship.get("order_value_usd", self.config["budget_baseline_usd"]))
            delay_days = int(round(float(ship.get("estimated_delay_days", 0))))

            # Option A: Air Freight Expedited
            cost_a = base_cost * self.config["prescriptive_options"]["air_freight"]["expedite_cost_multiplier"]
            rem_delay_a = max(0, delay_days - self.config["prescriptive_options"]["air_freight"]["days_saved"])
            c[3 * i + 0] = cost_a + (self.penalty_per_day * rem_delay_a)

            # Option B: Alternate Regional Supplier
            cost_b = base_cost * self.config["prescriptive_options"]["alternate_supplier"]["cost_premium_rate"]
            rem_delay_b = max(0, delay_days - self.config["prescriptive_options"]["alternate_supplier"]["days_saved"])
            c[3 * i + 1] = cost_b + (self.penalty_per_day * rem_delay_b)

            # Option C: Accept Delay & Reallocate Buffer
            cost_c = base_cost * self.config["prescriptive_options"]["standard_delay"]["cost_premium_rate"]
            rem_delay_c = delay_days
            c[3 * i + 2] = cost_c + (self.penalty_per_day * rem_delay_c)

        # 2. Assignment Equality Constraints: Sum_j x_{i,j} = 1
        A_eq = np.zeros((N, num_vars))
        b_eq = np.ones(N)
        for i in range(N):
            A_eq[i, 3 * i : 3 * i + 3] = 1.0

        # 3. Fleet Capacity Bounds: Air Freight <= 20%, Alt Supplier <= 35%
        max_opt_a = max(1, int(np.ceil(0.20 * N)))
        max_opt_b = max(1, int(np.ceil(0.35 * N)))

        A_ub = np.zeros((2, num_vars))
        b_ub = np.array([max_opt_a, max_opt_b])
        for i in range(N):
            A_ub[0, 3 * i + 0] = 1.0
            A_ub[1, 3 * i + 1] = 1.0

        # 4. Variable Bounds: [0, 1] with Hard Budget Cap restriction
        bounds = []
        for i, ship in enumerate(shipments):
            base_cost = float(ship.get("order_value_usd", self.config["budget_baseline_usd"]))
            for opt_key in ["air_freight", "alternate_supplier", "standard_delay"]:
                mult = self.config["prescriptive_options"][opt_key].get(
                    "expedite_cost_multiplier",
                    self.config["prescriptive_options"][opt_key].get("cost_premium_rate", 1.0)
                )
                opt_cost = base_cost * mult
                upper = 0.0 if opt_cost > self.max_cap else 1.0
                bounds.append((0.0, upper))

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

        # Fallback to Option C if constrained solver finds infeasibility
        x_sol = res.x if res.success else np.tile([0, 0, 1], N)

        # 5. Output matching App Team JSON schema contract
        results = []
        for i, ship in enumerate(shipments):
            base_cost = float(ship.get("order_value_usd", self.config["budget_baseline_usd"]))
            delay_days = int(round(float(ship.get("estimated_delay_days", 0))))

            cost_a = round(base_cost * self.config["prescriptive_options"]["air_freight"]["expedite_cost_multiplier"], 2)
            cost_b = round(base_cost * self.config["prescriptive_options"]["alternate_supplier"]["cost_premium_rate"], 2)
            cost_c = round(base_cost * self.config["prescriptive_options"]["standard_delay"]["cost_premium_rate"], 2)

            options = [
                {
                    "option_id": "OPT-A",
                    "name": "Air Freight Expedited",
                    "cost_usd": cost_a,
                    "net_cost_increase_usd": round(cost_a - base_cost, 2),
                    "days_delayed_mitigated": min(delay_days, self.config["prescriptive_options"]["air_freight"]["days_saved"]),
                    "final_estimated_delay": max(0, delay_days - self.config["prescriptive_options"]["air_freight"]["days_saved"]),
                    "optimal_assigned": bool(np.isclose(x_sol[3 * i + 0], 1.0, atol=1e-3)),
                    "tradeoff": "Maximum transit compression (+45% freight surcharge)"
                },
                {
                    "option_id": "OPT-B",
                    "name": "Alternate Regional Supplier",
                    "cost_usd": cost_b,
                    "net_cost_increase_usd": round(cost_b - base_cost, 2),
                    "days_delayed_mitigated": min(delay_days, self.config["prescriptive_options"]["alternate_supplier"]["days_saved"]),
                    "final_estimated_delay": max(0, delay_days - self.config["prescriptive_options"]["alternate_supplier"]["days_saved"]),
                    "optimal_assigned": bool(np.isclose(x_sol[3 * i + 1], 1.0, atol=1e-3)),
                    "tradeoff": "Balanced mitigation (+15% procurement cost, 2 days saved)"
                },
                {
                    "option_id": "OPT-C",
                    "name": "Accept Delay & Reallocate Buffer",
                    "cost_usd": cost_c,
                    "net_cost_increase_usd": 0.0,
                    "days_delayed_mitigated": 0,
                    "final_estimated_delay": delay_days,
                    "optimal_assigned": bool(np.isclose(x_sol[3 * i + 2], 1.0, atol=1e-3)),
                    "tradeoff": "Zero expenditure increase; absorbs schedule variance"
                }
            ]

            results.append({
                "shipment_id": str(ship.get("shipment_id", f"SHIP-M4-{i+1:04d}")),
                "predicted_delay_risk": float(ship.get("predicted_delay_risk", 0.0)),
                "initial_delay_estimate_days": delay_days,
                "prescribed_options": options
            })

        return results
    