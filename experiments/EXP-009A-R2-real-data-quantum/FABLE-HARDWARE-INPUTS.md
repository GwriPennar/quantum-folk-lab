# Fable hardware-design inputs

This package contains validated local evidence for revising the proposed “Four Families, One
Quantum Job” design. It does not choose a primary hardware metric and does not authorize IBM access.

## Exact and local summary

- Logical width: 8 qubits.
- Untranspiled p=1 nonzero two-qubit interactions: 28.
- Exact optimum: `01100110`; class size 1.
- Exact gap: `0.005944337816346`.
- Frozen β: `1.1781497421205491`; frozen γ: `0.22442462761826065`.
- Ideal feasible mass: `0.9999270070068652`.
- Ideal optimum mass: `0.062494744573416805`.
- Ideal four-lowest-feasible mass: `0.24997943889667615`.
- Ideal feasible energy/probability Spearman ρ: `0.9441176470588234`.

The ideal distribution is nearly uniform within the feasible subspace. Feasibility concentration is
strong, while within-feasible energy ordering is not favorable.

## Preregistered 4096-shot detectability

- Detectable at estimated power ≥ 0.80: feasible_subspace_mass, optimum_class_mass, four_lowest_feasible_mass, expected_energy.
- Not detectable at estimated power ≥ 0.80: feasible_energy_probability_spearman.

Mass metrics may be detectable primarily because the circuit concentrates on the constrained
subspace; detectability alone does not make them scientifically primary. Fable should use these
results to revise the protocol before any separately authorized hardware activity.

No IBM Runtime client, backend, credential, session, simulator service, or QPU was contacted.
