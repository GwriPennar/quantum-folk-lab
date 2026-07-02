# EXP-002 Max-Cut Reference Review

## Recommendation

PASS - READY FOR HUMAN MERGE DECISION

This recommendation is advisory. Gwri makes the merge decision.

## Reviewed Branch And Commit

- Branch: `codex/exp-002-maxcut-reference`
- Original reviewed PR head: `0e7944d08665fd2ec461823d4a701fe62cc881c2`
- PR: `https://github.com/GwriPennar/quantum-folk-lab/pull/2`
- PR state at review: open draft, mergeable, GitHub Actions checks passing

A minimal review fix was made after review to clarify Qiskit circuit width and result provenance. See "Changes Made".

## Files Reviewed

- `.github/workflows/ci.yml`
- `README.md`
- `docs/architecture.md`
- `docs/ibm-quantum-setup.md`
- `docs/ibm_quantum_setup.md`
- `docs/learning-roadmap.md`
- `docs/plans/EXP-002-maxcut-reference-plan.md`
- `docs/roadmap.md`
- `experiments/EXP-002-maxcut-reference/README.md`
- `experiments/EXP-002-maxcut-reference/RESULT.md`
- `experiments/EXP-002-maxcut-reference/results/maxcut-exact.json`
- `experiments/EXP-002-maxcut-reference/results/maxcut-qaoa-p1.json`
- `experiments/EXP-002-maxcut-reference/results/maxcut-comparison.json`
- `notebooks/03_maxcut_reference.ipynb`
- `pyproject.toml`
- `scripts/check_public_safety.py`
- `src/quantum_folk_lab/cli.py`
- `src/quantum_folk_lab/maxcut.py`
- `src/quantum_folk_lab/maxcut_exact.py`
- `src/quantum_folk_lab/maxcut_ising.py`
- `src/quantum_folk_lab/maxcut_qaoa.py`
- `tests/test_exp002_maxcut_exact.py`
- `tests/test_exp002_qiskit_maxcut.py`

## Mathematical Verification

The registered graph is `cycle4` with nodes `[0, 1, 2, 3]` and weighted edges `(0, 1, 1.0)`, `(1, 2, 1.0)`, `(2, 3, 1.0)`, `(3, 0, 1.0)`.

The following table was independently regenerated from `verify_equivalence(CYCLE4)` during review.

| Bitstring | Direct cut | QUBO value | Pauli cut expectation | Minimisation energy |
| --- | ---: | ---: | ---: | ---: |
| 0000 | 0.0 | 0.0 | 0.0 | -0.0 |
| 0001 | 2.0 | 2.0 | 2.0 | -2.0 |
| 0010 | 2.0 | 2.0 | 2.0 | -2.0 |
| 0011 | 2.0 | 2.0 | 2.0 | -2.0 |
| 0100 | 2.0 | 2.0 | 2.0 | -2.0 |
| 0101 | 4.0 | 4.0 | 4.0 | -4.0 |
| 0110 | 2.0 | 2.0 | 2.0 | -2.0 |
| 0111 | 2.0 | 2.0 | 2.0 | -2.0 |
| 1000 | 2.0 | 2.0 | 2.0 | -2.0 |
| 1001 | 2.0 | 2.0 | 2.0 | -2.0 |
| 1010 | 4.0 | 4.0 | 4.0 | -4.0 |
| 1011 | 2.0 | 2.0 | 2.0 | -2.0 |
| 1100 | 2.0 | 2.0 | 2.0 | -2.0 |
| 1101 | 2.0 | 2.0 | 2.0 | -2.0 |
| 1110 | 2.0 | 2.0 | 2.0 | -2.0 |
| 1111 | 0.0 | 0.0 | 0.0 | -0.0 |

Findings:

- All 16 assignments are enumerated.
- Maximum cut is `4.0`.
- The only optimal project bitstrings are `0101` and `1010`.
- Complementary representatives are handled consistently: canonical `0101`, complement `1010`.

## Bit And Qubit Ordering

Project assignment order follows graph node order. Tuple index `k` maps to graph node `nodes[k]`, and displayed bitstrings are left-to-right in that same order.

Qiskit qubit `k` represents graph node `nodes[k]`. Qiskit count keys are decoded centrally in `qiskit_key_to_assignment()` and `decode_counts()` by reversing measured count keys before converting to project bitstrings. Tests pin the worked examples:

- project assignment `(0, 1, 0, 1)` displays as `0101`;
- the corresponding Qiskit count key is `1010`;
- decoded counts `{ "1010": 3, "0101": 5 }` become project counts `{ "0101": 3, "1010": 5 }`.

## QUBO, Ising, Sign And Offset Verification

The QUBO implementation uses `x_i + x_j - 2 x_i x_j` for every edge. The Pauli cut operator is documented and implemented as:

`H_cut = sum w_ij / 2 * (I - Z_i Z_j)`

For an equal-bit edge this contributes `0`; for a differing-bit edge it contributes `w_ij`. The constant `I` term is included explicitly in `build_cut_operator()`, so reported Pauli expectations match direct cut values rather than omitting the offset.

QAOA minimises `-H_cut`; therefore expected cut is recovered as `-expected_energy`. The all-assignment table above verifies the sign and offset for every basis state.

## QAOA Authenticity

The implementation genuinely uses the local Qiskit path described in the PR:

