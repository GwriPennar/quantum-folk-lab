# EXP-007A protocol-deviation audit

## Finding

The 256-shot submission was an explicit operator choice that matched a retained 256-shot runner
default. It was not caused by IBM Runtime, result generation, or count extraction.

## Evidence

- The original governing plan requested 1,024 shots.
- The committed runner at `f803d9e143e2cb84f32a3721d02e75a66ae234a1` set the command-line
  default to 256.
- The committed README example at that commit explicitly showed 256 shots.
- The actual safe execution transcript explicitly supplied `--shots 256`; the default was therefore
  not merely applied implicitly.
- `run_hardware_smoke` forwarded the selected integer unchanged to `SamplerV2.run`.
- The result-generation code rejected a returned count total different from the requested shot count.
- The preserved result contains exactly 256 counts: 119 + 5 + 1 + 131 = 256.
- The Runtime warnings recorded during execution concern account-instance selection only and do not
  report a shot substitution.

The causal classification is therefore **explicit operator choice, reinforced by a retained
default**. There is no evidence of a code defect in shot forwarding or an IBM Runtime/API override.

## Preservation decision

No additional IBM job was submitted during this audit. The completed job, backend, job identifier,
counts, software versions, and interpretation remain unchanged. It is preserved as EXP-007A, a
valid 256-shot infrastructure smoke test. It must not be described as following a 1,024-shot
protocol. Any future 1,024-shot replication is EXP-007B and requires explicit authorization.
