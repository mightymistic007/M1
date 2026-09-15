
# M4 Track — Day 11: Prescriptive Option Ranking & Score Formulation

## 1. Ranking Objective

Each evaluated shipment produces three distinct candidate options (`OPT-A`, `OPT-B`, `OPT-C`). The solver evaluates and ranks these actions using a unified scalar Cost-to-Impact score $J_j$, ordering them from most optimal (Rank 1) to least optimal (Rank 3) while respecting batch-level capacity constraints.

---

## 2. Composite Score Formulation

For shipment $i$ evaluated under prescriptive action $j \in \{\text{OPT-A}, \text{OPT-B}, \text{OPT-C}\}$:

$$
J_{i,j} = C_{i,j} + \lambda \cdot \max\big(0, D_i - \Delta_j\big) + \Omega_{i,j}
$$

Where:

* $C_{i,j}$: Direct financial cost of option $j$ ($C_{i,j} = \text{BaseOrderCost}_i \times \text{Multiplier}_j$).
* $\lambda$: Delay breach penalty multiplier ($\$45.00/\text{day}$).
* $D_i$: Initial predicted delay duration in days ($p_{\text{delay}} \times 6$).
* $\Delta_j$: Days mitigated by option $j$ ($\Delta_A = 4$, $\Delta_B = 2$, $\Delta_C = 0$).
* $\max(0, D_i - \Delta_j)$: Net unmitigated delay days.
* $\Omega_{i,j}$: Penalty term for constraint violations:
  $$
  \Omega_{i,j} = \begin{cases} +\infty & \text{if } C_{i,j} > \$399.98 \text{ (Budget Cap Exceeded)} \\ 0 & \text{otherwise} \end{cases}
  $$

---

## 3. Option Archetypes & Tradeoff Hierarchy

| Rank Attribute              | Option A (Air Freight)                                                                                                                                                                                                    | Option B (Alt Supplier)                       | Option C (Buffer Delay)                           |
| :-------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------- | :------------------------------------------------ |
| **Option ID**         | `OPT-A`                                                                                                                                                                                                                 | `OPT-B`                                     | `OPT-C`                                         |
| **Primary Advantage** | Maximum transit compression (up to 4 days saved).                                                                                                                                                                         | Balanced cost/speed trade-off (2 days saved). | Zero direct expenditure increase (\$0 surcharge). |
| **Cost Surcharge**    | $+45\%$ over baseline.                                                                                                                                                                                                  | $+15\%$ over baseline.                      | $+0\%$ over baseline.                           |
| **Optimal Profile**   | Critical, high-delay shipments where penalty$> \$45/\text{day} \times 4$. | Moderate disruptions where 2 days mitigation eliminates penalty. | Low-risk shipments ($D_i \le 1$) or orders exceeding the \$399.98 cap. |                                               |                                                   |

---

## 4. Contract Schema Preservation

While options are sorted or evaluated by score $J_{i,j}$, the primary JSON return preserves the original list order (`OPT-A`, `OPT-B`, `OPT-C`) expected by the Application Team, with the optimal choice designated via the `optimal_assigned: true` boolean attribute.
