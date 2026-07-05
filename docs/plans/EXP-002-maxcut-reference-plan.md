# EXP-002 Max-Cut Reference Plan

## Current Base

- Start from `main` at EXP-001 squash merge `cb2726e95437c72dc5b32e272714a7af9f5ce06c`.
- Work on `codex/exp-002-maxcut-reference`.
- Keep `.venv-qiskit` ignored and reuse it for optional quantum validation.
- Do not use IBM Runtime, credentials, cloud backends, or QPU access.

## Files To Add Or Modify

- Add `src/quantum_folk_lab/maxcut.py` for graph representation, assignment handling, bit-order conversion, and cut values.
- Add `src/quantum_folk_lab/maxcut_exact.py` for exhaustive enumeration.
- Add `src/quantum_folk_lab/maxcut_ising.py` for QUBO and Pauli/Ising construction and exhaustive equivalence checks.
- Add `src/quantum_folk_lab/maxcut_qaoa.py` for genuine local Qiskit QAOA execution.
- Extend `src/quantum_folk_lab/cli.py` with `maxcut-list`, `maxcut-exact`, `maxcut-qaoa`, and `maxcut-compare`.
- Add tests for non-quantum exact logic and quantum mapping/QAOA logic.
- Update EXP-002 experiment docs, machine-readable results, README, architecture, roadmap, research roadmap, and IBM setup docs.
- Add `notebooks/03_maxcut_reference.ipynb` as a thin package-function companion.
- Extend CI quantum job to include EXP-002 CLI smoke coverage while preserving split installs.

## Graph Definition

- Primary registered graph: `cycle4`.
- Fixed node order: `[0, 1, 2, 3]`.
- Weighted edges: `(0, 1, 1.0)`, `(1, 2, 1.0)`, `(2, 3, 1.0)`, `(3, 0, 1.0)`.
- Direct exact optimum should be cut value `4.0` with complementary optima including `0101` and `1010`.

## Classical Objective

For assignment `x` in graph-node order:

`cut(x) = sum w_ij if x_i != x_j else 0`.

The exact solver will enumerate every bit assignment, calculate the cut directly, collect all optimal assignments, and report deterministic canonical/complement representatives.

## QUBO And Ising Conventions

For each edge:

`different(i, j) = x_i + x_j - 2 x_i x_j`.

- QUBO value is the positive Max-Cut objective: `sum w_ij * different(i, j)`.
- Pauli cut operator is `H_cut = sum w_ij / 2 * (I - Z_i Z_j)`.
- QAOA optimisation minimises the negative cut operator `H_min = -H_cut`.
- Expected cut value is recovered as `-expected_energy` for `H_min`.
- Exhaustive verification will compare direct cut, QUBO value, Pauli basis expectation, and negative-cost expectation for all 16 assignments.

## Bit Order Convention

- Internal assignment order follows graph node order: tuple index `k` maps to node `nodes[k]`.
- Displayed bitstrings are left-to-right in graph node order, e.g. tuple `(0, 1, 0, 1)` displays as `0101`.
- Qiskit qubit `k` represents graph node `nodes[k]`.
- Qiskit sampler count keys are decoded through one conversion function. Because measured classical strings are displayed most-significant classical bit first, the decoder reverses count keys when converting back to graph-node order.
- Tests will fail if `0101` and `1010` are swapped or lost by incorrect reversal.

## QAOA Execution Path

- Construct `SparsePauliOp` for `H_min`.
- Build `QAOAAnsatz(cost_operator, reps=depth)` with the default X mixer.
- Use `StatevectorEstimator` to evaluate exact statevector expectation during optimisation.
- Use `scipy.optimize.minimize(method="COBYLA")` with a small fixed set of initial points and max iteration bound.
- Select the run with the lowest expected energy, equivalent to highest expected cut.
- Bind the selected parameters, add measurements to the final circuit, and sample with `StatevectorSampler(seed=42)` for 4096 finite shots.
- Distinguish exact enumeration, statevector expectation, and finite-shot sampling in results and docs.

## Optimiser And Initialisation Strategy

- Primary depth: `p = 1`.
- Registered initial points: a small deterministic grid such as `[0.2, 0.2]`, `[0.5, 0.5]`, `[0.8, 0.3]`, `[1.0, 0.7]` in QAOA parameter order.
- COBYLA maximum iterations kept small enough for local and CI runs.
- Record every start, function evaluations, selected start, optimal parameters, and elapsed time.

## Exact Validation Method

- Exact enumeration must derive the optimum without hard-coding answers.
- Equivalence verification must cover all 16 assignments and fail loudly on sign, offset, or bit-order errors.
- Exact solver remains the source of truth for approximation ratios and optimal-sample probability.

## Test Plan

- Non-quantum tests: graph validation, assignment validation, cut values, exact enumeration, complement handling, canonical ordering, `cycle4` optimum, exact result schema, CLI/exact behaviour without Qiskit imports.
- Quantum tests marked `pytest.mark.quantum`: QUBO/Ising equivalence over all 16 assignments, bit-order conversion, `QAOAAnsatz` construction, measured circuit construction, sampler-count decoding, optimal-probability aggregation, registered p=1 run, and missing-Qiskit error handling.

## Result Schema

Machine-readable QAOA results will include experiment ID, graph metadata, execution path, genuine-Qiskit flag, simulator type, package versions, seeds, shots, depth, parameter count, optimiser metadata, initial points, selected point, optimal parameters, exact optimum, exact optimal bitstrings, expected cut and ratio, sampled best bitstring and ratio, optimal sample count/probability, counts, circuit width/depth/transpiled depth, operation counts, two-qubit gate count, elapsed seconds, pass/caution status, and limitations.

## Documentation Changes

- Mark EXP-002 complete only after validation succeeds.
- Explain that Max-Cut is a tiny transparent reference benchmark and brute force is superior for this instance.
- State that the quantum circuit is a bounded reference benchmark, ideal simulation is not hardware, and sampling an optimal string is not the same as expected approximation ratio 1.
- Keep EXP-005A as the future domain-specific QAOA milestone.

## CI Changes

- Standard CI remains `.[dev]`, non-quantum tests, Ruff, mypy, and safety scan.
- Quantum CI remains `.[dev,quantum]`, quantum tests, local CLI smoke checks.
- Add EXP-002 quantum CLI smoke only if it remains fast.
- No IBM Runtime, secrets, cloud execution, or hardware jobs.

## Safety Checks

- No private source data, ABC, audio, MIDI, PDF documents, credential files, contact addresses, private identifiers, tokens, local absolute paths, or notebook checkpoints.
- Run `python scripts/check_public_safety.py` before staging and again before commit.
- Stage only EXP-002 and necessary shared changes.

## Stop Conditions

- Stop if QAOA cannot be made to sample an exact optimum under the documented bounded strategy after verifying bit order, Hamiltonian sign, offsets, and optimiser convergence.
- Stop if current Qiskit APIs differ from the installed stable stack in a way that would require adding unplanned packages.
- Stop if validation reveals private or unrelated files in the worktree.
