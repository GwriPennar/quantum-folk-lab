# EXP-010A compact local-QAOA report

The frozen four-qubit p=1 protocol evaluated all 33,153 grid pairs, refined the sixteen
predeclared best grid points with bounded L-BFGS-B, and completed one seeded 4096-shot local sample.

- Frozen gamma: `3.31779751919292`.
- Frozen beta: `2.47650529998603`.
- Uniform-16 raw energy: `0.0510055654039282`.
- Ideal raw energy: `0.0402356614041937`.
- Shot raw energy: `0.0402702442162102`.
- Ideal relative expected-energy improvement: `0.599911842992114`.
- Shot relative expected-energy improvement: `0.597985489842336`.
- Ideal optimum mass: `0.303828616378613`.
- Shot optimum mass: `0.303955078125`.
- Ideal four-lowest mass: `0.669233263634782`.
- Shot four-lowest mass: `0.6748046875`.
- Ideal energy/probability Spearman rho: `-0.932352941176471`.
- Shot energy/probability Spearman rho: `-0.932352941176471`.
- Ideal total-variation distance from uniform-16: `0.529267384720919`.
- Shot total-variation distance: `0.52294921875`.
- Most frequent sampled compact state: `1010`, 1245 of 4096 shots.
- Maximum analytic/Qiskit probability disagreement: `2.22044604925031e-16`.

Detectability power is 1.0 for the primary relative-energy metric and for each predeclared
secondary metric. The hardware-readiness gate passes. Exact compact enumeration remains
authoritative; this is not quantum advantage or a claim of musical truth.

No IBM service, credential, backend, session, or QPU was accessed.
