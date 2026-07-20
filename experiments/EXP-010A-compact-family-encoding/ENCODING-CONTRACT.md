# EXP-010A compact encoding contract

Frozen: 2026-07-20, before formal compact equivalence evaluation.

EXP-010A is a data-informed successor to EXP-009A-R2. It reads only committed R2 aggregate evidence
and does not reopen the external dataset.

## Variables and order

One binary variable `y[f]` represents each family, in this fixed order:

1. Blackbird;
2. Bold Deserter;
3. Catherine Tyrrell;
4. The Merry Old Woman.

`y[f]=0` selects the first R2 setting and maps to R2 pair `10`. `y[f]=1` selects the second setting
and maps to pair `01`. Algebraically, `x[f,0]=1-y[f]` and `x[f,1]=y[f]`.

All 16 compact states map bijectively to all 16 one-hot-feasible R2 states. Every compact state is
valid. No one-hot penalty, invalid-state penalty, feasibility postselection, repair, or tune-specific
exception is permitted.

## Objective and conventions

The compact objective is derived only by substituting the algebraic mapping into the committed R2
musical objective. R2 feature vectors, pairwise distances, weights, and scientific energies remain
unchanged.

Compact QUBO convention:

`E(y)=offset + Σ_i Q[i,i]y_i + Σ_{i<j}Q[i,j]y_i y_j`.

Compact Ising convention:

`y_i=(1-z_i)/2`, with constant, linear `h_i`, and upper-triangular pair `J_ij` recorded separately.

All 16 mapped R2 musical, compact direct, QUBO, and Ising energies must agree within `1e-12`.
The complete compact spectrum must equal the committed R2 feasible spectrum, including optimum
class, degeneracy, and exact gap. Exact enumeration is authoritative.
