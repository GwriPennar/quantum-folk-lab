# Build Week Codex contribution log

## Evidence boundary

- Pre-Build Week public baseline: `281ba4013112a071bba4a70579c24d051da36c51`.
- Build Week governing-plan baseline: `3950a1f4f6c7c3f65c613133dec6dd8075739f57`.
- Judged implementation: product work after the governing-plan baseline.

This Codex conversation is the primary implementation session.

## Stage 1 — validated deterministic core

Codex contributions:

- inspected the public fixture, similarity, graph, QUBO, Ising, exact, CLI, learning, and safety APIs;
- implemented versioned demo-state and result-envelope contracts;
- composed existing public scientific functions into one exact-first workflow;
- added three learner-level deterministic explanations, claim validation, JSON/Markdown exports, CLI access, and tests;
- preserved the registered EXP-005A fixture, configuration, numerical evidence, and provenance artefacts.

Gwri decisions governing this work:

- use the fixed `synthetic-two-family-v1-seed42` fixture;
- keep exact enumeration authoritative;
- separate current exact, current quick-Qiskit, and historical registered evidence;
- require deterministic operation without Qiskit, Streamlit, OpenAI, network access, or credentials;
- prioritise a coherent Education journey over optional scope.

## Primary-session feedback evidence

Codex Session ID supplied privately through the Devpost submission form.

The identifier is intentionally excluded from public repository evidence.

## Stage 2 — Guided Experiment product

Codex contributions:

- made Guided Experiment the prominent Learning Console route, alongside Foundations and
  Glossary;
- reused the Stage 1 validated result envelope for evidence, exact results, learner-level
  explanations, and reproducibility downloads;
- added a bounded adapter around the existing genuine local-Qiskit route using p=1, 256 shots,
  fixed registered seeds, one fixed initial point, and eight optimiser iterations;
- measured the quick route locally and kept current exact, current quick-Qiskit, and historical
  registered 4,096-shot evidence explicitly separated;
- added an optional Responses API adapter defaulting to `gpt-5.6-sol`, with a filtered input,
  strict JSON schema, grounding checks, claim checks, numeric checks, and deterministic fallback;
- added fake-client, capability, service, navigation, and adapter tests and completed a Streamlit
  AppTest runtime audit.

Gwri decisions governing this stage:

- the exact path must remain complete without Qiskit, OpenAI, network access, or credentials;
- optional controls must not turn the product into a developer dashboard;
- only the standard OpenAI SDK credential environment variable may be used as a runtime secret,
  and it must never be displayed or saved;
- the deterministic musical preview was omitted to protect the reliability and clarity of P0/P1.

## Stage 3 — in-app 256 Reveal

Codex contributions:

- inspected the registered fixture, exact solver, objective, and unchanged EXP-005A evidence before
  designing an additive presentation layer;
- constructed a pure exact-landscape read model from existing scientific functions, enumerated all
  256 assignments, verified complement symmetry, retained both exact optima, and kept `00001111`
  as the canonical representative rather than the only optimum;
- reused direct/QUBO and QUBO/Ising verification and validated the tracked measurement evidence
  before presenting it;
- built the gated Streamlit reveal, readable 16×16 landscape, accessible 256-row table, exact
  metrics, and registered comparison;
- kept the registered p=1, 4,096-shot optimum-class evidence separate from the optional current
  p=1, 256-shot quick run;
- added focused numerical, evidence-integrity, no-key, no-Qiskit, and Streamlit AppTest coverage;
- diagnosed the CI-only CRLF/LF hash mismatch and made the evidence-integrity test portable without
  changing the evidence;
- conducted desktop, narrow-width, light/dark, no-capability, and timed visual review before the
  final merge.

Gwri decisions governing this stage:

- reopen the frozen release only for a bounded, judge-visible improvement;
- preserve the exact-first evidence hierarchy and show both complement-equivalent optima;
- present registered QAOA only as local ideal-simulator evidence, never hardware or advantage
  evidence;
- keep GPT-5.6 explanatory rather than evidential;
- accept the final visual review, reject further cosmetic code changes, and approve the squash
  merge of PR #20.

All Codex work remained subject to human review and merge authority. The private Session ID stayed
outside the public repository.

## Stage 4 — governed real data and formulation gates

Codex implemented and verified public-source provenance records, licence gates, deterministic
symbolic fixtures, QUBO/Ising equivalence checks, and exact truth gates. Weak, ambiguous, or
non-detectable formulations were preserved as negative results rather than promoted. GPT-5.6
helped frame explanations and review language only; deterministic code established every value.
Gwri chose the sources, accepted or rejected candidate formulations, and required explicit stops
when provenance, detectability, or interpretability failed.

Safety gates could stop work for uncertain licensing, transcription ambiguity, exact/QUBO/Ising
disagreement, weak signal, changed evidence, or any pressure to overstate musical meaning.

## Stage 5 — compact encoding and fail-closed IBM preparation

Codex developed the compact four-qubit encoding, verified the exact optimum `1010`, prepared
bounded simulator comparisons, and implemented hardware-layout, routing, measurement-decoding,
usage, immutable-intent, durable-receipt, one-job, and zero-retry controls. Layout and receipt
reviews found and corrected real safety defects before execution. GPT-5.6 did not select a backend,
layout, shot count, threshold, or submission action. Gwri approved every frozen protocol and alone
supplied each exact hardware-authorization phrase.

Preflight failed closed on missing credentials, properties, layout/decoding disagreement, excessive
estimated usage, stale intent or receipt, or any ambiguous submission state.

## Stage 6 — EXP-010D supported landscape

Codex packaged the frozen 25-cell landscape, locally validated the parameterised ISA circuit,
submitted only after Gwri's exact authorization, retrieved the recorded job, regenerated the
sanitized result, repaired mechanical CI portability issues, and verified the result PR. The one
`ibm_fez` job returned 32/32 PUBs; ideal-versus-hardware rho was `0.96`, the centre ranked first,
and classification was **LANDSCAPE SUPPORTED**. The predeclared control-quality warning remained.

Gwri decided that the warning must remain visible, that no retry was permitted, and that the result
supported only the frozen small landscape—not advantage, speedup, or musical truth.

## Stage 7 — EXP-011 dense independent replication

Codex constructed the exact-decimal 9×9 grid, embedded all original 25 cells, froze the 88-PUB
order, generated the ideal landscape, enforced a fresh identity/intent/receipt boundary, and ran
the single job only after Gwri's exact authorization. It retrieved 88/88 PUBs, applied the frozen
100,000-permutation and 10,000-bootstrap analysis, regenerated evidence byte-identically, repaired
result-field and CI issues without rerunning hardware, and prepared PR #38.

The full 81-cell rho was `0.9046747967479675`, embedded-25 rho was
`0.9315384615384615`, and cross-run rho was `0.9776923076923076`; classification was **STRONGLY
REPLICATED**. The centre ranked `4/81`, inside the frozen top-five check, and the control warning
remained. Gwri authorized the job, reviewed the interpretation, and approved the merge. GPT-5.6
remained explanatory and did not influence statistics or claims.

Across the hardware era, Codex never possessed scientific or hardware authority: human approval
selected the research question, froze each protocol, supplied each authorization phrase, accepted
warnings, and controlled every merge. The Session ID remains private and absent from public files.
