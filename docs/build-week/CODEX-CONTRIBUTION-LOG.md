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

`PENDING USER ACTION — invoke /feedback in the primary Codex session and add the returned session ID during release review.`

Do not replace this placeholder with an invented identifier.
