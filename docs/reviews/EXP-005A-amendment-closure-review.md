# EXP-005A Amendment Closure Review

## Recommendation

APPROVE

All three amendments required by the independent implementation review are closed. PR #7 may be marked ready and merged after human approval, this closure-review report is merged, `main` branch protection is enabled, required checks pass on the final PR head, and any required review conversations are resolved.

This is a review-only report. It does not modify PR #7 implementation code, mark PR #7 ready, or merge PR #7.

## Reviewed Material

- Implementation PR: `https://github.com/GwriPennar/quantum-folk-lab/pull/7`
- Previous reviewed head: `cab31cac9417fccc874b9a56cdf9d0354b15b7ca`
- Current amended head: `1d0a66abe3866603df515d5e91d94d50986b8c8c`
- Mandatory pre-QAOA checkpoint: `4cd27253385c349c4a4b87f67388452ea8b2cef4`
- Merge-from-main commit on implementation branch: `56d102e9e3819f5be1715101f27f2e9961fbd497`
- Merged independent review commit: `1370749cbf76b25a902d20b829bbeb34beaa9aaf`
- Amendment commit: `1d0a66abe3866603df515d5e91d94d50986b8c8c`
- Review report being closed: `docs/reviews/EXP-005A-implementation-review.md`

At review time, PR #7 was open, draft, unmerged, targeting `main`, mergeable, and at the expected amended head `1d0a66abe3866603df515d5e91d94d50986b8c8c`.

## Branch History

The branch history preserves the original implementation chronology. The mandatory checkpoint `4cd27253385c349c4a4b87f67388452ea8b2cef4`, completed implementation commit `cab31cac9417fccc874b9a56cdf9d0354b15b7ca`, merge-from-main commit `56d102e9e3819f5be1715101f27f2e9961fbd497`, and amendment commit `1d0a66abe3866603df515d5e91d94d50986b8c8c` are all in the current PR ancestry.

The delta from `cab31cac...` to `56d102e...` only brings in the already-merged independent review report from `main`. The actual amendment commit changes only EXP-005A schema, CLI, tests, result/provenance artefacts, and EXP-005A documentation. No `.gitignore` or `private/` path is changed.

## Amendment 1: Generated Provenance Schema

Closed.

`TuneFamilyQAOAResult` now declares first-class provenance fields:

- `base_commit`
- `implementation_base_commit`
- `checkpoint_commit`
- `executable_source_commit`
- `threshold_manifest_path`
- `governing_plan_path`
- `governing_plan_commit`
- `governing_plan_version`
- `governing_review_paths`
- `governing_review_commits`
- `result_schema_version`
- `run_identifier`
- `fixture_identifier`
- `execution_classification`

`run_tune_family_qaoa(...)` now emits these fields directly, and `to_dict()` serialises them without manual JSON augmentation. The `tune-family-qaoa` and `tune-family-compare` CLI routes pass the same provenance constants into the generator. The committed primary result JSON and nested threshold manifest now agree with generated output.

A direct generated 16-shot result confirmed:

- execution classification: `genuine-local-qiskit`
- measurement count total: `16`
- logical problem qubits: `8`
- expected energy is produced as a float
- fallback remains labelled `classical-fallback`
- threshold remains `0.05`
- all required provenance fields are present in `to_dict()`

The 32-shot CLI checks confirmed that `tune-family-qaoa` and `tune-family-compare` emit matching first-class provenance fields and keep expected metrics separate from sampled metrics.

## Amendment 2: Governing Commit Provenance

Closed.

Generated output and stored artefacts now distinguish the governing document commits from the implementation base and threshold checkpoint:

- governing plan: `docs/plans/EXP-005A-current-qiskit-local-plan.md`
- governing plan commit: `53c9b4cf13375a842a5d5d095629c1fbc67ffb28`
- first design review: `docs/reviews/EXP-005A-tune-family-qubo-plan-review.md`
- first design review commit: `38e07a00867d5d6fe05760abf35ef3943a1df949`
- final amended-plan approval review: `docs/reviews/EXP-005A-revised-plan-second-review.md`
- approval review commit: `10b86878ae64eaeb82080d9fab897bea42e4b8cf`
- implementation base commit: `e2ed10d692b5ac03cd2964c691ba37de8de4eacd`
- threshold checkpoint: `4cd27253385c349c4a4b87f67388452ea8b2cef4`
- executable source commit for the registered result: `4cd27253385c349c4a4b87f67388452ea8b2cef4`

The threshold manifest now includes a provenance clarification stating that the branch version clarifies governing document provenance after independent review and does not alter the pre-QAOA threshold, fixture, QAOA configuration, or scientific criteria registered at the threshold checkpoint.

The historical checkpoint was not rewritten.

## Amendment 3: Genuine Qiskit Smoke Test

Closed.

`tests/test_exp005a_tune_family_qiskit.py::test_exp005a_genuine_qiskit_estimator_sampler_smoke` calls `run_tune_family_qaoa(...)` with a bounded test configuration:

- one initial point: `(0.2, 0.2)`
- optimiser max iterations: `1`
- shots: `16`

This still executes the genuine EXP-005A Qiskit route: `QAOAAnsatz`, `StatevectorEstimator`, `StatevectorSampler`, estimator evaluation, and finite-shot sampling. It does not substitute a classical fallback or hard-code an optimum. The reductions are test-only and do not change production defaults or the registered primary result configuration.

The test asserts:

