# EXP-005A Revised Plan Second Review

## Recommendation

APPROVE WITH AMENDMENTS

The revised EXP-005A plan is a substantial improvement over the first reviewed version. It now defines the tune-family mathematical objective before QAOA, registers the synthetic fixture, fixes the bit-ordering ambiguity, separates the classical fallback from genuine local Qiskit QAOA, and adds the validation gates needed before any quantum run.

No EXP-005A implementation was performed in this review. No source code, result file, notebook, dependency file, CI workflow, IBM Runtime path, cloud backend, hardware execution, or private workspace content was added.

## Reviewed Material

- Pull request under review: PR #4
- Reviewed head commit: `32c6badcb883fd999a92c33f8862807bcf811a41`
- Reviewed plan: `docs/plans/EXP-005A-current-qiskit-local-plan.md`
- Prior review: `docs/reviews/EXP-005A-tune-family-qubo-plan-review.md`
- EXP-002 plan, result, and review material
- Current synthetic fixture, similarity, graph, QUBO, exact-solver, metrics, local fallback, and EXP-002 Qiskit Max-Cut code paths

The reviewed PR changes only the governing EXP-005A plan. It does not contain implementation code.

## Summary Finding

The revised plan is now clear enough to authorise implementation after a small set of documentation amendments. The remaining amendments are governance and result-schema clarifications, not mathematical blockers.

The plan correctly states that EXP-005A is not direct Max-Cut. It frames the problem as a two-family signed graph-partitioning or correlation-style QUBO, with known family labels used only for evaluation. It also correctly preserves brute-force exact enumeration as ground truth and treats QAOA as an educational local ideal-simulation reference.

## Closure Of Prior Review

All blocking items from the first `REVISE` review are closed at the planning level:

| Prior item | Second-review status |
| --- | --- |
| Mathematical formulation missing | Closed. The plan now defines the signed graph-partitioning objective before QAOA. |
| Max-Cut transfer risk | Closed. The plan explicitly says EXP-005A is not direct Max-Cut and limits EXP-002 reuse to engineering discipline. |
| Fixture not registered | Closed. The plan registers the eight tune IDs, labels, generator, similarity weights, graph threshold, and fixture identifier. |
| Ambiguous variants unnamed | Closed. Rhythm, insertion, and deletion variants are named and explained. |
| Variable order and decoding missing | Closed. The plan registers human bit order, Qiskit qubits, count-key reversal, and worked examples. |
| Direct objective missing | Closed. Pair and balance terms are written before QUBO expansion. |
| `tau` and `lambda` inherited | Closed. The plan registers `tau=0.25` and `lambda=0.1` with grid evidence. |
| Penalty evidence missing | Closed for plan. Future implementation must reproduce the exhaustive grid. |
| QUBO verification incomplete | Closed for plan. All `256` direct/QUBO checks are required before QAOA. |
| Ising verification missing | Closed for plan. All `256` QUBO/Ising checks with sign, offset, and bit order are required. |
| Complement symmetry unregistered | Closed. Canonicalisation and probability aggregation across complements are specified. |
| Classical baselines underspecified | Closed with amendment below. Baselines are registered, but exact random-success probabilities should be added. |
| Approximation-ratio language unsafe | Closed. The plan prefers objective gaps and probabilities. |
| Circuit size and density unregistered | Closed for plan. Future implementation must measure the actual circuit. |
| Fallback naming unsafe | Closed for plan. The fallback must be labelled classical and must not silently replace genuine QAOA. |
| Interpretation boundaries weak | Closed. Allowed and disallowed conclusions are explicit. |
| Privacy and provenance schema incomplete | Closed with amendment below. The schema should add plan version/provenance. |

## Independent Fixture Check

A read-only local enumeration using the existing repository code confirmed the plan's registered fixture:

