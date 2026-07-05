# EXP-005A Implementation Review

## Recommendation

APPROVE WITH AMENDMENTS

The EXP-005A implementation is mathematically sound, reproducible under the recorded seeds, and stays within the approved local-simulation boundary. The registered eight-tune fixture, `tau=0.25`, `lambda=0.1`, exhaustive direct/QUBO checks, exhaustive QUBO/Ising checks, exact classical ground truth, complement-equivalent optima, committed pre-QAOA threshold manifest, local Qiskit p=1 QAOA run, finite-shot sampler result, CLI surface, documentation, notebook, result artefact, and public-safety boundary are all present.

The PR should remain draft until the amendments below are made. The amendments are provenance, schema, and automated-coverage issues; they do not invalidate the recorded numerical result.

## Reviewed Material

- Implementation PR: `https://github.com/GwriPennar/quantum-folk-lab/pull/7`
- PR state at review: open draft, mergeable, targeting `main`
- PR head branch: `codex/exp-005a-tune-family-qaoa`
- Reviewed PR head: `cab31cac9417fccc874b9a56cdf9d0354b15b7ca`
- Base commit: `e2ed10d692b5ac03cd2964c691ba37de8de4eacd`
- Mandatory pre-QAOA checkpoint: `4cd27253385c349c4a4b87f67388452ea8b2cef4`
- Final implementation commit: `cab31cac9417fccc874b9a56cdf9d0354b15b7ca`
- Governing plan: `docs/plans/EXP-005A-current-qiskit-local-plan.md`
- Governing reviews:
  - `docs/reviews/EXP-005A-tune-family-qubo-plan-review.md`
  - `docs/reviews/EXP-005A-revised-plan-second-review.md`
- Result reviewed: `experiments/EXP-005A-tune-family-qaoa/results/tune-family-qaoa-p1.json`
- Threshold manifest reviewed: `experiments/EXP-005A-tune-family-qaoa/threshold-manifest.json`

The implementation PR contains no private Streamlit files and no EXP-005A material outside the public repository scope. This review did not inspect `private/`.

## Summary Findings

The scientific core passes review. The implementation uses exact brute-force enumeration as ground truth, verifies the direct objective against QUBO for all `256` assignments, verifies the QUBO/Ising mapping for all `256` basis states, and records complement-equivalent optima `00001111` and `11110000`. The Ising conversion has zero linear terms and `28` quadratic `ZZ` terms, which is valid for this symmetric dense fixture and is independently confirmed by exhaustive equivalence.

The local Qiskit path is genuine: it builds a `QAOAAnsatz`, optimises with `StatevectorEstimator`, samples with `StatevectorSampler`, and records the path as `genuine-local-qiskit`. The deterministic pseudo-sampling path is labelled separately as `classical-fallback` and is not presented as QAOA.

The registered QAOA run is reproducible under the recorded seeds. A read-only rerun of the registered 4096-shot configuration reproduced the stored expected energy, measurement counts, sampled summary, and circuit metrics exactly.

## Required Amendments

1. Align generated result schema and CLI output with the stored result provenance.

   The stored result JSON includes top-level fields such as `base_commit`, `checkpoint_commit`, and `threshold_manifest_path`, but `TuneFamilyQAOAResult` and the `tune-family-qaoa` CLI-generated payload do not produce those same top-level fields. They appear to have been added to the committed result artefact outside the result dataclass. The implementation should make these provenance fields first-class generated schema fields, or clearly document that they are post-run publication metadata. Prefer making the generator produce them so future reruns cannot silently omit them.

2. Clarify governing plan and review commit provenance.

   The threshold manifest and result record `e2ed10d692b5ac03cd2964c691ba37de8de4eacd` as the governing plan commit and for both governing review commits. That commit is a later `main` snapshot containing the approved plan and reviews, not the distinct commits where the plan and reviews entered history. The relevant document history includes `53c9b4c` for the revised plan and `10b8687` for the amended-plan approval review. The result should either record the exact document-introduction or approval commits for each governing artefact, or label `e2ed10d...` explicitly as the containing public-positioning snapshot used as implementation base.

3. Add automated coverage for the EXP-005A estimator and sampler execution path.

   The quantum tests verify Ising/operator structure, all-basis QUBO/Ising equivalence, QAOA ansatz construction, measurement binding, and missing-Qiskit error handling. They do not execute `run_tune_family_qaoa` or otherwise exercise the EXP-005A `StatevectorEstimator` plus `StatevectorSampler` path in automated tests. The registered result and CLI smoke validation do execute that path, but the test suite should include a small-shot quantum smoke test that confirms `execution_classification == "genuine-local-qiskit"`, count totals equal shots, and the classical fallback is not used.

