# EXP-010A compact local-QAOA protocol

Frozen: 2026-07-20, after exact compact equivalence passed and before QAOA execution.

## Circuit and objective

- four logical qubits in the frozen family order;
- uniform-superposition initial state;
- standard X mixer;
- depth `p=1`;
- normalized cost `C_norm=(E-E_min)/(E_max-E_min)`;
- minimize exact expected normalized energy;
- no penalties, conditioning, postselection, repair, or optimum-mass objective;
- final local Qiskit statevector verification and seeded 4096-shot sampling;
- simulator and transpiler seed 42;
- no IBM service or hardware.

## Deterministic bounded parameter selection

- gamma domain: `[0,16π]`;
- beta domain: `[0,π]`;
- gamma grid: 257 inclusive points;
- beta grid: 129 inclusive points;
- evaluate every one of the 33,153 grid pairs with exact statevectors;
- select the 16 lowest expected-energy grid points, tied by lower gamma then beta;
- refine all 16 with SciPy L-BFGS-B using the exact frozen bounds;
- L-BFGS-B maximum iterations 500, `ftol=1e-15`, `gtol=1e-12`, and `maxls=20`;
- select lowest refined exact expected energy, tied by lower gamma then beta.

Domains, grid, objective, starts, and selection rules may not change after observing results.

## Baselines and metrics

The principal null is uniform over the 16 compact states. The primary metric is:

`R=(E_uniform16-E_qaoa)/(E_uniform16-E_min)`.

Secondary metrics are optimum mass (baseline `1/16`), four-lowest mass (`4/16`), raw and normalized
expected energy, energy/probability Spearman ρ (favorable direction negative), total-variation
distance from uniform-16, most frequent state, all state probabilities, and Wilson intervals for
shot masses.

After parameters freeze, run 10,000 multinomial resamples with 4096 shots and seed 42. Alternative
is the frozen ideal compact distribution; null is uniform-16. At one-sided α=0.05, favorable
directions are higher for R and masses and lower for Spearman ρ. Power is the alternative fraction
crossing the applicable uniform-null 95th or 5th percentile.

Hardware-readiness requires exact equivalence, ideal `R≥0.10`, primary power `≥0.80`, ideal energy
below uniform-16, and no postselection. Secondary metrics cannot override the primary gate.
