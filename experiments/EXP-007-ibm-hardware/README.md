# EXP-007 — Hello Folk Music World

Status: bounded IBM Quantum hardware smoke test

Objective: verify direct authentication, transpilation and execution of one two-qubit Bell-state
circuit on operational IBM Quantum hardware. The qubits are described only as a toy
“call-and-response pair”; they do not encode a melody or solve a music problem.

Method: select the least-busy operational non-simulator backend with at least two qubits,
ISA-transpile the circuit with a preset pass manager, then use `SamplerV2` in backend job mode
with 256 finite shots. No Runtime session is used.

Credential handling: supply an external JSON file at execution time. The runner accepts exactly one
non-empty supported credential field, authenticates in memory, and does not persist or report the
credential or its path. The accepted spellings are covered by focused tests without embedding
sensitive-looking field names in public documentation.

Command:

```powershell
python experiments/EXP-007-ibm-hardware/run_hello_folk_world.py `
  --credential-file <external-json-path> `
  --shots 256 `
  --confirm-qpu
```

Classification: this is a real-QPU connectivity and execution smoke test and an infrastructure
precursor to EXP-007. It is not EXP-005A, tune-family QAOA, a music-analysis result, a use of real
folk-music data, a replacement for exact enumeration, or part of the frozen Build Week release.

Responsible interpretation: finite-shot Bell measurements can verify that the bounded execution path
works. They cannot demonstrate quantum advantage or support a claim about folk music.

Recorded execution: [RESULT.md](RESULT.md) contains the public-safe output from the single bounded
hardware job. It contains no credential value or credential-file location.
