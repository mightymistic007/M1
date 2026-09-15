
# M4 Track — Day 13: Application Team JSON Schema Contract Specification

## 1. Overview

This document defines the schema contract between the Prescriptive Optimization Engine (M4) and the downstream Application Platform. All API responses and batch file exports strictly adhere to this schema.

---

## 2. JSON Schema Definition (Draft-07 Compatible)

```json
{
  "$schema": "[http://json-schema.org/draft-07/schema#](http://json-schema.org/draft-07/schema#)",
  "title": "PrescriptiveOptimizationBatchResponse",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "shipment_id",
      "predicted_delay_risk",
      "initial_delay_estimate_days",
      "prescribed_options"
    ],
    "properties": {
      "shipment_id": {
        "type": "string",
        "description": "Unique identifier of the order or shipment item"
      },
      "predicted_delay_risk": {
        "type": "number",
        "minimum": 0.0,
        "maximum": 1.0,
        "description": "Predicted probability of disruption from XGBoost classifier"
      },
      "initial_delay_estimate_days": {
        "type": "integer",
        "minimum": 0,
        "maximum": 6,
        "description": "Projected disruption delay duration before mitigation"
      },
      "prescribed_options": {
        "type": "array",
        "minItems": 3,
        "maxItems": 3,
        "items": {
          "type": "object",
          "required": [
            "option_id",
            "name",
            "cost_usd",
            "net_cost_increase_usd",
            "days_delayed_mitigated",
            "final_estimated_delay",
            "optimal_assigned",
            "tradeoff"
          ],
          "properties": {
            "option_id": {
              "type": "string",
              "enum": ["OPT-A", "OPT-B", "OPT-C"]
            },
            "name": {
              "type": "string"
            },
            "cost_usd": {
              "type": "number",
              "minimum": 0.0
            },
            "net_cost_increase_usd": {
              "type": "number",
              "minimum": 0.0
            },
            "days_delayed_mitigated": {
              "type": "integer",
              "minimum": 0
            },
            "final_estimated_delay": {
              "type": "integer",
              "minimum": 0
            },
            "optimal_assigned": {
              "type": "boolean"
            },
            "tradeoff": {
              "type": "string"
            }
          }
        }
      }
    }
  }
}

[
  {
    "shipment_id": "SHIP-1001",
    "predicted_delay_risk": 0.8421,
    "initial_delay_estimate_days": 5,
    "prescribed_options": [
      {
        "option_id": "OPT-A",
        "name": "Air Freight Expedited",
        "cost_usd": 295.47,
        "net_cost_increase_usd": 91.70,
        "days_delayed_mitigated": 4,
        "final_estimated_delay": 1,
        "optimal_assigned": true,
        "tradeoff": "Maximum transit compression (+45% freight surcharge)"
      },
      {
        "option_id": "OPT-B",
        "name": "Alternate Regional Supplier",
        "cost_usd": 234.34,
        "net_cost_increase_usd": 30.57,
        "days_delayed_mitigated": 2,
        "final_estimated_delay": 3,
        "optimal_assigned": false,
        "tradeoff": "Balanced mitigation (+15% procurement cost, 2 days saved)"
      },
      {
        "option_id": "OPT-C",
        "name": "Accept Delay & Reallocate Buffer",
        "cost_usd": 203.77,
        "net_cost_increase_usd": 0.0,
        "days_delayed_mitigated": 0,
        "final_estimated_delay": 5,
        "optimal_assigned": false,
        "tradeoff": "Zero expenditure increase; absorbs schedule variance"
      }
    ]
  }
]

```
