# EXP-009A objective contract

Frozen: 2026-07-19, before feature extraction, exhaustive enumeration, or local QAOA.

## Question and variables

Choose exactly one of two reproducibly selected settings from each of four provisional tune
families while minimizing coarse pairwise feature incoherence. The eight binary variables use the
ordering in the merged EXP-008B manifest: Blackbird 199/200, Bold Deserter 291/1791, Catherine
Tyrrell 336/337, and Merry Old Woman 799/800.

For family `f` and setting `s`, `x[f,s] ∈ {0,1}`. The hard constraint is
`x[f,0] + x[f,1] = 1` for every family.

## Frozen objective

`E(x) = A Σ_f (x[f,0] + x[f,1] - 1)^2 + B Σ_{i<j,cross-family} d[i,j] x[i]x[j]`

- `B = 1`.
- `d[i,j]` is the uniform-weight squared Euclidean distance over the nine features frozen in
  `FEATURE-CONTRACT.md`.
- Same-family musical distances are excluded; their interaction is solely the hard one-hot penalty.
- No coefficient, weight, normalization, or parser rule may change after results are observed.

## One-hot penalty proof

Every feature is bounded to `[0,1]`; nine uniform weights sum to 1. Therefore every pairwise squared
distance lies in `[0,1]`. A feasible assignment selects four variables and contains exactly six
cross-family pairs, so every feasible musical cost is at most `6B = 6`.

Any infeasible assignment violates at least one integer one-hot equation, making its squared penalty
at least 1. Pairwise costs are nonnegative. Setting `A = 7` therefore gives every infeasible state
energy at least 7 while every feasible state has energy at most 6. Thus no infeasible state can be a
global optimum. This proof is independent of observed feature values.

Frozen coefficients: `A = 7`, `B = 1`.

## QUBO convention

`E = offset + Σ_i Q[i,i]x_i + Σ_{i<j}Q[i,j]x_ix_j` with upper-triangular coefficients:

- offset `= 4A = 28`;
- diagonal `Q[i,i] = -A = -7`;
- same-family off-diagonal `Q[i,j] = 2A = 14`;
- cross-family off-diagonal `Q[i,j] = d[i,j]`.

## Ising convention

Use `x_i = (1-z_i)/2`, where `z_i ∈ {-1,+1}` is the Pauli-Z eigenvalue. Record the Ising constant,
linear `h_i`, and pairwise `J_ij` separately and require direct/QUBO/Ising agreement within `1e-10`
for all 256 assignments.

Exact enumeration is authoritative. QAOA is a bounded local heuristic and does not find “truth.”
This objective is not EXP-005A: it selects whole external settings using coarse set coherence,
whereas EXP-005A's registered synthetic tune-family objective and evidence remain unchanged.
