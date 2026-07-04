# EXP-005A Tune-Family QUBO And Local Qiskit QAOA Plan

Status: revised and reviewed; awaiting final human approval before implementation. This document is a mathematical and experimental design plan, not implementation evidence.

Reviewed base: `38e07a00867d5d6fe05760abf35ef3943a1df949`

Merged review addressed: `docs/reviews/EXP-005A-tune-family-qubo-plan-review.md`

Second review addressed: `docs/reviews/EXP-005A-revised-plan-second-review.md`

## Purpose

EXP-005A will replace or clearly separate the current deterministic pseudo-sampling path from a genuine local Qiskit QAOA experiment on the repository's synthetic tune-family QUBO.

This plan now governs both:

- the tune-family mathematical formulation; and
- the future local-Qiskit execution route.

The eventual implementation must remain local, synthetic, and educational. It must use no IBM account, no IBM Runtime service, no cloud backend, no hardware execution, and no QPU job. The exact classical solver remains the source of truth.

## Plain-English Summary

EXP-005A asks a small optimiser question:

Given eight synthetic tunes generated as two known families, can a binary optimisation model split the tunes into two unlabeled groups so that similar tunes stay together, dissimilar tunes separate, and the partition does not collapse into a trivial all-in-one assignment?

The known family labels are used only after optimisation to score the answer. They are not part of the objective.

## Correct Mathematical Formulation

EXP-005A is a two-family signed graph-partitioning or correlation-style QUBO over a bounded synthetic tune fixture.

EXP-005A is not direct Max-Cut.

The formulation expresses:

- similar tune pairs prefer the same partition;
- dissimilar tune pairs prefer different partitions;
- a balance term discourages trivial assignments;
- the two partition labels are interchangeable;
- known synthetic family labels are evaluation truth only.

Max-Cut infrastructure from EXP-002 can be reused for exact enumeration patterns, bit-order checks, QUBO/Ising verification discipline, local Qiskit circuit construction, and result reporting. EXP-002's Max-Cut objective, positive cut maximisation convention, approximation-ratio language, and `H_cut = sum w/2 * (I - Z_i Z_j)` Hamiltonian are not mathematically reusable without alteration.

## Registered Fixture

Primary fixture identifier: `synthetic-two-family-v1-seed42`

Generator:

- function: `generate_benchmark(seed=42, variants_per_family=4)`
- source: `src/quantum_folk_lab/domain/synthetic.py`
- tune count: `8`
- generated families: `2`
- variants per family: `4`
- evaluation labels: equivalent to `00001111`
- labels enter evaluation only after optimisation
- source data: deterministic synthetic pitch and duration sequences only

Fixed human-readable tune order:

| Index | Tune identifier | Family label for evaluation | Role |
| ---: | --- | ---: | --- |
| 0 | `fam_a_base` | 0 | family A base |
| 1 | `fam_a_transposed` | 0 | family A transposition |
| 2 | `fam_a_substitution` | 0 | family A pitch substitution |
| 3 | `fam_a_rhythm` | 0 | family A rhythm variant |
| 4 | `fam_b_base` | 1 | family B base |
| 5 | `fam_b_transposed` | 1 | family B transposition |
| 6 | `fam_b_inserted` | 1 | family B insertion variant |
| 7 | `fam_b_deleted` | 1 | family B deletion variant |

Ambiguity/noise examples:

- `fam_a_rhythm` changes duration while retaining the family-A pitch outline. It tests whether rhythm variation weakens similarity without causing a family split.
- `fam_b_inserted` changes sequence length by inserting a note. It tests whether edit-distance similarity tolerates local expansion.
- `fam_b_deleted` changes sequence length by deleting a note. It tests whether edit-distance similarity tolerates local contraction.

These examples are useful because they create non-identical but still family-related variants. The optimiser must recover family structure from pairwise evidence, not exact sequence equality.

## Feature And Similarity Representation

Tune representation:

- pitch representation: integer pitch offsets stored in `NoteEvent.pitch`;
- duration representation: positive integer durations stored in `NoteEvent.duration`;
- interval representation: adjacent pitch differences from `Melody.intervals`;
- contour representation: interval signs `U`, `D`, or `S` from `Melody.contour`;
- rhythm representation: duration sequence from `Melody.durations`.

