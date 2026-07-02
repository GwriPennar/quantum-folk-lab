# EXP-005A Tune-Family QUBO Plan Review

## Recommendation

REVISE

This recommendation is advisory. Gwri makes the final decision.

## Reviewed Branch And Base

- Review branch: `codex/review-exp-005a-tune-family-qubo`
- Reviewed `main` commit: `869d7e591487d83e06d1eeeb19383be4db196bfe`
- Repository: `GwriPennar/quantum-folk-lab`
- Scope: mathematical and experimental design review only

No EXP-005A implementation was started. No tune-family QUBO implementation, QAOA circuit, quantum run, real folk-tune data, IBM Runtime use, cloud backend, credentials, hardware execution, or QPU job was introduced.

## Governing EXP-005A Plan

Exact plan path reviewed:

- `docs/plans/EXP-005A-current-qiskit-local-plan.md`

Searches for `EXP-005A`, `tune-family`, `QUBO`, synthetic family, and clustering material found one explicit EXP-005A plan. That plan governs the future local-Qiskit execution route, dependency strategy, result schema, CI split, and fallback labelling. It does not yet fully govern the tune-family mathematical formulation. The currently implied formulation is spread across `docs/mathematical_model.md`, `src/quantum_folk_lab/qubo/two_family.py`, `src/quantum_folk_lab/domain/synthetic.py`, and the CLI pipeline.

This is not a blocking document conflict, but it is a blocking design gap: EXP-005A should not proceed to quantum implementation until the mathematical formulation is promoted into an explicit EXP-005A design section or companion plan.

## Files Reviewed

