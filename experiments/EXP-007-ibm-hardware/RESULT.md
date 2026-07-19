# EXP-007 — Hello Folk Music World result

Execution classification: real-QPU connectivity and execution smoke test.

## Public-safe execution record

- Backend: `ibm_kingston` (operational, non-simulator hardware)
- Runtime job ID: `d9eism2neu4c739ogln0`
- Requested and returned shots: 256
- Qiskit: 2.5.0
- qiskit-ibm-runtime: 0.48.0
- Logical circuit: two qubits and two classical bits
- ISA circuit: backend-wide 156-qubit representation, depth 8
- Counts: `00`: 119, `01`: 5, `10`: 1, `11`: 131
- Correlated outcomes (`00` or `11`): 250/256 (97.65625%)

The circuit prepared and measured a Bell pair. The two logical qubits are described only as a toy
“call-and-response pair.” The label is thematic: no melody, music feature, corpus, or real folk-music
data was encoded or analysed.

## Interpretation boundary

This successful result verifies the bounded direct-authentication, hardware selection,
ISA-transpilation, SamplerV2 backend-job, and V2 count-extraction path. It is an infrastructure
precursor to EXP-007. It is not the registered EXP-005A result, the eight-qubit tune-family QAOA
experiment, a replacement for exact enumeration, evidence of quantum advantage, or part of the
frozen OpenAI Build Week submission release.

Credential material was supplied only to the process in memory. The recorded result contains no
token and no credential-file location; no account was saved by the experiment.
