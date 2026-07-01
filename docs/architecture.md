# Architecture

The project is staged as a learning path before it becomes a music-inspired optimisation sandbox.

## Layers

1. Quantum fundamentals: small Qiskit circuits run locally with Aer in EXP-001.
2. Reference optimisation: EXP-002 will introduce a bounded Max-Cut example.
3. Synthetic music domain: deterministic symbolic melody families and transformations.
4. Similarity graph: interval, contour, and rhythm scores create weighted edges.
5. QUBO and exact solving: provider-independent binary optimisation remains the source of truth.
6. Future local QAOA: EXP-005A will add genuine local Qiskit QAOA and clearly separate it from the current classical fallback sampler.

Preprocessing remains classical. Quantum computing is tested only on bounded, inspectable circuit and optimisation kernels.

EXP-001 uses no cloud backend, no IBM account, no token, and no QPU job. It is intentionally noise-free so learners can inspect ideal circuit behaviour before later noise and hardware discussions.
