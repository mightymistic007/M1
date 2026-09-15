
# M4 Track — Day 3: Canonical Matrix & Linear Programming Constraints

## 1. Vector Variable Flattening

For a batch of $N$ shipments, define the continuous decision vector $\mathbf{x} \in \{0, 1\}^{3N}$:

$$
\mathbf{x} = \big[ x_{1,1}, x_{1,2}, x_{1,3}, x_{2,1}, x_{2,2}, x_{2,3}, \dots, x_{N,1}, x_{N,2}, x_{N,3} \big]^T
$$

Where index $(3(i-1) + j)$ represents shipment $i$ assigned to option $j \in \{1, 2, 3\}$.

---

## 2. Objective Function Vector Formulation

$$
\min_{\mathbf{x}} \mathbf{c}^T \mathbf{x}
$$

Where coefficient vector element $c_{i,j}$ is:

$$
c_{i,j} = C_{i,j} + \lambda \cdot \max(0, D_i - \Delta_j)
$$

* Cost penalty rate $\lambda = \$45.00/\text{day}$
* $C_{i,1} = 1.45 \cdot \text{BaseCost}_i, \quad \Delta_1 = 4$
* $C_{i,2} = 1.15 \cdot \text{BaseCost}_i, \quad \Delta_2 = 2$
* $C_{i,3} = 1.00 \cdot \text{BaseCost}_i, \quad \Delta_3 = 0$

---

## 3. Equality Constraints (Assignment Invariance)

Every shipment $i$ must receive exactly one mitigation action:

$$
\mathbf{A}_{eq} \mathbf{x} = \mathbf{b}_{eq}
$$

Where $\mathbf{A}_{eq} \in \mathbb{R}^{N \times 3N}$ is a block matrix of ones:

$$
\mathbf{A}_{eq}[i, 3(i-1) + 1 : 3(i-1) + 3] = [1, 1, 1], \quad \mathbf{b}_{eq} = \mathbf{1}_N
$$

---

## 4. Inequality Constraints (Capacity & Budget Caps)

$$
\mathbf{A}_{ub} \mathbf{x} \le \mathbf{b}_{ub}
$$

### A. Carrier Air Freight Expedited Capacity ($\le 20\%$)

$$
\sum_{i=1}^N x_{i,1} \le \lceil 0.20 \cdot N \rceil
$$

Row coefficient mapping:

$$
\mathbf{A}_{ub}[0, 3(i-1) + 1] = 1, \quad \mathbf{A}_{ub}[0, 3(i-1) + 2] = 0, \quad \mathbf{A}_{ub}[0, 3(i-1) + 3] = 0 \quad \forall i
$$

$$
\mathbf{b}_{ub}[0] = \lceil 0.20 \cdot N \rceil
$$

### B. Alternate Regional Supplier Capacity ($\le 35\%$)

$$
\sum_{i=1}^N x_{i,2} \le \lceil 0.35 \cdot N \rceil
$$

Row coefficient mapping:

$$
\mathbf{A}_{ub}[1, 3(i-1) + 2] = 1, \quad \text{zero elsewhere}
$$

$$
\mathbf{b}_{ub}[1] = \lceil 0.35 \cdot N \rceil
$$

### C. Individual Shipment Hard Budget Cap

For any shipment where $C_{i,j} > \text{budget\_max\_cap\_usd}$ (\$399.98), enforce:

$$
x_{i,j} = 0 \implies \text{upper\_bound}(x_{i,j}) = 0
$$

---

## 5. Decision Space Bounds

$$
x_k \in [0, 1] \quad \forall k \in \{1, \dots, 3N\}, \quad x_k \in \mathbb{Z} \text{ (Integer Binary)}
$$
