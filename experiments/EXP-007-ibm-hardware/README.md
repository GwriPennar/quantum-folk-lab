# EXP-007A — Hello Folk Music World

Status: preserved 256-shot IBM Quantum hardware smoke test.

Objective: verify direct authentication, transpilation and execution of one two-qubit Bell-state
circuit on operational IBM Quantum hardware. The qubits are described only as a toy
“call-and-response pair”; they do not encode a melody or solve a music problem.

## Protocol and post-run review

The original governing plan requested 1,024 shots. The first bounded hardware run instead executed
with 256 shots because the submission command explicitly supplied 256, matching the runner's retained
256-shot default and its then-current example. Post-run review identified this protocol deviation.
The completed job is preserved as EXP-007A; it has not been altered, regenerated, or rerun.

The preserved run used an operational non-simulator backend, ISA-transpiled the Bell circuit with a
preset pass manager, and used `SamplerV2` in backend job mode. No Runtime session was used. The
public-safe result is recorded in [RESULT.md](RESULT.md), and the causal audit is recorded in
[AUDIT.md](AUDIT.md).

Any future 1,024-shot replication would be a separate **EXP-007B** experiment and requires explicit
authorization. Merely running the script, tests, documentation checks, or report generation cannot
submit hardware work. A future authorized invocation must supply both `--submit-hardware` and the
exact confirmation phrase `I AUTHORIZE ONE IBM QPU JOB`; omission or variation fails closed before
the Runtime client is imported or constructed.

Credential handling: an authorized operator supplies an external JSON file at execution time. The
runner accepts exactly one non-empty supported credential field, authenticates in memory, and does
not persist or report the credential or its path.

Classification: EXP-007A is a real-QPU connectivity and execution smoke test. It is not QAOA,
EXP-005A, a music-analysis result, a use of real folk-music data, evidence of quantum advantage, a
replacement for exact enumeration, or part of the frozen Build Week release on `main`.