Similarity functions:

- interval similarity: normalized edit similarity over interval sequences;
- contour similarity: normalized edit similarity over contour sequences;
- rhythm similarity: normalized edit similarity over duration sequences;
- combined similarity weights: `(0.5, 0.3, 0.2)` for interval, contour, and rhythm respectively.

Graph construction:

- function: `build_similarity_graph(melodies, threshold=0.45)`;
- all tune pairs are scored;
- an edge is included when `combined_similarity >= 0.45` or `combined_similarity <= 0.25`;
- edge weights are rounded to six decimal places;
- for the registered fixture, the graph contains all `28` pairwise edges.

Terminology:

- graph edge inclusion boundaries decide which pairwise similarities enter the graph;
- pair classification threshold `tau` decides whether an included pair is treated as similar or dissimilar in the QUBO objective;
- balance penalty `lambda` controls the soft partition-size penalty.

`tau` is the mathematical and result-schema name for the pair-classification threshold. In the existing implementation code, the equivalent parameter may currently appear as `dissimilar_threshold`. Future implementation must either rename the public and user-facing parameter to `tau`, or retain `dissimilar_threshold` internally while explicitly mapping it to `tau` in code comments, configuration, CLI output, result schema, and documentation. Do not conflate `tau`, graph edge inclusion boundaries, and other similarity thresholds.

Registered edge weights for seed `42`:

| Pair | Weight | Interpretation under `tau=0.25` |
| --- | ---: | --- |
| 0-1 | 1.000000 | similar |
| 0-2 | 0.857143 | similar |
| 0-3 | 0.975000 | similar |
| 0-4 | 0.125000 | dissimilar |
| 0-5 | 0.125000 | dissimilar |
| 0-6 | 0.170833 | dissimilar |
| 0-7 | 0.239286 | dissimilar |
| 1-2 | 0.857143 | similar |
| 1-3 | 0.975000 | similar |
| 1-4 | 0.125000 | dissimilar |
| 1-5 | 0.125000 | dissimilar |
| 1-6 | 0.170833 | dissimilar |
| 1-7 | 0.239286 | dissimilar |
| 2-3 | 0.832143 | similar |
| 2-4 | 0.125000 | dissimilar |
| 2-5 | 0.125000 | dissimilar |
| 2-6 | 0.170833 | dissimilar |
| 2-7 | 0.239286 | dissimilar |
| 3-4 | 0.125000 | dissimilar |
| 3-5 | 0.125000 | dissimilar |
| 3-6 | 0.193056 | dissimilar |
| 3-7 | 0.239286 | dissimilar |
| 4-5 | 1.000000 | similar |
| 4-6 | 0.815278 | similar |
| 4-7 | 0.789286 | similar |
| 5-6 | 0.815278 | similar |
| 5-7 | 0.789286 | similar |
| 6-7 | 0.630556 | similar |

## Binary Variables And Bit Ordering

Use one binary variable per tune:

`x_i in {0, 1}`

Meaning:

- `x_i = 0`: tune `i` is assigned to partition side 0;
- `x_i = 1`: tune `i` is assigned to partition side 1.

Partition labels are arbitrary. A bitstring and its complement represent the same unlabeled partition.

| Index | Variable name | Tune identifier | Human bit position | Qiskit qubit | Measured count-key character |
| ---: | --- | --- | ---: | ---: | ---: |
| 0 | `x_0_fam_a_base` | `fam_a_base` | 0 | 0 | 7 |
| 1 | `x_1_fam_a_transposed` | `fam_a_transposed` | 1 | 1 | 6 |
| 2 | `x_2_fam_a_substitution` | `fam_a_substitution` | 2 | 2 | 5 |
| 3 | `x_3_fam_a_rhythm` | `fam_a_rhythm` | 3 | 3 | 4 |
| 4 | `x_4_fam_b_base` | `fam_b_base` | 4 | 4 | 3 |
| 5 | `x_5_fam_b_transposed` | `fam_b_transposed` | 5 | 5 | 2 |
| 6 | `x_6_fam_b_inserted` | `fam_b_inserted` | 6 | 6 | 1 |
| 7 | `x_7_fam_b_deleted` | `fam_b_deleted` | 7 | 7 | 0 |

