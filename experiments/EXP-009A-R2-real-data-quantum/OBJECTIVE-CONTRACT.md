# EXP-009A-R2 objective contract

Frozen: 2026-07-19, before R2 access to the selected records or result calculation.

R2 inherits the EXP-009A mathematical objective unchanged:

`E(x) = 7 × Σ_f (x[f,0] + x[f,1] - 1)^2 + Σ_{i<j,cross-family} d[i,j] x_i x_j`

- four families and two settings per family;
- eight binary variables;
- `A = 7` and `B = 1`;
- nine uniformly weighted bounded aggregate features;
- direct/QUBO/Ising agreement tolerance `1e-10`;
- exhaustive enumeration of all 256 assignments;
- exact enumeration as scientific authority.

No coefficient, feature weight, or normalization may change after the R2 result is observed.

The inherited proof remains data-independent: every feasible assignment has six cross-family
distances bounded by 1 and therefore energy at most 6. Every infeasible assignment incurs penalty
at least 7 plus nonnegative musical cost. Hence every global optimum is feasible.

A bounded local p=1 QAOA run may proceed only after the exact gate passes. It is a heuristic
comparison, not musical truth, authenticity, cultural ranking, or evidence of quantum advantage.
