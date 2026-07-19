# EXP-009A-R2 local QAOA report

The frozen p=1 local protocol completed with Qiskit 2.5.0 and no IBM service.

- Parameter order: `β[0]`, `γ[0]`.
- Frozen selected β: `1.1781497421205491`.
- Frozen selected γ: `0.22442462761826065`.
- Selected initial point: `[0.8, 0.3]`.
- Total optimizer function evaluations: 139 across four predeclared starts.
- Ideal optimum-class mass: `0.062494744573416805`.
- Seeded 4096-shot optimum-class mass: `0.06103515625`.
- Ideal feasible-subspace mass: `0.9999270070068652`.
- Seeded feasible-subspace mass: `1.0`.
- Ideal expected energy: `0.051557321668141344`.
- Shot expected energy: `0.05108773489208682`.
- Ideal four-lowest-feasible cumulative mass: `0.24997943889667615`.
- Shot four-lowest-feasible cumulative mass: `0.24951171875`.
- Ideal feasible energy/probability Spearman ρ: `0.9441176470588234`.
- Shot feasible energy/probability Spearman ρ: `0.14738429531859928`.
- Most frequent sampled bitstring: `01010110` with 274 counts.

The exact optimum class contains one state, so optimum-class mass is not weakened by optimum
degeneracy. However, the ideal distribution is almost uniform across the 16 feasible states. The
positive ideal rank relationship means higher-energy feasible states receive marginally greater
probability, not less, and the seeded shot rank statistic is weak. Feasibility concentration is the
clear p=1 signal; within-feasible energy ranking is not.

Exact enumeration remains authoritative. This local result is not evidence of musical truth,
authenticity, cultural superiority, hardware performance, or quantum advantage.