- `execution_classification == "genuine-local-qiskit"`
- measurement count total equals requested shots
- sampled distribution exists
- expected energy is produced
- logical problem qubits equal `8`
- classical fallback remains explicitly labelled `classical-fallback`
- generated provenance fields are present
- threshold remains `0.05`

Observed smoke-test runtime in the quantum suite: about `1.55s`.

## Primary Result Integrity

Closed.

The registered primary result remains unchanged:

- shots: `4096`
- expected energy: `5.2872120969`
- expected gap: `5.2872120969`
- `P(00001111)`: `0.259521484375`
- `P(11110000)`: `0.271484375`
- optimum complement-class probability: `0.531005859375`
- balanced-sample probability: `0.7119140625`
- threshold: `0.05`
- `tau`: `0.25`
- `lambda`: `0.1`
- QAOA depth: `1`
- optimiser budget: `80`
- initial points: `[0.2, 0.2]`, `[0.5, 0.5]`, `[0.8, 0.3]`, `[1.0, 0.7]`

The stored result JSON changes are provenance/schema updates only. The 16-shot smoke test and 32-shot CLI checks did not replace the registered 4,096-shot result.

## Mathematical Integrity

Closed.

Focused verification confirmed:

- tune order remains `fam_a_base`, `fam_a_transposed`, `fam_a_substitution`, `fam_a_rhythm`, `fam_b_base`, `fam_b_transposed`, `fam_b_inserted`, `fam_b_deleted`
- graph edge count remains `28`
- `tau` remains `0.25`
- `lambda` remains `0.1`
- direct/QUBO verified assignments: `256`
- maximum direct/QUBO disagreement: `5.329070518200751e-15`
- QUBO/Ising verified assignments: `256`
- maximum QUBO/Ising disagreement: `2.4868995751603507e-14`
- Ising linear terms: `0`
- Ising quadratic terms: `28`
- exact optima: `00001111`, `11110000`
- canonical complement class: `00001111`
- family recovery: `1.0`

No fixture, tune ordering, objective, QUBO coefficients, Ising coefficients, exact optima, equivalence checks, complement canonicalisation, or label-independence boundary changed.

## CLI Closure Checks

Closed.

The active Qiskit-capable Python environment was used because `.venv-qiskit` is absent in this worktree.

`python -m quantum_folk_lab.cli tune-family-qaoa --shots 32` and `python -m quantum_folk_lab.cli tune-family-compare --shots 32` both produced:

- `run_identifier`: `synthetic-two-family-v1-seed42-p1-shots32-seed42`
- `base_commit`: `e2ed10d692b5ac03cd2964c691ba37de8de4eacd`
- `implementation_base_commit`: `e2ed10d692b5ac03cd2964c691ba37de8de4eacd`
- `checkpoint_commit`: `4cd27253385c349c4a4b87f67388452ea8b2cef4`
- `executable_source_commit`: `4cd27253385c349c4a4b87f67388452ea8b2cef4`
- `source_commit`: `4cd27253385c349c4a4b87f67388452ea8b2cef4`
- `threshold_manifest_path`: `experiments/EXP-005A-tune-family-qaoa/threshold-manifest.json`
- `governing_plan_commit`: `53c9b4cf13375a842a5d5d095629c1fbc67ffb28`
- `governing_review_commits`: `38e07a00867d5d6fe05760abf35ef3943a1df949`, `10b86878ae64eaeb82080d9fab897bea42e4b8cf`
- `fixture_identifier`: `synthetic-two-family-v1-seed42`
- `execution_classification`: `genuine-local-qiskit`
- sampled shots: `32`
- measurement count total: `32`

The compare output also preserved `exact_solver_is_ground_truth`, `expected_and_sampled_metrics_are_distinct`, `no_maxcut_approximation_ratio_used`, and `no_quantum_advantage_claimed`.

## Validation

- `python -m pytest -m "not quantum"`: `26 passed, 19 deselected`
- `python -m pytest -m quantum --durations=10`: `19 passed, 26 deselected`, `17` warnings
- `python -m pytest`: `45 passed`, `17` warnings
- `python -m ruff check .`: passed
- `python -m ruff format --check .`: passed
- `python scripts/check_public_safety.py`: passed
- `python -m mypy`: failed with the known pre-existing optional-Qiskit missing-stub and unused-ignore errors in:
  - `src/quantum_folk_lab/quantum_basics.py`
  - `src/quantum_folk_lab/maxcut_ising.py`
  - `src/quantum_folk_lab/simulation.py`
  - `src/quantum_folk_lab/qubo/qiskit_adapter.py`
  - `src/quantum_folk_lab/maxcut_qaoa.py`

No EXP-005A file appears in the mypy failure list.

GitHub checks on PR #7:

- `test`: pass
- `quantum-exp-001`: pass

## Safety

No IBM Runtime use, cloud backend use, QPU execution, credentials, real tune corpus, private data, private Streamlit change, quantum-advantage claim, force-push, rebase, or checkpoint rewrite was found.

## Non-Blocking Notes

- The quantum suite still reports Qiskit deprecation warnings from current `QAOAAnsatz`/`NLocal` internals. This is not a closure blocker, but it should remain on the Qiskit 3.0 migration watchlist.
- The bounded smoke test asks COBYLA for fewer evaluations than SciPy's recommended minimum, producing a warning. This is acceptable for a CI smoke test because it is testing the estimator/sampler path, not optimiser quality.

## Final Decision

Recommendation: APPROVE.

The three independent-review amendments are closed. PR #7 may proceed to human merge decision after this closure-review report is merged, human approval is given, `main` branch protection is enabled, required checks pass, and review conversations are resolved.
