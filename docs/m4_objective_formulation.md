
# M4 Track — Day 2: Optimization Objective Function Formulation

## 1. Problem Definition

The prescriptive engine solves a mixed-integer cost minimization problem across all flagged disruptive shipments in a batch. For each candidate shipment $i \in \{1, \dots, N\}$, the solver selects exactly one prescriptive mitigation action $j \in \{1, 2, 3\}$ (`OPT-A`, `OPT-B`, `OPT-C`).

## 2. Decision Variables

Define binary decision variable:

$$
x_{i,j} \in \{0, 1\} \quad \forall i \in \{1, \dots, N\}, \, j \in \{1, 2, 3\}
$$

Where:

* $x_{i,1} = 1 \implies$ Option A: Air Freight Expedited
* $x_{i,2} = 1 \implies$ Option B: Alternate Regional Supplier
* $x_{i,3} = 1 \implies$ Option C: Accept Delay & Reallocate Buffer

## 3. Objective Function

Minimize total expenditure, defined as the sum of direct procurement/freight costs and unmitigated customer SLA penalty costs:

$$
\min \sum_{i=1}^N \sum_{j=1}^3 x_{i,j} \cdot \Big[ C_{i,j} + \lambda \cdot \max\big(0, D_i - \Delta_{j}\big) \Big]
$$

Where:

* $C_{i,j}$: Total option cost (Base Order Cost $\times$ Option Cost Multiplier).
  * $C_{i,1} = \text{BaseCost}_i \times 1.45$
  * $C_{i,2} = \text{BaseCost}_i \times 1.15$
  * $C_{i,3} = \text{BaseCost}_i \times 1.00$
* $\lambda$: Disruption penalty multiplier ($45.00/day for delivery breach).
* $D_i$: Initial predicted disruption delay in days ($p_{\text{delay}} \times \text{max\_historical\_delay\_days}$).
* $\Delta_j$: Days mitigated by option $j$ ($\Delta_1 = 4$, $\Delta_2 = 2$, $\Delta_3 = 0$).
* $\max(0, D_i - \Delta_j)$: Remaining post-mitigation delay days.

## 4. Fundamental Constraints

1. **Assignment Uniqueness**: Exactly one action must be selected per shipment:

   $$
   \sum_{j=1}^3 x_{i,j} = 1 \quad \forall i \in \{1, \dots, N\}
   $$
2. **Per-Shipment Hard Budget Ceiling**:

   $$
   \sum_{j=1}^3 x_{i,j} \cdot C_{i,j} \le \text{budget\_max\_cap\_usd} \quad (\$399.98) \quad \forall i
   $$
3. **Fleet Capacity Limits (Batch Level)**:

   * Option A (Air Freight capacity $\le 20\%$):
     $$
     \sum_{i=1}^N x_{i,1} \le \lceil 0.20 \times N \rceil
     $$
   * Option B (Alternate Supplier capacity $\le 35\%$):
     $$
     \sum_{i=1}^N x_{i,2} \le \lceil 0.35 \times N \rceil
     $$
