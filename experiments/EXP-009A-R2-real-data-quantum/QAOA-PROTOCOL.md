# EXP-009A-R2 local QAOA protocol

Frozen: 2026-07-19, after the authoritative exact gate passed and before any R2 QAOA execution.

## Fixed execution

- QAOA depth: `p = 1`;
- logical width: 8 qubits;
- optimizer: SciPy COBYLA;
- maximum function evaluations per start: 80;
- COBYLA initial trust-region radius: `rhobeg = 0.5`;
- deterministic simulator and transpiler seed: 42;
- finite-shot sample size: 4096;
- exact statevector distribution recorded where supported;
- local Qiskit primitives only; no IBM service or hardware.

Predeclared initial points in Qiskit's deterministic ansatz parameter order:

1. `[0.2, 0.2]`;
2. `[0.5, 0.5]`;
3. `[0.8, 0.3]`;
4. `[1.0, 0.7]`.

The attempt with the lowest estimator energy is selected, with lexicographic initial-point order as
the deterministic tie-break. No parameter, start, iteration limit, seed, or metric may be changed
after observing the result. A poor result must be preserved.

## Predeclared outputs

Record parameter names and selected values, including identified γ and β; optimizer attempts and
function evaluations; ideal and seeded shot distributions; optimum-class mass; feasible-subspace
mass; expected energy; most frequent bitstring; cumulative mass for the four lowest-energy feasible
states; Spearman correlation between feasible-state probability and exact energy; uniform
baselines; and 95% binomial Wilson intervals for shot-derived optimum, feasible, and low-energy
masses.

Exact enumeration remains authoritative. Degeneracy and metric limitations must be reported. No
quantum advantage, musical truth, authenticity, cultural ranking, or hardware performance is
claimed.