Human-readable bitstrings are left-to-right in tune order. Qiskit qubit `i` represents variable `x_i`. Qiskit count keys are displayed most-significant classical bit first after measurement, so a central decoder must reverse count keys before interpreting them as human-order bitstrings.

Worked examples:

- `00001111`: family-A variants on side 0, family-B variants on side 1; Qiskit count key appears as `11110000` before decoding.
- `11110000`: same unlabeled partition as `00001111` after complement; Qiskit count key appears as `00001111` before decoding.
- `01001101`: mixed assignment. Tunes 0, 2, 3, and 6 are on side 0; tunes 1, 4, 5, and 7 are on side 1. Its complement is `10110010`.

## Objective Before QUBO Expansion

Scientific objective:

Minimise disagreement with pairwise similarity evidence while encouraging the registered two-family balance rule.

For each edge `(i, j)` with similarity weight `w_ij`:

`different_ij = x_i + x_j - 2 x_i x_j`

`same_ij = 1 - x_i - x_j + 2 x_i x_j`

Registered pair threshold:

`tau = 0.25`

The pair objective is:

`E_pair(x) = sum_{w_ij >= tau} w_ij * different_ij + sum_{w_ij < tau} (1 - w_ij) * same_ij`

Low-similarity edges use `(1 - w_ij)` as a cannot-link weight. This matches the existing repository formulation and gives stronger separation pressure to pairs with lower similarity.

Registered balance design:

Use a soft quadratic balance penalty with the standard QAOA X mixer.

`E_balance(x) = lambda * (sum_i x_i - n/2)^2`

Primary registered values:

- `n = 8`
- `tau = 0.25`
- `lambda = 0.1`

Total objective:

`E_total(x) = E_pair(x) + E_balance(x)`

Optimisation direction: minimise `E_total`.

Lower energy means fewer pairwise disagreements and better balance. For this registered fixture, the exact global minimum is approximately `0.0`.

## QUBO Expansion

The QUBO energy is:

`E_QUBO(x) = offset + sum_i a_i x_i + sum_{i<j} b_ij x_i x_j`

For a similar edge `w_ij >= tau`:

- add `w_ij` to `a_i`;
- add `w_ij` to `a_j`;
- add `-2 w_ij` to `b_ij`.

For a dissimilar edge `w_ij < tau`, with `c_ij = 1 - w_ij`:

- add `c_ij` to `offset`;
- add `-c_ij` to `a_i`;
- add `-c_ij` to `a_j`;
- add `2 c_ij` to `b_ij`.

For the balance term:

`lambda * (sum_i x_i - n/2)^2 = lambda * n^2/4 + lambda * (1 - n) * sum_i x_i + 2 lambda * sum_{i<j} x_i x_j`

For `n=8` and `lambda=0.1`, the balance contribution is:

- offset: `1.6`;
- each linear coefficient: `-0.7`;
- each quadratic coefficient: `0.2`.

Primary QUBO coefficients for `tau=0.25`, `lambda=0.1`:

- offset: `14.937301`
- linear coefficients:
  - `x_0_fam_a_base`: `-1.207738`
  - `x_1_fam_a_transposed`: `-1.207738`
  - `x_2_fam_a_substitution`: `-1.493452`
  - `x_3_fam_a_rhythm`: `-1.235515`
  - `x_4_fam_b_base`: `-1.595436`
  - `x_5_fam_b_transposed`: `-1.595436`
  - `x_6_fam_b_inserted`: `-1.733333`
  - `x_7_fam_b_deleted`: `-1.533728`

Quadratic coefficient summary:

- all `28` variable pairs have nonzero quadratic coefficients;
- same-family-like edges have negative quadratic coefficients;
- cross-family-like edges have positive quadratic coefficients;
- nonzero coefficient absolute range including offset: `1.061112` to `14.937301`.

The full implementation must store or report the complete coefficient dictionary exactly as generated for the registered fixture.

## Balance Sensitivity Registration

A read-only exhaustive analysis over all `256` assignments was run with existing repository functions for:

- `lambda in {0.05, 0.1, 0.25, 0.5, 1.0}`;
- `tau in {0.20, 0.25, 0.30}`.

For all tested combinations:

- QUBO energy matched the direct objective for every bitstring;
- the only global optima were `00001111` and `11110000`;
- every global optimum was balanced;
- every global optimum recovered the intended family partition up to complement.

