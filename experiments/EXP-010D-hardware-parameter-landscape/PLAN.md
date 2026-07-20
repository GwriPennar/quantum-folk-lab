# EXP-010D hardware parameter-landscape plan

## Status and question

This is an offline protocol freeze only. IBM was not contacted, no credential was read, no
backend was queried, no Runtime service was constructed, and no workload was submitted.

EXP-010D asks whether hardware preserves the local parameter-landscape structure predicted by
the frozen ideal four-qubit model, rather than merely producing a positive result at one selected
parameter pair. It is not an optimisation run, and hardware observations may not retune the grid.

## Frozen inheritance

- QUBO SHA-256: `96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e`
- Ising SHA-256: `635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5`
- Logical order and Qiskit classical-bit reversal remain unchanged.
- Circuit family: H/RZ/RZZ/RX/measurement, no postselection.
- Exact energy evaluation and `R=(E_uniform16-E_observed)/(E_uniform16-E_min)` are frozen.
- Exact optimum: `1010`; shots: 4,096 per execution.

## Proposed workload

One future SamplerV2 job contains 32 PUB executions: each of 24 non-centre grid points once,
the centre four times total, and the zero-angle uniform control four times. The deterministic
four-block sequence is frozen in `execution-order.json`. Automatic retries are forbidden.

The later preflight targets only `ibm_fez`, requires layout `[20, 21, 23, 22]`, uses transpiler
seed `44`, transpiles one parameterised circuit once, hashes the ISA QPY, and binds the 32 rows
only after manifest verification. Failure of the backend, layout, existing hardware gates, or
the 180-second conservative usage ceiling is a NO-GO; no alternate backend or layout is allowed.

## Safety boundary

Submission defaults off and requires the new exact phrase
`I AUTHORIZE ONE EXP-010D IBM QPU JOB` plus separate credential-file authorization. A durable
intent precedes credential access, a receipt follows submission immediately, any existing intent
or receipt blocks submission, and any post-intent exception is ambiguous and never retried. The
EXP-010C authorization phrase cannot authorize EXP-010D.

No credential, intent, receipt, backend snapshot, parameterised QPY, or result belongs in this
plan-only package. Future execution requires human review, a read-only preflight, and explicit
one-job authorization.

## Interpretation limits

An eventual result may address only local-landscape preservation, within-job repeatability,
comparison with the frozen control, and possible displacement of the best hardware cell. It
cannot establish quantum advantage, speedup, optimisation superiority, generalisation,
cross-calibration reproducibility, or commercial usefulness. Exact classical search remains the
ground truth.
