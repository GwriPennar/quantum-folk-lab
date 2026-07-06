# EXP-005A Result

EXP-005A successfully executed a genuine local Qiskit p=1 QAOA reference experiment for the registered synthetic tune-family QUBO.

## Verification

The registered fixture `synthetic-two-family-v1-seed42` contains eight tunes and all 28 pairwise similarity edges. With `tau = 0.25` and `lambda = 0.1`, exhaustive enumeration over all 256 assignments found exactly two complement-equivalent optima:

- `00001111`
- `11110000`

The exact optimum energy is approximately zero. Both optima are balanced and recover the intended family partition with family recovery `1.0`.

The direct scientific objective and expanded QUBO agree for all 256 assignments with maximum disagreement `5.329070518200751e-15`. The QUBO and Ising mapping agree for all 256 assignments with maximum disagreement `2.4868995751603507e-14`.

## Precommitted Threshold

The pre-QAOA threshold manifest fixes the optimal complement-class probability threshold at `0.05`.

This threshold was registered before QAOA output was generated. It is above both random exact-success baselines:

- all assignments: `0.00781250`
- balanced assignments: `0.02857143`

## QAOA Result

- execution classification: `genuine-local-qiskit`
- depth: `p=1`
- optimiser: `COBYLA`
- shots: `4096`
- expected energy: `5.2872120969`
- expected gap: `5.2872120969`
- best sampled bitstring: `00001111`
- best sampled energy: approximately `0.0`
- optimal complement-class probability: `0.531005859375`
- balanced-sample probability: `0.7119140625`
- family recovery for the best sampled partition: `1.0`

The sampled distribution recovered an exact optimum and exceeded the precommitted probability threshold. The expected energy remains substantially above the exact optimum, so the result is a successful local execution and sampling result, not evidence that QAOA is a useful solver for this instance.

## Independent Review Amendments

The independent implementation review was merged at
`1370749cbf76b25a902d20b829bbeb34beaa9aaf` with recommendation
`APPROVE WITH AMENDMENTS`. The amendments clarify provenance, make generated
schema and CLI output consistent, and add automated genuine-Qiskit estimator/sampler
smoke coverage.

The governing provenance is now first-class generated result data:

- implementation base commit: `e2ed10d692b5ac03cd2964c691ba37de8de4eacd`
- threshold checkpoint: `4cd27253385c349c4a4b87f67388452ea8b2cef4`
- executable source commit for the registered result:
  `4cd27253385c349c4a4b87f67388452ea8b2cef4`
- governing plan commit: `53c9b4cf13375a842a5d5d095629c1fbc67ffb28`
- governing review commits:
  `38e07a00867d5d6fe05760abf35ef3943a1df949`,
  `10b86878ae64eaeb82080d9fab897bea42e4b8cf`

These amendments do not change the mathematical formulation, threshold `0.05`,
registered fixture, primary QAOA configuration, or registered 4,096-shot numerical
result.

## Interpretation

Exact enumeration remains the source of truth. Brute force is superior for this eight-variable fixture. The result validates the formulation, QUBO/Ising conversion, bit ordering, local Qiskit execution, finite-shot sampling, and reporting path.

No IBM Runtime service, cloud backend, credentials, hardware execution, QPU job, real tune corpus, quantum-advantage claim, or production-readiness claim is introduced.