Primary registration:

`tau = 0.25`, `lambda = 0.1`

Rationale:

- `tau = 0.25` aligns with the graph construction's low-similarity inclusion boundary and yields zero pair disagreement for the registered fixture.
- `lambda = 0.1` is the smallest nonzero existing default that passed the registered grid and keeps coefficients smaller than larger tested penalties.
- The primary pair has exact optimum energy approximately `0.0`, two complement optima, balanced optima, and family recovery `1.0`.

Primary summary:

| tau | lambda | Optimum energy | Optimal bitstrings | Balanced optima | Family recovery up to complement | QUBO/direct mismatches |
| ---: | ---: | ---: | --- | --- | --- | ---: |
| 0.25 | 0.10 | approximately `0.0` | `00001111`, `11110000` | yes | yes | 0 |

Baseline energy summaries for the primary registration:

- all-assignment energy range: approximately `0.0` to `14.937301`;
- balanced-assignment energy range: approximately `0.0` to `13.579168`;
- uniform random over all assignments expected energy: `12.036707`;
- uniform random over balanced assignments expected energy: `11.622336` over `70` balanced assignments.

Random-success probabilities for the exact optimum complement class are separate from expected random energy:

- uniform over all assignments: `2 / 256 = 0.00781250`;
- uniform over balanced Hamming-weight-four assignments: `2 / 70 = 0.02857143`.

The numerator `2` corresponds to the two complement-equivalent exact optima `00001111` and `11110000`. Future result files must report both random expected energy and random probability of the exact optimum complement class. These probabilities must be used when justifying the future QAOA optimal-probability threshold.

Pre-QAOA gate:

Future implementation must reproduce this sensitivity table in tests or generated review output before constructing a QAOA circuit. If any future fixture or coefficient change alters the argmin set, EXP-005A must stop for review.

## Complement Symmetry

For every bitstring `x`, the complement `1 - x` represents the same unlabeled partition.

Canonical reporting rule:

Use the lexicographically smaller of a human-order bitstring and its complement.

Examples:

- canonical(`00001111`) = `00001111`;
- canonical(`11110000`) = `00001111`;
- canonical(`01001101`) = `01001101` because it is lexicographically smaller than `10110010`.

Canonicalisation is for reporting and evaluation only. It must not be added as an artificial objective penalty.

Required future behaviour:

- exact optima grouped by complement class;
- sampled probabilities aggregated across complementary optima;
- family-recovery and partition metrics invariant to label swap;
- no sampled complement is reported as a failure.

## QUBO-To-Ising Convention

Register the convention:

`x_i = (1 - Z_i) / 2`

The tune-family cost operator is a minimisation Hamiltonian whose computational-basis expectation must match `E_QUBO(x)` up to any explicitly recorded rescaling.

The conversion must include:

- constant offset;
- linear `Z_i` terms;
- quadratic `Z_i Z_j` terms;
- sign convention;
- bit-order conversion;
- any coefficient scaling factor.

Tolerance:

- direct objective vs QUBO energy: absolute tolerance `1e-9`;
- QUBO energy vs Ising/Pauli expectation: absolute tolerance `1e-8`, unless Qiskit numerical behaviour requires a tighter documented choice.

Any rescaling must preserve the argmin set. If the Hamiltonian is scaled by factor `s`, result records must include both scaled and unscaled energies, plus the value of `s`.

Required all-bitstring verification over all `256` assignments:

- direct scientific objective;
- expanded QUBO energy;
- Ising/Pauli expectation plus constant offset;
- decoded solution;
- complement canonical form;
- feasibility or balance status;
- label-aligned metrics.

No QAOA implementation may proceed if this equivalence table fails.

## Classical Ground Truth And Baselines

Register these baselines separately:

1. Exhaustive enumeration over all `256` assignments.
2. Exact optimum grouped by complement symmetry.
3. Uniform-random assignment baseline over all assignments.
4. Uniform-random balanced assignment baseline over Hamming weight `4`.
5. Existing EXP-005 deterministic pseudo-sampling fallback, clearly labelled classical fallback sampling.
6. Optional simple greedy bit-flip or local-search baseline if the existing implementation supports it without adding new scope.

The exact classical solver is the source of truth.