- tune IDs: `fam_a_base`, `fam_a_transposed`, `fam_a_substitution`, `fam_a_rhythm`, `fam_b_base`, `fam_b_transposed`, `fam_b_inserted`, `fam_b_deleted`
- evaluation labels: `00001111`
- graph edges: `28`
- QUBO offset for `tau=0.25`, `lambda=0.1`: `14.937301`
- quadratic terms: `28`
- maximum direct/QUBO mismatch over all assignments: about `5.33e-15`
- exact optima: `00001111`, `11110000`
- exact optima are balanced: yes
- family recovery for both optima: `1.0`
- all-assignment energy range: approximately `0.0` to `14.937301`
- balanced-assignment energy range: approximately `0.0` to `13.579168`
- uniform all-assignment expected energy: `12.036707`
- uniform balanced-assignment expected energy: `11.622336`

The tau/lambda grid in the revised plan was also reproduced. For every tested combination in `tau in {0.20, 0.25, 0.30}` and `lambda in {0.05, 0.1, 0.25, 0.5, 1.0}`, the only exact optima were `00001111` and `11110000`, both balanced and both recovering the intended family partition.

## Required Amendments Before Implementation

1. Add exact random-success probabilities to the baseline section.

   The plan already records random expected energies, but it should also record the exact probability of drawing the optimal complement class by chance:

   - uniform over all assignments: `2 / 256 = 0.00781250`
   - uniform over balanced assignments: `2 / 70 = 0.02857143`

   These values matter because the later QAOA optimal-probability threshold is explicitly justified against a random baseline.

2. Tighten the threshold-governance sentence.

   The plan currently says the exact numerical optimal-probability threshold must be registered after QUBO/Ising validation and before QAOA result generation. That is directionally correct, but the implementation task should make the threshold part of committed configuration or a committed manifest before any optimiser, estimator, or sampler output is inspected. Changing that threshold after viewing QAOA output should require a fresh review.

3. Add plan provenance to the result schema.

   The schema already includes result schema version, source commit, and fixture identifier. Add a distinct plan-provenance field such as reviewed plan path plus reviewed plan commit, so later result files can be traced to the approved EXP-005A design rather than only to the implementation commit.

4. Align terminology between plan and code.

   The plan uses `tau`; the current code calls the same parameter `dissimilar_threshold`. This is not a blocker, but the implementation should either rename user-facing fields to `tau` or explicitly map `tau` to `dissimilar_threshold` in code comments, CLI output, and result schema.

## Implementation Readiness

The revised plan is suitable for implementation once the amendments above are made. In particular:

- preserving the eight-variable benchmark is appropriate;
- `p=1` with optional `p=2` sensitivity is an educationally sound scope;
- the dense eight-qubit complete interaction graph is acceptable for local ideal simulation;
- exact enumeration remains the source of truth;
- QUBO/Ising equivalence must precede any QAOA output;
- genuine local Qiskit execution must fail clearly if optional quantum dependencies are unavailable;
- the deterministic pseudo-sampling path must be labelled as a classical fallback, never as QAOA;
- no IBM Runtime, cloud backend, credentials, hardware job, real tune corpus, or advantage claim is allowed.

## Validation Performed

Review-time checks performed:

- inspected PR #4 metadata from the earlier fetched state;
- confirmed the reviewed head SHA was `32c6badcb883fd999a92c33f8862807bcf811a41`;
- confirmed the PR diff changes only `docs/plans/EXP-005A-current-qiskit-local-plan.md`;
- inspected the revised plan, prior review, EXP-002 references, and relevant current code paths;
- independently enumerated all `256` assignments for the registered fixture using existing code;
- reproduced the registered tau/lambda grid without running Qiskit or EXP-005A.

Full project validation should be run for this review report before publishing:

```bash
python -m pytest -m "not quantum"
python -m ruff check .
python -m ruff format --check .
python scripts/check_public_safety.py
```

The known local optional-Qiskit typing issue is outside this documentation-only review and should not be fixed in this review PR.

## Final Decision

Recommendation: APPROVE WITH AMENDMENTS.

The plan no longer needs a fundamental redesign. The next safe step is to amend the plan with the four review points above, then proceed to implementation in a separate task only after that amended plan is accepted.
