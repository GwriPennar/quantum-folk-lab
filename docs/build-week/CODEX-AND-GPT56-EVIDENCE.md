# Codex and GPT-5.6 evidence

## Codex contribution

This conversation is the primary Build Week implementation session. Codex verified the checkout,
baseline, public architecture, registered fixture, exact/QUBO/Ising routes, Qiskit route, Learning
Console, tests, and safety scanner, then accelerated the bounded implementation and verification
sequence governed and approved by Gwri:

- PR #16, **feat: add Build Week deterministic experiment core**, merge
  `39489b0422715936bb9059c7d70cbc8ef4a5e4d0`;
- PR #17, **feat: add Build Week Guided Experiment**, merge
  `06f55317a8d38ac0c5d22285793cabf3ebb40b48`;
- PR #18, **docs: prepare Quantum Folk Lab Build Week release**, merge
  `120016459c45c26066188602a463bde1f68f630b`;
- PR #19, **docs: finalize Build Week submission guidance**, merge
  `b900a08bedea6bc834d61825730cee5e36fb9a18`;
- PR #20, **feat: add the in-app 256 reveal**, merge
  `a5a43bff1fc078094005100878e39374e727c4b3`.
- PR #22, **exp: record Hello Folk Music World IBM hardware run**, preserved the disclosed
  256-shot infrastructure smoke test and one-job controls;
- PRs #24–#28, real-data selection and truth gates, preserved licence/provenance decisions and
  rejected weak or non-detectable formulations rather than manufacturing a positive result;
- PR #29, **EXP-010B compact hardware protocol**, merged the fail-closed four-qubit package;
- PR #31, **exp: record EXP-010C IBM hardware result**, recorded one controlled hardware
  validation;
- PRs #32–#36 froze, corrected, executed, and published EXP-010D, culminating in merge
  `38097de33ed8894c560e95f98510982a7269b667`;
- PR #37 froze the exact-decimal EXP-011 dense replication plan, merge
  `ab5180fac52a759563327bbbbdd2d35706b3e522`;
- PR #38 published the one-job EXP-011 result, merge
  `104a6c87d39ea953ca9281ff9534d85890abb663`.

Codex accelerated contract and adapter construction, renderer composition, focused tests, CI
diagnosis, runtime audits, public-safety verification, release documentation, and rendered visual
review. PR #20 is the judge-visible centrepiece: it reuses the registered synthetic objective to
enumerate and present all 256 assignments, both complement-equivalent optima, and the registered
QAOA comparison. It changed no registered EXP-005A evidence and works without an OpenAI key or
Qiskit installation.

## Human decisions

Gwri authored or approved the governing direction and retained final authority over the fixed
synthetic fixture, Education category, exact-first authority, learner levels, Guided Experiment
hierarchy, distinction between registered and live evidence, p=1/256-shot quick-run boundary,
optional `gpt-5.6-sol` feature, privacy boundary, deferred scope, visual acceptance, and staged
merges. Codex did not independently choose the scientific direction.

## GPT-5.6 runtime boundary

GPT-5.6 Sol optionally rewrites a validated result for the selected learner level. It receives no
arbitrary prompt, repository file, secret, environment dump, or hidden evidence. A strict response
schema and post-response checks enforce grounded fields, known numeric values, exact-result
consistency, and prohibited-claim policy. Scientific values always come from deterministic code.
The deterministic explanation is the complete fallback.

Deterministic code establishes the scientific result before GPT-5.6 is invoked. Input is filtered;
output is schema-, grounding-, number-, and claim-checked. GPT-5.6 cannot calculate the optimum,
change registered values, or convert local ideal-simulator evidence into a hardware or advantage
claim. **The AI can explain the experiment. It cannot rewrite the evidence.**

## Hardware-era responsibility matrix

| Stage | Codex implemented or verified | GPT-5.6 contribution | Human decision | Stop gate |
| --- | --- | --- | --- | --- |
| Real-data gating | provenance/licence records, deterministic parsers and tests | explanatory framing only | source choice and cultural/scientific acceptability | uncertain licence, provenance or transcription |
| Truth gates | exact QUBO/Ising checks and detectability audits | review-language support | reject or retain a formulation | disagreement, weak signal or ambiguous meaning |
| Compact encoding | four-qubit contract, exact optimum and simulator evidence | optional explanation | accept encoding and claims boundary | changed optimum or unverifiable mapping |
| IBM preparation | layout/decoding checks, immutable intent/receipt and zero-retry controls | none | backend protocol and exact job authorization | failed preflight, stale evidence or ambiguous state |
| EXP-010D | 32-PUB packaging, retrieval, regeneration and CI repair | conservative explanation only | accept warning and merge | missing PUB, changed threshold or unsupported claim |
| EXP-011 | 88-PUB dense replication, frozen statistics and cross-run comparison | conservative explanation only | authorize job and approve interpretation | usage ceiling, malformed PUB, post-hoc change or retry |

Codex did not autonomously authorize hardware, choose the final scientific claim, remove warnings,
or merge results. GPT-5.6 did not calculate rho, p-values, ranks, energies, or hardware outcomes.

## Pre-existing and Build Week work

The public Foundations product and registered experiments pre-date Build Week at
`281ba4013112a071bba4a70579c24d051da36c51`. Work after governing-plan merge
`3950a1f4f6c7c3f65c613133dec6dd8075739f57` added deterministic orchestration, the Guided
Experiment, optional validated explanation, release evidence, the 256 Reveal, and the later
governed real-data/hardware programme. Pre-existing fixtures and registered values were preserved;
new hardware experiments were added as separately planned, reviewed, authorized evidence.

## Primary-session feedback

Codex Session ID supplied privately through the Devpost submission form.

The identifier is intentionally excluded from public repository evidence.
