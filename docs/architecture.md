# Architecture

The project is staged as a learning path before it becomes a music-inspired optimisation sandbox.

## Layers

1. Quantum fundamentals: small Qiskit circuits run locally with Aer in EXP-001.
2. Reference optimisation: EXP-002 uses a bounded Max-Cut example with exact enumeration, verified QUBO/Ising algebra, and genuine local Qiskit QAOA.
3. Synthetic music domain: deterministic symbolic melody families and transformations.
4. Similarity graph: interval, contour, and rhythm scores create weighted edges.
5. QUBO and exact solving: provider-independent binary optimisation remains the source of truth.
6. Future local QAOA: EXP-005A will add genuine local Qiskit QAOA and clearly separate it from the current classical fallback sampler.

Preprocessing remains classical. Quantum computing is tested only on bounded, inspectable circuit and optimisation kernels.

EXP-001 and EXP-002 use no cloud backend, no IBM account, no token, and no QPU job. EXP-002 is intentionally small: brute force is better for the four-node reference graph, while QAOA validates circuit construction, bit ordering, and result reporting before EXP-005A.