- `README.md`
- `pyproject.toml`
- `.github/workflows/ci.yml`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/learning-roadmap.md`
- `docs/mathematical_model.md`
- `docs/responsible_research.md`
- `docs/ibm_quantum_setup.md`
- `docs/ibm-quantum-setup.md`
- `docs/plans/EXP-005A-current-qiskit-local-plan.md`
- `docs/plans/EXP-002-maxcut-reference-plan.md`
- `docs/reviews/EXP-002-maxcut-reference-review.md`
- `data/README.md`
- `results/README.md`
- `experiments/EXP-001-quantum-basics/README.md`
- `experiments/EXP-001-quantum-basics/RESULT.md`
- `experiments/EXP-002-maxcut-reference/README.md`
- `experiments/EXP-002-maxcut-reference/RESULT.md`
- `experiments/EXP-003-synthetic-tune-families/README.md`
- `experiments/EXP-004-qubo-family-partition/README.md`
- `experiments/EXP-005-qaoa-simulator/README.md`
- `src/quantum_folk_lab/cli.py`
- `src/quantum_folk_lab/domain/synthetic.py`
- `src/quantum_folk_lab/domain/models.py`
- `src/quantum_folk_lab/graph/build.py`
- `src/quantum_folk_lab/similarity/combined.py`
- `src/quantum_folk_lab/qubo/model.py`
- `src/quantum_folk_lab/qubo/two_family.py`
- `src/quantum_folk_lab/qubo/qiskit_adapter.py`
- `src/quantum_folk_lab/classical/exact.py`
- `src/quantum_folk_lab/evaluation/metrics.py`
- `src/quantum_folk_lab/quantum/qaoa_local.py`
- `src/quantum_folk_lab/maxcut.py`
- `src/quantum_folk_lab/maxcut_exact.py`
- `src/quantum_folk_lab/maxcut_ising.py`
- `src/quantum_folk_lab/maxcut_qaoa.py`
- `scripts/check_public_safety.py`

## Proposed Optimisation Problem

As currently implemented and documented, the tune-family problem is a two-family graph partitioning problem over synthetic melodies.

The optimiser is not selecting medoids, not choosing representatives, not assigning tunes to one of `K > 2` labelled families, and not discovering an unknown number of clusters. It assigns each synthetic tune to one of two unlabeled sides of a partition so that:

- high-similarity pairs prefer the same side;
- low-similarity pairs prefer different sides;
- a soft balance penalty discourages trivial all-in-one assignments.

Known synthetic family labels are evaluation truth only. They must not be encoded as objective terms.

Plain English: given eight synthetic tunes with known hidden labels `AAAA BBBB`, build pairwise similarity edges, then find a balanced two-way partition that keeps related variants together and separates the two synthetic families.

## Sound Parts Of The Plan

The EXP-005A plan is sound in several implementation and research-boundary areas:

- It correctly separates genuine local Qiskit QAOA from the existing deterministic pseudo-sampling fallback.
- It preserves the non-Qiskit installation path and keeps Qiskit imports optional.
- It chooses a local simulator-only route with no IBM account, no Runtime service, no cloud backend, and no QPU job.
- It keeps the exact classical solver as the source of truth.
- It prefers direct `QAOAAnsatz` construction for educational transparency, which matches the repository's learning goals.
- It requires Qiskit, Aer, SciPy, seeds, shots, depth, optimiser settings, and circuit metadata in future result records.
- It keeps CI split between default non-quantum checks and optional quantum checks.
- It explicitly avoids quantum-advantage claims.

These parts should be retained when the mathematical formulation is revised.

## Unsupported Or Premature Assumptions

The current plan assumes the existing eight-variable tune-family QUBO is ready to receive the verified EXP-002 local-QAOA machinery. That assumption is premature.

Unsupported assumptions to resolve before implementation:

- that "tune-family QUBO" has a single explicit EXP-005A mathematical definition;
- that `lambda = 0.1` is an adequate balance penalty rather than an empirical default;
- that the current similarity threshold is scientifically registered rather than inherited from exploratory code;
- that the objective should be treated as Max-Cut-like because EXP-002 implemented Max-Cut;
- that a sampled label-swapped bitstring can be interpreted without explicit canonicalisation rules;
- that future result metrics can reuse approximation-ratio language from EXP-002 without redefining it for a minimisation problem;
- that the eight-variable dense interaction graph will remain educationally transparent after QAOA circuit expansion.

These are not fatal objections. They are design choices that need to be made visible and testable.

## Synthetic Fixture Review

The current fixture is suitable as a first bounded review target with amendments:

- Tune count: `8`
- Families: two synthetic families, four variants each
- Known labels: `00001111`, used only for evaluation
- Tune identifiers:
  - `fam_a_base`
  - `fam_a_transposed`
  - `fam_a_substitution`
  - `fam_a_rhythm`
  - `fam_b_base`
  - `fam_b_transposed`
  - `fam_b_inserted`
  - `fam_b_deleted`
- Representation: synthetic pitch and duration sequences, transformed through deterministic transpose, substitution, rhythm, insertion, and deletion operations
- Similarity: weighted interval, contour, and rhythm edit similarities
- Graph: the default settings produce all `28` pairwise edges after thresholding on the eight-tune benchmark
- Exhaustive search size: `2^8 = 256` assignments, or `128` if complement symmetry fixes the first bit to zero

The fixture is synthetic and public-safe. It contains no ABC bodies, real tune corpus, private metadata, embeddings, cloud services, or IBM credentials.

Required amendment: explicitly name at least one ambiguous or noisy example. The current likely candidates are `fam_a_rhythm`, `fam_b_inserted`, and `fam_b_deleted`, because they change rhythm or sequence length, but the plan should state which example is intended to test ambiguity and why.

State exactly what makes two synthetic tunes related: they are related when they are generated from the same synthetic base family and have high interval, contour, and rhythm similarity under the documented deterministic scoring function. This relation is evaluation truth; the optimiser only sees pairwise weights.

## Variable Dictionary

The current two-family formulation uses one binary variable per tune:

`x_i in {0, 1}` for tune index `i`, where `i = 0, ..., 7`.

Interpretation:

- `x_i = 0`: tune `i` is assigned to partition side 0
- `x_i = 1`: tune `i` is assigned to partition side 1
- Side labels are arbitrary. A bitstring and its complement represent the same partition.

Current variable ordering:

| Index | Variable | Tune |
| ---: | --- | --- |
| 0 | `x_0_fam_a_base` | `fam_a_base` |
| 1 | `x_1_fam_a_transposed` | `fam_a_transposed` |
| 2 | `x_2_fam_a_substitution` | `fam_a_substitution` |
| 3 | `x_3_fam_a_rhythm` | `fam_a_rhythm` |
| 4 | `x_4_fam_b_base` | `fam_b_base` |
| 5 | `x_5_fam_b_transposed` | `fam_b_transposed` |
| 6 | `x_6_fam_b_inserted` | `fam_b_inserted` |
| 7 | `x_7_fam_b_deleted` | `fam_b_deleted` |

Total variable count: `8`.

A completed bitstring maps back to a partition by reading bits in this exact order. For example, `00001111` assigns the four family-A variants to side 0 and the four family-B variants to side 1. `11110000` is the same partition after label swap.

This bitstring interpretation is unambiguous and suitable for exhaustive verification.

## Objective And Constraints

The scientific objective should be stated before QUBO conversion:

Minimise disagreement with pairwise synthetic similarity evidence while discouraging trivial unbalanced partitions.

For pair `(i, j)` with similarity `w_ij`, define:

- `different_ij = x_i + x_j - 2 x_i x_j`
- `same_ij = 1 - x_i - x_j + 2 x_i x_j`

For a similarity threshold `tau`, the current objective is:

`E_pair(x) = sum_{w_ij >= tau} w_ij * different_ij + sum_{w_ij < tau} (1 - w_ij) * same_ij`

The current balance penalty is:

`E_balance(x) = lambda * (sum_i x_i - n / 2)^2`

Total objective:

`E_total(x) = E_pair(x) + E_balance(x)`

Lower energy is better. Energy `0` means every included pair relation and the balance target are satisfied exactly under this fixture and threshold.

Current registered values implied by code:

- `tau = 0.25`
- `lambda = 0.1`
- `n = 8`

The balance term is a soft regulariser, not a hard feasibility constraint. If EXP-005A wants exactly four tunes per side, it must explicitly register this as a constraint and choose a penalty weight proven sufficient for the fixture.

## Constraint Review

Current two-side partition variables require no one-hot assignment constraint: each tune automatically belongs to exactly one of two sides because every tune has one binary variable.

Potential constraints and review status:

| Constraint | Algebraic condition | Current status | Penalty |
| --- | --- | --- | --- |
| Binary assignment | `x_i in {0,1}` | inherent in QUBO bitstrings | none |
| Exactly two partition sides | one bit per tune | inherent | none |
| Balanced sides | `sum_i x_i = n/2` | soft regulariser | `lambda * (sum_i x_i - n/2)^2` |
| Non-empty families | `1 <= sum_i x_i <= n-1` | implied if exact balance holds | not separately needed for `n=8` |
| Label symmetry | `x` equivalent to `1 - x` | present | canonicalise, not penalise |
| Must-link/cannot-link | optional pair constraints | not currently explicit | pair penalties already behave like soft must/cannot evidence |
| Unassigned tunes | none allowed | not supported | would require new variables |
| Representatives/medoids | not part of current model | not supported | would require new variables |

Balance penalty verification:

`lambda * (sum_i x_i - 4)^2` is zero when exactly four tunes are assigned to side 1 and positive otherwise. For `sum_i x_i` values `0` through `8`, penalty contributions are `1.6, 0.9, 0.4, 0.1, 0.0, 0.1, 0.4, 0.9, 1.6` when `lambda = 0.1`.

No auxiliary variables are needed for the current quadratic balance penalty.

## Penalty Weight Analysis

The current `lambda = 0.1` is not derived in the EXP-005A plan. It should not be accepted as scientifically registered until a defensible bound and sensitivity grid are added.

For this objective class, a sufficient hard-balance penalty lower bound can be derived by bounding the maximum possible pair-objective advantage an unbalanced assignment could gain over a balanced assignment. A conservative fixture-specific bound is:

`lambda > sum_pair_coefficients`

where `sum_pair_coefficients = sum_{w_ij >= tau} w_ij + sum_{w_ij < tau} (1 - w_ij)`.

This bound is safe but may be unnecessarily large for QAOA because it increases coefficient scale and can compress useful phase resolution. A tighter bound may be computed exhaustively for the fixed fixture:

1. enumerate all balanced and unbalanced bitstrings;
2. find the best balanced pair objective;
3. find the best unbalanced pair objective for each violation amount `d = |sum_i x_i - 4|`;
4. require `lambda * d^2` to exceed the maximum unbalanced advantage plus a small margin.

Required registered sensitivity grid:

- `lambda in {0.05, 0.1, 0.25, 0.5, 1.0}`
- threshold `tau in {0.20, 0.25, 0.30}` if the threshold remains part of the formulation

Required proof before quantum implementation: exhaustive enumeration must show every global optimum is feasible under the registered balance rule and recovers the intended partition up to label swap.

Risk if penalties are too small: QAOA and exact search may prefer unbalanced or all-in-one assignments that reduce pair disagreement but are not useful family partitions.

Risk if penalties are too large: large coefficients dominate the Hamiltonian, reduce numerical interpretability, and can make shallow QAOA behaviour mostly about satisfying balance rather than using similarity evidence.

Coefficient rescaling should be planned for QAOA if the final coefficient range becomes broad. Any rescaling must preserve argmin assignments and be recorded in results.

## Max-Cut Suitability

EXP-005A should not be described as a direct Max-Cut experiment.

The current formulation is a signed or correlation-style two-way graph partitioning QUBO:

- similar edges penalise cuts;
- dissimilar edges penalise non-cuts;
- a balance regulariser is added.

This is closer to constrained graph partitioning or correlation clustering than Max-Cut. Max-Cut rewards cutting positive edges. The tune-family model has mixed preferences and a balance term, so borrowing the EXP-002 Max-Cut objective would be mathematically wrong unless the tune-family objective were deliberately redefined as a pure cut problem on dissimilarity edges.

Reusable EXP-002 components:

- exact enumeration pattern;
- bit-order discipline;
- complement/canonical partition handling;
- all-bitstring QUBO/Ising verification style;
- Pauli conversion test strategy using `x = (1 - Z) / 2`;
- local `QAOAAnsatz`, `StatevectorEstimator`, `StatevectorSampler`, deterministic seeds, and result reporting patterns;
- distinction between expected objective, best sampled solution, and probability mass on optima;
- CI split for non-quantum and quantum tests.

Not reusable without alteration:

- Max-Cut graph class as the domain model;
- positive cut-value maximisation convention;
- `H_cut = sum w/2 * (I - Z_i Z_j)` as the direct objective;
- approximation ratio semantics;
- optimal-bitstring interpretation;
- claim that the objective is Max-Cut.

## QUBO Conversion Requirements

The current QUBO construction agrees with the direct objective for the registered eight-variable fixture. A review-time exhaustive check over all `256` bitstrings found:

- mismatches between `QUBOModel.energy()` and `direct_objective()`: `0`
- best energy: approximately `0.0`
- best bitstrings: `00001111` and `11110000`
- family recovery: `1.0`
- best assignments balanced: yes
- global optima: `2`, exactly the label-swap pair

The future implementation must turn this into committed tests and a stored verification table.

Required QUBO documentation:

- full linear coefficients;
- full quadratic coefficients;
- constant offset;
- variable ordering;
- minimisation convention;
- pair threshold and balance coefficient;
- whether the balance term is a soft regulariser or hard feasibility penalty.

Required exhaustive table fields:

- bitstring;
- decoded partition;
- direct pair objective;
- balance violation count or magnitude;
- penalty contribution;
- total QUBO energy;
- feasibility;
- family recovery after label alignment;
- whether the bitstring belongs to the equivalent optimal set.

## Ising Mapping Requirements

EXP-005A may reuse the project convention:

`x_i = (1 - Z_i) / 2`

but only after proving the complete mapping for this QUBO. The future implementation must verify every computational basis assignment:

- QUBO energy;
- Pauli expectation;
- constant offset;
- sign convention;
- bit ordering;
- minimisation direction.

Unlike EXP-002, the tune-family Hamiltonian will include linear `Z_i`, quadratic `Z_i Z_j`, and constant terms from both pair evidence and balance. The offset must not be dropped when comparing exact energies, even if QAOA optimisation itself is unaffected by constants.

## Symmetry And Degeneracy

The family labels are symmetric. `00001111` and `11110000` represent the same recovered partition.

Required handling:

- canonicalise each partition as `min(bitstring, complement(bitstring))`;
- count both label-swapped optima as success;
- report probability mass across all equivalent optimal bitstrings;
- evaluate family recovery after label alignment;
- do not call a sampled complement a QAOA failure.

Symmetry-breaking by fixing `x_0 = 0` is useful for exact reporting, but it should not be imposed inside the QAOA circuit unless the model is explicitly reduced from eight variables to seven. If exact enumeration fixes the first bit to zero, result reporting must still account for both sampled complements in the full eight-qubit QAOA distribution.

## Classical Baselines

Required sources of truth:

- exhaustive enumeration over the fixed eight-variable fixture;
- deterministic brute-force optimum;
- direct objective evaluation independent of QUBO coefficient storage;
- random balanced-assignment baseline;
- simple greedy bit-flip or local-search baseline;
- known synthetic labels used strictly for evaluation.

Recommended metrics:

- objective gap from exact optimum;
- feasible or balanced-solution rate;
- exact optimum recovery;
- family assignment accuracy after label alignment;
- adjusted Rand index or pairwise partition agreement;
- pairwise precision, recall, and F1 for same-family predictions;
- probability mass on all equivalent optimal solutions;
- sampled-best objective reported separately from expected objective.

QAOA must never be used as its own ground truth.

## Quantum Experiment Suitability

For the current eight-tune, one-bit-per-tune formulation:

- logical variables/qubits: `8`
- exhaustive search size: `256`
- graph edges before QUBO expansion: `28`
- current QUBO quadratic terms: `28`
- expected Pauli structure: up to `8` linear `Z_i` terms, up to `28` quadratic `Z_i Z_j` terms, and one constant offset
- interaction graph density: complete graph on eight variables under default fixture settings
- expected `p=1` cost layer: dense all-to-all `ZZ` interactions plus single-qubit phase rotations
- approximate two-qubit entangling gate count before transpiler-specific routing: about `2 * 28 = 56` CX-equivalent gates for standard `RZZ` decompositions
- measured circuit width by Qiskit convention: likely `16` total width after adding eight classical bits

This is still small enough for local ideal statevector simulation and educational debugging. It is much denser than EXP-002, so the plan must keep claims modest and treat QAOA as a local reference demonstration rather than a useful solver.

If the formulation grows beyond eight to ten logical variables or adds one-hot `x[i,k]` assignment variables, EXP-005A should reduce the fixture before attempting a first QAOA reference.

## QAOA Evaluation Design

Recommended bounded registered design for a future implementation:

- primary depth: `p = 1`
- optional depth: `p = 2` only as a sensitivity run after `p = 1` is validated
- fixed initial points recorded in parameter order;
- optimiser: COBYLA or another explicitly pinned SciPy optimiser;
- iteration limit: small and registered;
- shots: `4096` for the stored result, with a smaller smoke value allowed in CI;
- seeds: fixed sampler and transpiler seeds;
- exact statevector expectation where practical;
- finite-shot sampled result reported separately;
- combined probability across both label-swapped optima;
- balanced-sample probability;
- expected objective, sampled-best objective, and exact optimum all reported separately.

EXP-002's expected-versus-sampled distinction should be retained exactly.

## Result Schema Requirements

Future EXP-005A results should record:

- result schema version;
- run identifier;
- source commit;
- Python, Qiskit, Aer, and SciPy versions;
- fixture version;
- exact variable ordering;
- objective version;
- threshold values;
- penalty values;
- QAOA depth and parameter count;
- optimiser and initial points;
- seeds and shots;
- logical problem qubits;
- classical-bit count;
- circuit-width definition;
- QUBO coefficient summary and offset;
- exact optimum and equivalent optima;
- expected objective;
- sampled-best solution;
- optimal probability across equivalents;
- balanced-sample probability;
- label-aligned family metrics;
- limitations.

Do not record private machine paths, usernames, credentials, tokens, cloud backend names, or hardware job identifiers.

## Safety And Interpretation Boundaries

Permitted conclusion after a future successful implementation:

> A small synthetic tune-family partitioning QUBO was correctly formulated and executed using a local ideal QAOA reference implementation.

Not permitted:

- quantum advantage;
- superiority over classical clustering;
- evidence about real Welsh, Irish, Scottish, or other folk-tune traditions;
- discovery of historical tune families;
- production readiness;
- usefulness on a large real corpus;
- claims based only on sampling one optimal bitstring.

The experiment must remain synthetic-only and local-only.

## Required Plan Amendments

Before EXP-005A implementation, amend the governing plan or add a linked mathematical design document to include:

| # | Issue | Why It Matters | Concrete Proposed Change | Acceptance Criterion | Blocks Implementation |
| ---: | --- | --- | --- | --- | --- |
| 1 | The governing plan is mostly a Qiskit execution plan, not a tune-family mathematical design. | Implementation would proceed without a stable scientific objective. | Add a "Tune-Family Mathematical Formulation" section or linked plan that defines the optimisation task before mentioning QAOA. | The plan states the optimiser is solving a two-family signed graph partitioning or correlation-style QUBO over synthetic tunes. | Yes |
| 2 | The plan does not explicitly reject Max-Cut as the tune-family objective. | Reusing EXP-002 Max-Cut directly would cut similar edges and invert the intended family logic. | State that EXP-005A is not Max-Cut unless deliberately reformulated as a pure dissimilarity-cut problem. | The plan lists reusable EXP-002 infrastructure separately from non-reusable Max-Cut mathematics. | Yes |
| 3 | The synthetic fixture is not fully registered in the EXP-005A plan. | Results cannot be reproduced or interpreted if the fixture can drift. | Register the eight tune IDs, hidden labels, deterministic generation method, similarity weights, graph threshold, and fixture version. | A reader can reconstruct the exact eight-tune fixture without reading package code. | Yes |
| 4 | Ambiguous or noisy examples are not named. | The experiment claims a family-recovery challenge but does not specify which cases test ambiguity. | Identify at least one noisy example, such as `fam_a_rhythm`, `fam_b_inserted`, or `fam_b_deleted`, and explain why it is difficult. | The plan documents one or more expected hard cases and how success or failure will be interpreted. | Yes |
| 5 | Variable ordering and bitstring decoding are not registered in the EXP-005A plan. | QAOA counts are meaningless if bit order, tune order, or label-side interpretation is ambiguous. | Include the exact `x_i` variable dictionary and bitstring-to-partition mapping. | The plan contains the eight-variable table from this review or an equivalent table. | Yes |
| 6 | The direct scientific objective is not stated before QUBO coefficients. | It is hard to tell whether the QUBO optimises family recovery or only follows inherited code. | State the pair-disagreement minimisation objective in ordinary mathematical form, then derive QUBO coefficients. | The plan separates scientific objective, pair terms, balance term, constants, and optional regularisation. | Yes |
| 7 | Threshold `tau` and balance weight `lambda` are inherited defaults. | Arbitrary thresholds and penalties can decide the outcome more than the similarity evidence. | Register `tau`, `lambda`, and whether balance is a hard feasibility constraint or soft regulariser. | The plan explains why each registered value is chosen for the fixture. | Yes |
| 8 | Penalty weights are not derived or exhaustively justified. | Too-small penalties permit invalid partitions; too-large penalties distort QAOA dynamics. | Add a fixture-specific exhaustive penalty analysis and a bounded sensitivity grid. | Exhaustive enumeration proves every global optimum is feasible under the registered penalty. | Yes |
| 9 | QUBO verification requirements are not complete. | A sign, offset, or coefficient bug could be hidden until QAOA sampling. | Require an all-256-bitstring table comparing direct objective, penalties, total QUBO energy, decoded solution, feasibility, and label-aligned metrics. | Tests fail if direct objective and `QUBOModel.energy()` differ for any bitstring. | Yes |
| 10 | Ising verification is not specific to the tune-family QUBO. | EXP-002's Max-Cut Hamiltonian omits linear terms that the tune-family QUBO can contain. | Require all-256-bitstring verification for `x = (1 - Z) / 2`, including offset, sign, and bit order. | Tests prove Pauli expectations and QUBO energies agree within tolerance for every computational basis state. | Yes |
| 11 | Complement symmetry is acknowledged in code but not registered for EXP-005A reporting. | Label-swapped optima could be misclassified as failures, and probability mass could be undercounted. | Define canonical partition handling and aggregate optimal probability across equivalent complements. | `00001111` and `11110000` are both counted as the same successful partition. | Yes |
| 12 | Classical baselines are underspecified. | QAOA must be compared against transparent classical truth, not treated as its own evidence. | Register exhaustive enumeration, random balanced assignment, and a simple greedy/local heuristic baseline. | Future results report objective gap, exact optimum recovery, feasible rate, label-aligned accuracy, and pairwise partition metrics. | Yes |
| 13 | EXP-002 approximation-ratio language does not transfer cleanly. | The tune-family objective is minimised and may have optimum near zero, making ratio metrics unstable. | Prefer objective gap and recovery/probability metrics; only use ratios if mathematically defined for this objective. | The plan avoids misleading approximation-ratio claims for zero or near-zero optima. | Yes |
| 14 | Circuit size and density are not registered for the tune-family instance. | Eight variables on a complete interaction graph is still small but much denser than EXP-002. | Record expected logical qubits, Pauli term count, interaction density, circuit-width definition, and approximate two-qubit gate count. | The plan states the first benchmark remains eight logical qubits and about 28 quadratic interactions unless deliberately reduced. | No, but required before result publication |
| 15 | The fallback path still has user-facing QAOA naming. | It can make deterministic classical pseudo-sampling look like quantum evidence. | Rename or relabel the fallback as classical fallback sampling everywhere it appears in EXP-005A scope. | CLI, docs, and result schema never present fallback results as genuine QAOA. | Yes |
| 16 | Interpretation boundaries need to be tied to EXP-005A success criteria. | Sampling an optimum on a tiny synthetic fixture is easy to overstate. | Register allowed and disallowed conclusions before implementation. | The plan permits only a local ideal synthetic-QUBO demonstration and rejects quantum advantage, real-corpus, or production claims. | Yes |
| 17 | Privacy and provenance fields are not tied to the final result schema. | Result files could accidentally expose local paths or private context. | Require schema fields for fixture version and package versions while excluding usernames, paths, credentials, backend accounts, and job IDs. | Public-safety scan passes and committed result files contain no private data or hardware identifiers. | Yes |

No plan amendment was made in this review because the required changes define the scientific formulation and should be approved deliberately rather than silently rewritten.

## Final Decision

Recommendation: REVISE

The current code and supporting mathematical note contain a plausible, bounded, testable two-family partition QUBO. However, the governing EXP-005A plan is primarily an implementation-environment plan for replacing pseudo-sampling with local Qiskit. It does not yet define the tune-family optimisation problem, variables, penalties, verification table, symmetry handling, or evaluation metrics with enough precision to authorise EXP-005A quantum implementation.

Once the required amendments are made, the current eight-variable synthetic fixture is a reasonable local ideal QAOA demonstration target.