Brute force is superior for this eight-variable benchmark. EXP-005A is educational: it validates modelling, QUBO/Ising conversion, bit ordering, local Qiskit execution, and reporting. It is not a claim of computational advantage.

The classical fallback must never be invoked silently when genuine Qiskit QAOA is requested. If optional Qiskit dependencies are missing, the genuine-QAOA command must fail clearly rather than returning fallback results under a QAOA label.

## Genuine Local QAOA Scope

Primary route:

- direct `QAOAAnsatz`;
- `SparsePauliOp` cost operator;
- local Qiskit V2 estimator and sampler primitives, or the verified Aer equivalent if the installed Qiskit stack requires it;
- SciPy classical optimiser;
- ideal local simulation only;
- deterministic seeds.

Primary experiment:

- QAOA depth: `p = 1`;
- optional `p = 2` sensitivity only after `p = 1` validation;
- fixed finite set of optimiser starts;
- bounded evaluation budget;
- deterministic initialisation strategy recorded in results;
- statevector expectation optimisation where practical;
- finite-shot sampling for the final distribution;
- no automatic hardware submission.

Constraint design:

EXP-005A uses the standard X mixer with a soft quadratic balance penalty. The mixer explores the full eight-qubit computational basis. Balanced assignments are encouraged by the cost function and measured through the balanced-sample probability. A hard fixed-Hamming-weight feasible-subspace mixer is deferred because the repository does not currently support constraint-preserving mixers and the first benchmark remains small enough for transparent penalty validation.

## Quantum Experiment Suitability

The registered fixture is suitable for a first local ideal QAOA demonstration because it is still exhaustively checkable:

- logical variables and problem qubits: `8`;
- exhaustive search size: `256` assignments;
- graph edges: `28`;
- QUBO quadratic terms: `28`;
- expected Ising structure: one constant offset, up to `8` linear `Z_i` terms, and up to `28` quadratic `Z_i Z_j` terms;
- interaction graph density: complete graph on eight variables for the registered fixture;
- expected p=1 cost layer: dense all-to-all `ZZ` interactions plus single-qubit phase rotations;
- approximate pre-routing two-qubit gate count: about `56` CX-equivalent gates for standard `RZZ` decompositions;
- measured Qiskit circuit width: expected to be `16` under Qiskit's total-width convention after adding eight classical bits.

This is denser than EXP-002's four-node cycle. The point is educational validation, not scalable performance. If future fixture changes increase the logical variable count beyond eight to ten variables or add one-hot assignment variables, the first EXP-005A QAOA target should be reduced before implementation proceeds.

## Qiskit Environment And Dependencies

Keep quantum dependencies optional. The non-quantum installation path must continue to run exact solving, fallback sampling, linting, typing, and public-safety checks without Qiskit installed.

Recommended implementation environment:

```powershell
py -3.12 -m venv .venv-qiskit
.\.venv-qiskit\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,quantum]"
```

Python 3.13 may be used when the optional quantum stack resolves cleanly, but Python 3.12 remains the preferred first CI-grade compatibility target.

Retain the current optional quantum package family unless a second implementation review updates it:

```toml
quantum = [
  "qiskit>=2.4,<3",
  "qiskit-aer>=0.17,<0.18",
  "scipy>=1.15,<2",
]
```

Do not add `qiskit-ibm-runtime` for EXP-005A. Do not configure IBM credentials.

## Metrics

Do not rely on one generic PASS label. Report separate metrics.

Execution correctness:

- circuit constructed;
- parameters bound;
- optimiser completed;
- sampler returned valid counts;
- counts sum to requested shots;
- no classical fallback substituted;
- package versions recorded;
- seeds and shots recorded.

Optimisation quality:

- exact minimum energy;
- expected QAOA energy;
- best sampled energy;
- optimal-partition probability aggregated across complements;
- balanced-sample probability;
- probability of the intended synthetic family partition up to label swap;
- objective gap from exact;
- best sampled gap;
- partition accuracy invariant to label swap;
- pairwise same-family precision, recall, and F1 where implemented;
- adjusted Rand index or an equivalent partition metric if added deliberately.

Avoid Max-Cut approximation-ratio terminology unless a mathematically valid minimisation equivalent is defined. Prefer objective gaps and optimal-probability metrics.

