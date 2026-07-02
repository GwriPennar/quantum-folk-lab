# EXP-002 Result

EXP-002 completed a transparent four-node Max-Cut reference experiment using exact enumeration, verified QUBO/Ising algebra, and genuine local Qiskit QAOA simulation.

## Environment

- Python: 3.13.5
- Qiskit: 2.4.2
- Qiskit Aer: 0.17.2
- SciPy: 1.18.0
- IBM Runtime: not installed or used
- Hardware/QPU: not used

## Exact Result

- Graph: `cycle4`
- Nodes: `[0, 1, 2, 3]`
- Edges: `(0, 1)`, `(1, 2)`, `(2, 3)`, `(3, 0)`
- Assignments enumerated: 16
- Exact maximum cut: 4.0
- Exact optimal bitstrings: `0101`, `1010`
- Canonical bitstring: `0101`

## QUBO And Ising Verification

All 16 assignments were checked. Direct cut values, QUBO values, Pauli cut expectations, and the negative minimisation energy agree under the documented sign convention.

The QAOA cost operator minimises `-H_cut`, where `H_cut = sum w_ij / 2 * (I - Z_i Z_j)`.

## QAOA Result

- Circuit: genuine local Qiskit `QAOAAnsatz`
- Depth/reps: 1
- Parameters: 2
- Optimiser: COBYLA
- Optimiser maximum iterations: 80
- Initial points: `[0.2, 0.2]`, `[0.5, 0.5]`, `[0.8, 0.3]`, `[1.0, 0.7]`
- Selected initial point: `[0.5, 0.5]`
- Optimal parameters: `[1.1780719862, 0.7853768025]`
- Expected cut value: 2.999999994
- Expected approximation ratio: 0.7499999985
- Shots: 4096
- Sampled best bitstring: `0101`
- Sampled best cut: 4.0
- Sampled-best approximation ratio: 1.0
- Optimal sample count across `0101` and `1010`: 2148
- Optimal sample probability: 0.5244140625
- Logical problem qubits: 4
- Classical bits after measurement: 4
- Circuit width: 8, using Qiskit total width: logical qubits plus classical bits after measurement
- Circuit depth: 15
- Transpiled depth: 15
- Two-qubit gate count: 8

## Limitations

This is a four-qubit ideal statevector simulation. It is not a hardware run and does not include device noise, queueing, calibration, topology, or readout effects. Sampling an optimal bitstring is not the same as achieving expected approximation ratio 1. Brute force remains the correct method for this tiny instance.