## Mathematical Verification

Independent read-only verification using repository code produced:

- tunes: `8`
- graph edges: `28`
- `tau`: `0.25`
- `lambda`: `0.1`
- direct/QUBO verified assignments: `256`
- maximum direct/QUBO disagreement: `5.329070518200751e-15`
- QUBO/Ising verified assignments: `256`
- maximum QUBO/Ising disagreement: `2.4868995751603507e-14`
- Ising linear terms: `0`
- Ising quadratic terms: `28`
- Ising constant: `12.036707000000009`
- exact optima: `00001111`, `11110000`
- exact optimum energy: `-1.7763568394002505e-15`
- uniform all-assignment exact success probability: `0.0078125`
- uniform balanced-assignment exact success probability: `0.02857142857142857`

The threshold manifest records an optimal-class probability threshold of `0.05`, which is `6.4x` the uniform all-assignment success probability and `1.75x` the uniform balanced-assignment success probability. The manifest was committed in checkpoint `4cd27253385c349c4a4b87f67388452ea8b2cef4` before the committed QAOA result was generated.

## QAOA Result Check

Read-only reproduction of the registered local Qiskit configuration matched the committed result:

- expected energy: `5.2872120969`
- expected objective gap: `5.2872120969`
- best sampled human bitstring: `00001111`
- probability of `00001111`: `0.259521484375`
- probability of `11110000`: `0.271484375`
- optimal complement-class probability: `0.531005859375`
- balanced sample probability: `0.7119140625`
- measurement counts matched stored result: yes
- circuit metrics matched stored result: yes

The result exceeds the precommitted `0.05` threshold and recovers an exact optimum in the finite-shot sample. This is a controlled local ideal-simulation result only; it is not evidence of quantum advantage, production readiness, real-corpus family discovery, or hardware performance.

## Checkpoint And Provenance

The PR has exactly two commits:

- `4cd27253385c349c4a4b87f67388452ea8b2cef4` - `Implement EXP-005A classical and Ising verification gates`
- `cab31cac9417fccc874b9a56cdf9d0354b15b7ca` - `Complete EXP-005A tune-family QAOA benchmark`

The diff from checkpoint to final commit contains documentation, result, notebook, and one quantum test update. It does not modify `src/`, so no executable EXP-005A source changed after the checkpoint before the recorded result was committed.

## Validation Performed

- `gh pr view 7 --json ...`: PR open, draft, mergeable, base `main`, head branch `codex/exp-005a-tune-family-qaoa`, head SHA `cab31cac9417fccc874b9a56cdf9d0354b15b7ca`
- GitHub Actions checks: `test` success, `quantum-exp-001` success
- `python -m pytest -m "not quantum"`: `24 passed, 18 deselected`
- `python -m pytest -m quantum`: `18 passed, 24 deselected`, with Qiskit deprecation warnings
- `python -m pytest`: `42 passed`, with Qiskit deprecation warnings
- `python -m ruff check .`: passed
- `python -m ruff format --check .`: passed
- `python scripts/check_public_safety.py`: passed
- `python -m mypy`: failed with the known optional-Qiskit missing-stub and unused-ignore errors in pre-existing Qiskit modules outside EXP-005A; no EXP-005A file was reported

The Qiskit deprecation warnings come from current `QAOAAnsatz`/`NLocal` internals under Qiskit 2.5.0 and should be tracked before Qiskit 3.0, but they do not block this local reference experiment.

## Safety And Scope

- No IBM Runtime use found.
- No cloud backend use found.
- No QPU or hardware execution found.
- No IBM token or credential handling found.
- No real private tune corpus used.
- No private Streamlit workspace content reviewed or published.
- No quantum-advantage claim found.
- No Max-Cut approximation-ratio framing found for EXP-005A.
- Classical fallback remains labelled as classical fallback, not QAOA.

## Final Decision

Recommendation: APPROVE WITH AMENDMENTS.

Gwri can treat the numerical and mathematical result as valid for review purposes. Before PR #7 is marked ready or merged, amend the provenance/schema mismatch and add an automated quantum smoke test for the EXP-005A estimator/sampler path.
