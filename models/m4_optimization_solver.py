import os
import json
import math
import numpy as np
from scipy.optimize import linprog
from typing import List, Dict, Any

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "solver_constraints_config.json")

class M4OptimizationSolver:
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        cfg = {
            "budget_cap_usd": 399.98,
            "budget_baseline_usd": 203.77,
            "option_a_capacity_pct": 0.20,
            "option_b_capacity_pct": 0.35,
            "delay_penalty_per_day_usd": 45.0,
            "max_historical_delay_days": 6
        }
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    loaded = json.load(f)
                    cfg.update(loaded)
            except Exception:
                pass

        # Normalize penalty rate key across naming variations
        if "delay_penalty_per_day_usd" not in cfg:
            cfg["delay_penalty_per_day_usd"] = cfg.get(
                "sla_penalty_rate_per_day",
                cfg.get("delay_penalty_usd", cfg.get("sla_penalty_cost_per_day_usd", 45.0))
            )

        return cfg

    def _sanitize_record(self, record: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """Edge-case sanitization for dirty or abnormal input fields."""
        shipment_id = str(record.get("shipment_id", f"SHIP-DEF-{idx:04d}"))
        
        # Order Value sanitization
        raw_val = record.get("order_value_usd", self.config.get("budget_baseline_usd", 203.77))
        try:
            val = float(raw_val) if raw_val is not None else float(self.config.get("budget_baseline_usd", 203.77))
            val = max(1.0, val)
        except (ValueError, TypeError):
            val = float(self.config.get("budget_baseline_usd", 203.77))

        # Delay sanitization
        raw_delay = record.get("estimated_delay_days", 0)
        try:
            delay = int(round(float(raw_delay)))
            delay = max(0, min(delay, self.config.get("max_historical_delay_days", 6)))
        except (ValueError, TypeError):
            delay = 0

        # Delay Risk sanitization
        raw_risk = record.get("predicted_delay_risk", 0.0)
        try:
            risk = float(raw_risk) if raw_risk is not None else 0.0
            risk = max(0.0, min(1.0, risk))
        except (ValueError, TypeError):
            risk = 0.0

        return {
            "shipment_id": shipment_id,
            "order_value_usd": round(val, 2),
            "estimated_delay_days": delay,
            "predicted_delay_risk": round(risk, 4)
        }

    def solve_batch(self, batch_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Solves LP assignment across 3 candidate options:
        - OPT-A: Air Expedited (Cost +45%, -4 delay days)
        - OPT-B: Regional Carrier (Cost +15%, -2 delay days)
        - OPT-C: Standard Ground (Cost +0%, 0 delay days mitigated)
        """
        if not batch_records:
            return []

        clean_batch = [self._sanitize_record(rec, idx) for idx, rec in enumerate(batch_records)]
        N = len(clean_batch)

        penalty_rate = self.config.get("delay_penalty_per_day_usd", 45.0)
        budget_cap = self.config.get("budget_cap_usd", 399.98)

        cap_a = max(1, math.ceil(self.config.get("option_a_capacity_pct", 0.20) * N))
        cap_b = max(1, math.ceil(self.config.get("option_b_capacity_pct", 0.35) * N))

        options_spec = [
            {"id": "OPT-A", "cost_pct": 0.45, "mitigate": 4},
            {"id": "OPT-B", "cost_pct": 0.15, "mitigate": 2},
            {"id": "OPT-C", "cost_pct": 0.00, "mitigate": 0}
        ]

        c_obj = []
        for rec in clean_batch:
            v = rec["order_value_usd"]
            d = rec["estimated_delay_days"]
            for opt in options_spec:
                direct_cost = v * (1.0 + opt["cost_pct"])
                residual_delay = max(0, d - opt["mitigate"])
                penalty_cost = residual_delay * penalty_rate
                
                # Budget cap infeasibility penalty
                if direct_cost > budget_cap:
                    penalty_cost += 1e6

                # Objective: minimize (direct cost increase + delay penalty)
                c_obj.append((v * opt["cost_pct"]) + penalty_cost)

        # Equality constraint: exactly one option chosen per shipment
        A_eq = np.zeros((N, 3 * N))
        b_eq = np.ones(N)
        for i in range(N):
            A_eq[i, i * 3 : (i + 1) * 3] = 1.0

        # Capacity inequality: sum(x_A) <= cap_a, sum(x_B) <= cap_b
        A_ub = np.zeros((2, 3 * N))
        b_ub = np.array([cap_a, cap_b])
        for i in range(N):
            A_ub[0, i * 3] = 1.0       # Option A
            A_ub[1, i * 3 + 1] = 1.0   # Option B

        bounds = [(0, 1) for _ in range(3 * N)]
        res = linprog(c=c_obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

        decisions = {}
        if res.success:
            for i in range(N):
                assigned_idx = int(np.argmax(res.x[i * 3 : (i + 1) * 3]))
                decisions[i] = assigned_idx
        else:
            for i in range(N):
                decisions[i] = 2

        output = []
        for i, rec in enumerate(clean_batch):
            chosen = decisions[i]
            v = rec["order_value_usd"]
            d = rec["estimated_delay_days"]

            opt_cards = []
            for j, opt in enumerate(options_spec):
                c_usd = round(v * (1.0 + opt["cost_pct"]), 2)
                mitigated = min(d, opt["mitigate"])
                final_delay = max(0, d - opt["mitigate"])

                opt_cards.append({
                    "option_id": opt["id"],
                    "name": "Air Expedited" if j == 0 else ("Regional Fast-Track" if j == 1 else "Standard Ground"),
                    "cost_usd": c_usd,
                    "net_cost_increase_usd": round(v * opt["cost_pct"], 2),
                    "days_delayed_mitigated": mitigated,
                    "final_estimated_delay": final_delay,
                    "optimal_assigned": (j == chosen)
                })

            output.append({
                "shipment_id": rec["shipment_id"],
                "original_estimated_delay": d,
                "prescribed_options": opt_cards
            })

        return output