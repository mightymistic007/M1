import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.m4_optimization_solver import M4OptimizationSolver

def validate_schema():
    print("=== [M4 Track] Day 13: Validating JSON Schema Contract Compliance ===")
    solver = M4OptimizationSolver()
    
    sample_records = [
        {"shipment_id": "VAL-001", "order_value_usd": 180.0, "estimated_delay_days": 3, "predicted_delay_risk": 0.65},
        {"shipment_id": "VAL-002", "order_value_usd": 320.0, "estimated_delay_days": 1, "predicted_delay_risk": 0.25}
    ]
    
    output = solver.solve_batch(sample_records)
    
    # Assert top-level list
    assert isinstance(output, list), "Schema violation: Output must be a list"
    assert len(output) == 2, "Output length mismatch"
    
    required_root_keys = {"shipment_id", "predicted_delay_risk", "initial_delay_estimate_days", "prescribed_options"}
    required_opt_keys = {
        "option_id", "name", "cost_usd", "net_cost_increase_usd",
        "days_delayed_mitigated", "final_estimated_delay", "optimal_assigned", "tradeoff"
    }
    
    for rec in output:
        assert required_root_keys.issubset(rec.keys()), f"Missing root keys in: {rec.keys()}"
        assert isinstance(rec["shipment_id"], str)
        assert isinstance(rec["predicted_delay_risk"], float)
        assert isinstance(rec["initial_delay_estimate_days"], int)
        assert isinstance(rec["prescribed_options"], list)
        assert len(rec["prescribed_options"]) == 3
        
        for opt in rec["prescribed_options"]:
            assert required_opt_keys.issubset(opt.keys()), f"Missing option keys in: {opt.keys()}"
            assert opt["option_id"] in ["OPT-A", "OPT-B", "OPT-C"]
            assert isinstance(opt["cost_usd"], float)
            assert isinstance(opt["net_cost_increase_usd"], float)
            assert isinstance(opt["days_delayed_mitigated"], int)
            assert isinstance(opt["final_estimated_delay"], int)
            assert isinstance(opt["optimal_assigned"], bool)
            assert isinstance(opt["tradeoff"], str)
            
    print("JSON Schema Contract validation passed successfully!")

if __name__ == "__main__":
    validate_schema()
