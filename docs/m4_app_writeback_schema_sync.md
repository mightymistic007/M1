
# M4 Track — Day 22: App Team Write-Back & Actual Outcome Schema Sync

## 1. Context & Purpose

When orders reach their delivery destination, the Application Team's platform records the final delivery metrics into PostgreSQL/database tables. This document establishes the write-back payload specification required by the M4 Closed-Loop Drift Monitor & Retraining Engine.

---

## 2. Actual Outcome Write-Back Schema Contract

| Field Name                  | Type         | Nullable | Description / Validation                                               |
| :-------------------------- | :----------- | :------- | :--------------------------------------------------------------------- |
| `shipment_id`             | String       | No       | Unique shipment identifier matching the original prescription request. |
| `order_item_id`           | String       | Yes      | Foreign key reference to order item record.                            |
| `assigned_option_id`      | String       | No       | Must be one of:`["OPT-A", "OPT-B", "OPT-C"]`.                        |
| `predicted_delay_days`    | Integer      | No       | Disruption delay duration projected by M4 solver ($\ge 0$).          |
| `actual_delivery_days`    | Integer      | No       | Total elapsed shipping days recorded from warehouse dispatch.          |
| `scheduled_delivery_days` | Integer      | No       | Days originally allotted by SLA contract baseline.                     |
| `actual_delay_days`       | Integer      | No       | Net realization:$\max(0, \text{actual} - \text{scheduled})$.         |
| `realized_penalty_usd`    | Float        | No       | Realized customer breach penalty cost incurred ($\ge 0.0$).          |
| `predicted_penalty_usd`   | Float        | No       | Projected penalty cost estimated during inference ($\ge 0.0$).       |
| `delivery_timestamp`      | String (ISO) | No       | UTC timestamp of confirmed destination delivery.                       |

---

## 3. Sample Write-Back JSON Object

```json
{
  "shipment_id": "SHIP-US-2026-9041",
  "order_item_id": "ITEM-10291",
  "assigned_option_id": "OPT-A",
  "predicted_delay_days": 1,
  "scheduled_delivery_days": 3,
  "actual_delivery_days": 4,
  "actual_delay_days": 1,
  "realized_penalty_usd": 45.00,
  "predicted_penalty_usd": 45.00,
  "delivery_timestamp": "2026-09-15T18:30:00Z"
}
```