- `SparsePauliOp` in `build_cut_operator()` and `build_minimization_operator()`;
- `QAOAAnsatz` in `build_qaoa_ansatz()`;
- `StatevectorEstimator` for objective evaluation during parameter optimisation;
- `StatevectorSampler` for finite-shot sampling after parameter selection;
- SciPy `minimize(..., method="COBYLA")` for optimisation.

No hard-coded optimum or classical shortcut is used inside the QAOA result path. Exact enumeration is used as ground truth for scoring and probability aggregation, which is appropriate and documented.

## Reproducibility Results

Registered settings:

- QAOA depth: `p=1`
- Shots: `4096`
- Seed: `42`
- Optimiser: COBYLA
- Max iterations: `80`
- Initial points: `[0.2, 0.2]`, `[0.5, 0.5]`, `[0.8, 0.3]`, `[1.0, 0.7]`
- Selected initial point: `[0.5, 0.5]`
- Optimal parameters: `[1.1780719862, 0.7853768025]`

The registered workflow reproduced the stored values exactly for rounded deterministic outputs and seeded counts. The only expected difference is `elapsed_seconds`.

Tolerance guidance:

- exact cut, best sampled cut, assignment lists, counts, seed, shots, and package versions should match exactly for the same environment;
- floating values stored to 10 decimal places should be accepted within `1e-8` across compatible Qiskit/SciPy patch environments;
- elapsed seconds should not be treated as reproducibility evidence.

## Expected Versus Sampled Result

The project correctly distinguishes expected and sampled metrics:

- Expected cut: `2.999999994`
- Expected approximation ratio: `0.7499999985`
- Sampled best bitstring: `0101`
- Sampled best cut: `4.0`
- Sampled-best approximation ratio: `1.0`
- Optimal sample count across `0101` and `1010`: `2148`
- Optimal sample probability: `0.5244140625`

Sampling one optimal bitstring does not make the expected approximation ratio equal to `1.0`. The expected metric remains approximately `0.75` for the registered p=1 state.

## Circuit Width Explanation

The Max-Cut problem has four logical problem qubits, one per graph node. The reported Qiskit circuit width is `8` because `QuantumCircuit.width()` returns total circuit width, including classical bits after measurement. The measured circuit has:

- logical problem qubits: `4`;
- classical bits: `4`;
- total Qiskit width: `8`;
- circuit depth: `15`;
- transpiled depth: `15`;
- two-qubit gate count: `8`.

A review fix added explicit `logical_problem_qubits`, `classical_bit_count`, `run_identifier`, `result_schema_version`, and `circuit_width_definition` fields, plus tests and docs, so the result does not imply eight problem qubits.

## Single Implementation Path

CLI commands, tests, notebook, and stored JSON all route through package functions in `src/quantum_folk_lab/maxcut*.py`. The notebook is a thin companion and does not duplicate solver or QAOA logic. Stored JSON was regenerated from the CLI after the review fix.

## Stored Result Provenance

Stored QAOA results record Python, Qiskit, Aer, SciPy, graph name, edges, weights, QAOA depth, optimiser, max iterations, initial points, selected start, seed, shots, schema version, and run identifier. They intentionally do not record machine-specific local paths or private environment details.

## Validation Commands

- `python -m pytest -m "not quantum"` -> `18 passed, 2 skipped`
- `.venv-qiskit\Scripts\python.exe -m pytest -m quantum` -> `15 passed, 18 deselected`, with Qiskit-internal deprecation warnings from `QAOAAnsatz`/`NLocal`
- `python -m ruff check .` -> passed
- `python -m ruff format --check .` -> `56 files already formatted`
- `python -m mypy` -> passed, 50 source files
- `python scripts/check_public_safety.py` -> passed
- `qfl doctor` -> Python 3.13.5, Qiskit 2.4.2, Aer 0.17.2, IBM Runtime not installed
- `qfl maxcut-list` -> passed
- `qfl maxcut-exact --graph cycle4` -> passed
- `qfl maxcut-qaoa --graph cycle4 --depth 1 --shots 4096` -> passed
- `qfl maxcut-compare --graph cycle4 --depth 1 --shots 4096` -> passed

GitHub Actions for PR #2 were also green at the start of review.

## Safety Findings

No IBM Runtime dependency, cloud backend, hardware execution, QPU job, credentials, private dataset, or unsupported quantum-advantage claim was introduced. The repository continues to state that brute force is better for this tiny graph and that EXP-002 is an ideal local simulator reference.

## EXP-005A Boundary

EXP-002 does not determine the future tune-family QUBO formulation. EXP-005A still requires separate review of variables, objective, constraints, penalty weights, solution interpretation, classical baseline, and whether any Max-Cut infrastructure is mathematically reusable.

EXP-005A was not started during this review.

## Changes Made

Minimal EXP-002-scope review fixes were made:

- clarified Qiskit circuit width and logical problem qubits in `src/quantum_folk_lab/maxcut_qaoa.py`;
- added run/schema provenance fields to QAOA result output;
- pinned width/provenance expectations in `tests/test_exp002_qiskit_maxcut.py`;
- updated EXP-002 README and RESULT documentation;
- regenerated stored EXP-002 JSON result files;
- created this review report.

## Remaining Limitations

- EXP-002 remains a four-node ideal local simulation and not a hardware result.
- Qiskit emits deprecation warnings from `QAOAAnsatz` internals in version 2.4.2; the implementation itself uses current V2 primitives for estimator and sampler execution.
- No quantum advantage is claimed or implied.
