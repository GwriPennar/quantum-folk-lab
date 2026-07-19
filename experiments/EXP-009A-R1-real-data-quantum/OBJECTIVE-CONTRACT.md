# EXP-009A-R1 objective contract

Frozen: 2026-07-19, before successor access to the selected real-data records or calculation of a
successor result.

EXP-009A-R1 inherits the EXP-009A mathematical objective unchanged. Only the parser treatment of
well-formed inline key metadata is revised.

`E(x) = 7 × Σ_f (x[f,0] + x[f,1] - 1)^2 + Σ_{i<j,cross-family} d[i,j] x_i x_j`

- four families with two settings each;
- eight binary variables and exact enumeration of all 256 assignments;
- exactly one selected setting per family;
- `A = 7` and `B = 1`;
- nine uniformly weighted, bounded EXP-009A aggregate features;
- direct/QUBO/Ising agreement tolerance `1e-10`;
- no data-dependent coefficient, weight, feature, or normalization change.

The original data-independent penalty proof remains authoritative: a feasible assignment contains
six cross-family distances, each at most 1, and therefore costs at most 6. Any infeasible assignment
incurs penalty at least 7 and has nonnegative musical cost. No infeasible state can be globally
optimal.

Exact enumeration remains authoritative. A later bounded local QAOA run, if the exact gate passes,
is a heuristic comparison and does not establish musical truth, authenticity, or quantum advantage.

