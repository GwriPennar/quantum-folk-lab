# EXP-002 Max-Cut Reference

Status: complete

EXP-002 validates the quantum optimisation pipeline on a standard four-node Max-Cut problem before applying QAOA to the repository's more domain-specific tune-family QUBO work.

## Graph

Primary registered graph: `cycle4`

- Nodes: `0, 1, 2, 3`
- Edges: `(0, 1)`, `(1, 2)`, `(2, 3)`, `(3, 0)`
- Edge weights: `1.0`
- Fixed node order: `[0, 1, 2, 3]`

The exact maximum cut is `4.0`. The complementary optimal bitstrings are `0101` and `1010` under graph-node order.

## Conventions

Assignments are displayed left-to-right in graph-node order. Qiskit qubit `k` maps to graph node `nodes[k]`. Qiskit count keys are decoded through one conversion layer because measured classical strings are displayed most-significant classical bit first.

For each edge:

```text
different(i, j) = x_i + x_j - 2 x_i x_j
```

The direct cut objective and QUBO value are maximised. The Pauli cut operator is:

```text
H_cut = sum w_ij / 2 * (I - Z_i Z_j)
```

The QAOA optimiser minimises `-H_cut`; the expected cut is recovered as `-expected_energy`.

## Commands

```powershell
qfl maxcut-list
qfl maxcut-exact --graph cycle4
qfl maxcut-qaoa --graph cycle4 --depth 1 --shots 4096
qfl maxcut-compare --graph cycle4 --depth 1 --shots 4096
```

The exact command is available without Qiskit. The QAOA commands require optional local quantum dependencies:

```powershell
python -m pip install -e ".[dev,quantum]"
```

No IBM account, token, Runtime service, cloud backend, or QPU is used.

## Results

See `RESULT.md` and `results/`.

The registered p=1 run uses `QAOAAnsatz`, `SparsePauliOp`, `StatevectorEstimator` for exact statevector expectation during optimisation, `scipy.optimize.minimize(method="COBYLA")`, and `StatevectorSampler` for finite-shot sampling.

The sampled best bitstring is optimal, but the expected approximation ratio is about `0.75`, not `1.0`. These metrics are intentionally kept separate.

## Interpretation

Brute force is superior for this tiny instance. The quantum circuit is educational and validates the local Qiskit plumbing, bit ordering, sign conventions, and reporting schema. No quantum advantage is claimed, and ideal simulation does not represent hardware noise.
