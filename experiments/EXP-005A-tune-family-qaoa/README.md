# EXP-005A Tune-Family QAOA

Status: implemented as a local ideal-simulation reference benchmark

EXP-005A formulates the registered eight-tune synthetic fixture as a two-family signed graph-partitioning QUBO and runs a genuine local Qiskit p=1 QAOA reference experiment. It is not direct Max-Cut and does not use Max-Cut approximation-ratio terminology.

The experiment uses only deterministic synthetic tunes from `synthetic-two-family-v1-seed42`. It uses no IBM Runtime service, no cloud backend, no credentials, and no QPU execution.

## Registered Fixture

- tune count: `8`
- tune order: `fam_a_base`, `fam_a_transposed`, `fam_a_substitution`, `fam_a_rhythm`, `fam_b_base`, `fam_b_transposed`, `fam_b_inserted`, `fam_b_deleted`
- evaluation labels: `00001111`
- graph edges: `28`
- pair threshold `tau`: `0.25`
- balance penalty `lambda`: `0.1`
- exact optima: `00001111`, `11110000`
- canonical complement class: `00001111`

The labels are used only for evaluation. They are not used in fixture generation, similarity scoring, graph construction, QUBO coefficients, exact enumeration, QAOA optimisation, or sampling.

## Verification Gates

- all `256` direct-objective/QUBO comparisons pass with maximum disagreement `5.329070518200751e-15`
- all `256` QUBO/Ising comparisons pass with maximum disagreement `2.4868995751603507e-14`
- both exact optima are balanced and recover the intended partition up to complement
- the pre-QAOA threshold manifest was committed before any QAOA output was generated

The precommitted optimal complement-class probability threshold is `0.05`. It is compared against random success probabilities `2 / 256 = 0.00781250` and `2 / 70 = 0.02857143`.

## Registered QAOA Run

- execution classification: `genuine-local-qiskit`
- QAOA depth: `p=1`
- optimiser: `COBYLA`
- optimiser budget: `80`
- initial points: `[0.2, 0.2]`, `[0.5, 0.5]`, `[0.8, 0.3]`, `[1.0, 0.7]`
- shots: `4096`
- sampler seed: `42`
- estimator seed: `42`
- transpiler seed: `42`

Summary:

- exact minimum energy: approximately `0.0`
- expected QAOA energy: `5.2872120969`
- expected objective gap: `5.2872120969`
- best sampled bitstring: `00001111`
- best sampled energy: approximately `0.0`
- probability of `00001111`: `0.259521484375`
- probability of `11110000`: `0.271484375`
- optimal complement-class probability: `0.531005859375`
- balanced-sample probability: `0.7119140625`
- family recovery for best sample: `1.0`

The sampled distribution exceeds the precommitted optimal-probability threshold and recovers an exact optimum. The expected energy remains far above the exact optimum, so the result should be interpreted cautiously.

## Circuit Metrics

- logical problem qubits: `8`
- classical bits: `8`
- total Qiskit circuit width: `16`
- width definition: logical problem qubits plus classical bits after measurement
- raw circuit depth: `42`
- transpiled depth: `42`
- two-qubit gate count: `56`
- parameter count: `2`
- Hamiltonian term count: `28`
- interaction-graph density: `1.0`

## Result Files

- `threshold-manifest.json`: pre-QAOA registration and threshold rationale
- `results/tune-family-qaoa-p1.json`: structured exact/QAOA/sampling result

## Provenance Clarification

The independent implementation review required provenance fields to be generated directly by
the schema and CLI output rather than added after result generation. The current schema records:

- implementation base commit: `e2ed10d692b5ac03cd2964c691ba37de8de4eacd`
- threshold checkpoint and executable source commit:
  `4cd27253385c349c4a4b87f67388452ea8b2cef4`
- governing plan commit: `53c9b4cf13375a842a5d5d095629c1fbc67ffb28`
- governing review commits:
  `38e07a00867d5d6fe05760abf35ef3943a1df949`,
  `10b86878ae64eaeb82080d9fab897bea42e4b8cf`

This clarification does not change the mathematical formulation, registered fixture,
`tau=0.25`, `lambda=0.1`, threshold `0.05`, primary QAOA configuration, or the
registered 4,096-shot numerical result.

## Limitations

Brute-force enumeration is superior for this eight-variable benchmark and remains the source of truth. This is a local ideal-simulation reference result, not evidence of quantum advantage, hardware behaviour, real-corpus family discovery, or production readiness.