## Success, Caution, And Failure Criteria

Implementation success:

- all `256` QUBO/direct-objective equivalence tests pass;
- all `256` QUBO/Ising equivalence tests pass;
- exact optimum is recovered and balanced;
- bit ordering is verified with worked examples;
- genuine local Qiskit circuit executes;
- no fallback is mislabelled as QAOA;
- reproducible result files are generated.

Optimisation success:

- at least one exact optimum is sampled;
- optimal complement-class probability exceeds a pre-implementation registered threshold;
- expected objective improves over the uniform-random baseline;
- intended partition is recovered up to label swap.

Threshold gate:

The exact numerical optimal-probability threshold must be derived only after the QUBO/direct and QUBO/Ising verification gates pass. It must be justified against `2 / 256`, `2 / 70`, and expected shallow-QAOA behaviour.

The threshold must be written into a committed configuration file, task document, or experiment manifest and committed before any QAOA optimiser, estimator, or sampler output is generated or inspected. The implementer must not select or revise the threshold post hoc. After QAOA output has been inspected, the threshold cannot be changed without documenting the reason, treating the change as a new sensitivity or amended experiment, and obtaining fresh review and Gwri approval.

Caution:

- execution succeeds but probability remains diffuse;
- best sample is optimal but expected energy remains weak;
- results are sensitive to seed, `lambda`, `tau`, or initialisation;
- dense interactions or circuit depth reduce interpretability;
- p=1 performs no better than random on expected energy but still samples an optimum.

Failure:

- QUBO/direct-objective disagreement;
- QUBO/Ising disagreement;
- unbalanced exact optimum under the registered formulation;
- bit-order mismatch;
- fallback presented as QAOA;
- no improvement over the registered random baseline;
- unreproducible result;
- any attempt to require IBM Runtime, cloud backend, or hardware execution.

A scientifically honest negative result is acceptable.

## Result Schema

Future result files must include:

- result schema version;
- run identifier;
- source commit;
- `governing_plan_path`;
- `governing_plan_commit`;
- `governing_plan_version`;
- `governing_review_path`;
- `governing_review_commit`;
- fixture identifier;
- deterministic seed;
- tune ordering;
- tune identifiers;
- hidden labels for evaluation;
- similarity weights;
- graph threshold;
- pair threshold `tau`;
- balance penalty `lambda`;
- QUBO offset;
- QUBO linear coefficients;
- QUBO quadratic coefficients;
- Ising coefficients and offset;
- scaling factor;
- exact optimum energy;
- exact optimal bitstrings;
- exact complement classes;
- canonical optimum;
- classical baseline summaries;
- QAOA depth;
- mixer type;
- optimiser;
- optimiser budget;
- initialisation;
- seeds;
- shots;
- optimal parameters;
- expected energy;
- best sampled energy;
- optimal probability across complements;
- balanced probability;
- counts;
- logical problem qubits;
- classical-bit count;
- circuit-width definition;
- circuit depth;
- transpiled depth;
- two-qubit gate count;
- Python, Qiskit, Aer, and SciPy versions;
- execution classification: `genuine-local-qiskit` or `classical-fallback`;
- limitations.

The `governing_plan_path` is `docs/plans/EXP-005A-current-qiskit-local-plan.md`. The result must identify the final approved plan commit, not the current pre-approval amendment commit. `source_commit` records the implementation or run commit, while the governing-plan and governing-review fields identify the approved experiment design that authorised the run.

Do not record private machine paths, usernames, credentials, tokens, cloud backend names, hardware job identifiers, private data paths, or local Streamlit workspace details.

## Implementation Phases And Gates

Phase 0: fixture and coefficient registration

- Exit criterion: fixture ID, tune order, similarities, variables, `tau`, `lambda`, and QUBO coefficients are reproduced from committed code and documented.

Phase 1: exact objective and QUBO validation

- Exit criterion: all `256` direct-objective and `QUBOModel.energy()` comparisons pass within `1e-9`.

Phase 2: Ising conversion and all-bitstring equivalence

- Exit criterion: all `256` QUBO/Ising energy comparisons pass within `1e-8`, with sign, offset, and bit order verified.

Phase 3: genuine p=1 QAOA construction

- Exit criterion: `QAOAAnsatz` circuit is built from the tune-family cost operator and reports correct logical qubits and parameters.

