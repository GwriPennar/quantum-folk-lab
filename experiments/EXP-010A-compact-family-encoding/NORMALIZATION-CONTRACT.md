# EXP-010A QAOA normalization contract

Frozen: 2026-07-20, before formal compact equivalence evaluation or QAOA execution.

After the exact compact spectrum independently supplies `E_min` and `E_max`, the QAOA cost is:

`C_norm(y) = (E(y) - E_min) / (E_max - E_min)`.

Subtracting `E_min` adds only a global phase. Dividing by the positive spectral range rescales gamma.
Neither changes the exact optimum, state ordering, gap ordering, or degeneracy. The transformation
must not be altered after QAOA results are observed.

All scientific energy metrics must also be reported in original R2 units. Normalization is used
only to define a stable QAOA angle domain; it does not change the underlying scientific objective.
