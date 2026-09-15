
# M4 Track — Day 6: Prescriptive Optimization Assumptions & Operational Logic

## 1. Core Mathematical Assumptions

* **Linear Delay Penalty ($\lambda = \$45.00/\text{day}$)**: Delays beyond the mitigated schedule accumulate penalties linearly without sudden non-linear inflection cliffs.
* **Deterministic Mitigation Times ($\Delta_j$)**:
  * Option A (Air Freight Expedited): Compresses transit time by up to 4 days.
  * Option B (Alternate Regional Supplier): Compresses transit time by up to 2 days.
  * Option C (Standard Delay Acceptance): Provides 0 days of delay mitigation.
* **Proportional Cost Multipliers**:
  * Option A incurs a +45% freight surcharge over baseline order value.
  * Option B incurs a +15% procurement premium over baseline order value.
  * Option C carries zero incremental surcharge (1.0x baseline).

---

## 2. Capacity & Operational Feasibility Bounds

* **Fleet Air Freight Quota ($\le 20\%$)**: Contractual airline cargo limits allow no more than $\lceil 0.20 \times N \rceil$ shipments in any concurrent operational batch to take Option A.
* **Alternate Supplier Quota ($\le 35\%$)**: Regional backup facilities cap inventory shifts at $\lceil 0.35 \times N \rceil$ concurrent allocations.
* **Hard Budget Cap Guard**: Any mitigation option where total cost exceeds `budget_max_cap_usd` ($399.98) is assigned an upper bound of $0.0$, preventing its selection.

---

## 3. Fallback Guarantees

* If LP solving encounters infeasibility due to overly restrictive concurrent constraints, the solver automatically falls back to **Option C** (`x_sol = [0, 0, 1]`) to ensure the pipeline never drops shipment records.
* Non-negative order values and normalized delay windows are guaranteed through input sanitization.