Phase 4: expectation optimisation

- Exit criterion: deterministic optimiser starts complete within the registered evaluation budget and expected energy is reported separately from samples.

Phase 5: finite-shot sampling

- Exit criterion: sampler counts sum to requested shots, decode correctly to human bitstrings, and aggregate complement-optimum probability.

Phase 6: classical/QAOA comparison

- Exit criterion: exact, random, classical fallback, expected-QAOA, and sampled-QAOA metrics are reported without mixing ground truth and quantum outputs.

Phase 7: documentation, tests, and CI

- Exit criterion: default non-quantum tests pass without Qiskit; quantum tests are marked and optional; public-safety scan passes.

Phase 8: optional sensitivity analysis

- Exit criterion: p=2, lambda, tau, or seed sensitivity is reported only after the primary p=1 workflow is validated.

No later phase may proceed if the previous mathematical validation fails.

## Files For Future Implementation

Expected future code files, after a second plan review approves implementation:

- `src/quantum_folk_lab/quantum/qaoa_local.py`: rename or split the existing pseudo-sampler into an explicitly classical fallback.
- `src/quantum_folk_lab/quantum/qaoa_qiskit.py`: add genuine local tune-family QAOA, imported lazily.
- `src/quantum_folk_lab/qubo/qiskit_adapter.py`: add QUBO-to-Ising `SparsePauliOp` conversion and bit-order helpers.
- `src/quantum_folk_lab/cli.py`: expose honest backend labels.
- `src/quantum_folk_lab/evaluation/reporting.py`: centralise richer result schema if needed.
- tests marked as non-quantum or quantum according to dependency needs.

This plan revision does not create or modify those executable files.

## Validation Commands

Default non-quantum validation:

```bash
python -m pytest -m "not quantum"
python -m ruff check .
python -m ruff format --check .
python -m mypy
python scripts/check_public_safety.py
```

Quantum environment validation for future implementation:

```bash
python -m pip install -e ".[dev,quantum]"
pytest -m quantum
```

Do not run EXP-005A QAOA until phases 0 through 2 pass.

The known local Python 3.13 `mypy` issue may expose pre-existing optional-Qiskit missing-stub errors in `maxcut_ising.py` and `maxcut_qaoa.py`. Do not add unrelated typing fixes to this plan-revision PR.

## Privacy And Research Boundaries

Retain these boundaries:

- synthetic public-safe fixture only;
- no private tune archive;
- no raw ABC;
- no MIDI or audio;
- no personal data;
- no hackathon application material;
- no scanned documents or PDFs;
- no credentials;
- no IBM Runtime;
- no QPU;
- no quantum-advantage claim;
- no extrapolation from eight synthetic tunes to real folk-music archives.

Permitted future conclusion after a successful implementation:

> A small synthetic tune-family partitioning QUBO was correctly formulated and executed using a local ideal QAOA reference implementation.

Not permitted:

- quantum advantage;
- superiority over classical clustering;
- evidence about real Welsh, Irish, Scottish, or other folk-tune traditions;
- discovery of historical tune families;
- production readiness;
- usefulness on a large real corpus;
- claims based only on sampling one optimal bitstring.

## Stop Conditions

Stop and request review if any of these occur:

- fixture generation or similarity values differ from the registered table;
- `tau` or `lambda` changes alter the exact argmin set;
- exact optimum becomes unbalanced;
- direct objective and QUBO disagree;
- QUBO and Ising energies disagree;
- bit-order conversion cannot be proven;
- Qiskit execution attempts to require IBM Runtime, a cloud backend, or credentials;
- the classical fallback would be returned under a genuine-QAOA label;
- any result file would expose private paths, credentials, private data, or hardware job identifiers;
- implementation would require weakening CI or public-safety checks.

## Review-Closure Matrix

