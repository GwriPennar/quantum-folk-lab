# EXP-007A — Hello Folk Music World: IBM hardware smoke-test result

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
- Unexpected outcomes (`01` or `10`): 6/256 (2.34375%)

The circuit prepared and measured a Bell pair. The two logical qubits are described only as a toy
“call-and-response pair.” The label is thematic: no melody, music feature, corpus, or real folk-music
data was encoded or analysed.

The predeclared smoke-test success band was correlated-state mass greater than or equal to 0.90;
the observed 0.9765625 is within that band. The original plan requested 1,024 shots, but this first
bounded run executed at 256 shots. Post-run review identified the deviation. The result is preserved
as executed rather than rewritten or rerun; a future 1,024-shot replication would be a separately
authorized EXP-007B experiment.

## Interpretation boundary

This successful result verifies the bounded direct-authentication, hardware selection,
ISA-transpilation, SamplerV2 backend-job, and V2 count-extraction path. It is an infrastructure
precursor to later work. It is not the registered EXP-005A result, the eight-qubit tune-family QAOA
experiment, a replacement for exact enumeration, evidence of quantum advantage, or part of the
frozen OpenAI Build Week submission release.

Credential material was supplied only to the process in memory. The recorded result contains no
token and no credential-file location; no account was saved by the experiment.