| Review item | Revised-plan section | Acceptance criterion | Status |
| --- | --- | --- | --- |
| 1. Plan lacked tune-family mathematical design | Correct Mathematical Formulation; Objective Before QUBO Expansion | Plan states two-family signed graph partitioning/correlation-style QUBO before QAOA | resolved in plan |
| 2. Max-Cut rejection was not explicit | Correct Mathematical Formulation | Plan says EXP-005A is not direct Max-Cut and separates reusable EXP-002 parts | resolved in plan |
| 3. Synthetic fixture not fully registered | Registered Fixture; Feature And Similarity Representation | Eight tune IDs, labels, generation, similarities, graph threshold, and fixture ID are listed | resolved in plan |
| 4. Ambiguous/noisy examples unnamed | Registered Fixture | Rhythm, insertion, and deletion variants are named and explained | resolved in plan |
| 5. Variable ordering and decoding missing | Binary Variables And Bit Ordering | Complete variable, tune, qubit, and count-key table plus examples are present | resolved in plan |
| 6. Direct scientific objective missing | Objective Before QUBO Expansion | Scientific objective and algebraic pair/balance terms are stated before QUBO expansion | resolved in plan |
| 7. `tau` and `lambda` inherited defaults | Objective Before QUBO Expansion; Balance Sensitivity Registration | Primary `tau=0.25`, `lambda=0.1` are registered with grid evidence | resolved in plan |
| 8. Penalty weights not justified | Balance Sensitivity Registration | Exhaustive grid summary proves balanced family-recovery optima for tested values | resolved in plan; requires implementation verification |
| 9. QUBO verification incomplete | QUBO Expansion; QUBO-To-Ising Convention; Implementation Phases | All-256 direct/QUBO table is required before QAOA | resolved in plan; requires implementation verification |
| 10. Ising verification not tune-specific | QUBO-To-Ising Convention | Plan requires all-256 QUBO/Ising checks with offset, sign, and bit order | resolved in plan; requires implementation verification |
| 11. Complement symmetry not registered | Complement Symmetry | Lexicographic canonicalisation and probability aggregation are specified | resolved in plan |
| 12. Classical baselines underspecified | Classical Ground Truth And Baselines | Exhaustive, random all, random balanced, fallback, and optional local search baselines are registered | resolved in plan |
| 13. Approximation-ratio language unsafe | Metrics | Plan prefers objective gaps and optimal probabilities; Max-Cut ratio language is avoided | resolved in plan |
| 14. Circuit size and density unregistered | Quantum Experiment Suitability; Genuine Local QAOA Scope; Result Schema | Plan records eight logical qubits, dense interactions, and circuit reporting fields | resolved in plan; requires implementation measurement |
| 15. Fallback naming unsafe | Classical Ground Truth And Baselines; Files For Future Implementation | Plan requires classical fallback labelling and clear failure when genuine QAOA is unavailable | resolved in plan; requires implementation verification |
| 16. Interpretation boundaries not tied to success | Success, Caution, And Failure Criteria; Privacy And Research Boundaries | Allowed and disallowed conclusions are listed with success/caution/failure criteria | resolved in plan |
| 17. Privacy/provenance schema incomplete | Result Schema; Privacy And Research Boundaries | Result fields and excluded private fields are explicitly listed | resolved in plan |

## Second-Review Amendment Closure

The independent second review recommended `APPROVE WITH AMENDMENTS`. This plan remains revised and reviewed, awaiting final human approval before implementation. This section records closure of the four authorised documentation amendments; it does not claim final approval by Gwri.

| Second-review amendment | Addressed in this plan |
| --- | --- |
| Add random-success probabilities | Balance Sensitivity Registration records `2 / 256 = 0.00781250` and `2 / 70 = 0.02857143`, explains the two optimum bitstrings, and requires future results to report random expected energy and random optimum-class probability separately. |
| Strengthen optimal-probability threshold governance | Success, Caution, And Failure Criteria requires the threshold to be derived after verification, justified against both random-success probabilities and shallow-QAOA expectations, committed before any QAOA output is inspected, and changed only through a reviewed amended experiment. |
| Add plan provenance | Result Schema requires governing plan and review path, commit, and version fields, and distinguishes those fields from `source_commit`. |
| Map `tau` terminology to `dissimilar_threshold` | Feature And Similarity Representation defines `tau` as the mathematical and result-schema pair-classification threshold and maps it to the existing internal `dissimilar_threshold` name while separating graph thresholds, `tau`, and `lambda`. |

## Required Final Approval

Before any EXP-005A implementation begins, this amended plan should receive final human approval. No QUBO, Ising, QAOA, CLI, notebook, or result-generation implementation may start from this plan alone.
