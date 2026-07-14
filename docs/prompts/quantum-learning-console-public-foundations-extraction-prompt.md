# Quantum Folk Lab — Public Learning Console Foundations Extraction Prompt

## Purpose

Implement a **self-gated public extraction** of the Quantum Folk Lab Learning Console Foundations work.

The goal is to promote a safe, useful public edition from the current private implementation without exposing private/local material and without touching the main README yet.

This is a controlled public-release task, not a blanket move of `private/`.

---

# Repository context

Repository:

`C:\Users\gwrip\Documents\Machine_Learning\CymruFfowcGen\quantum-folk-lab`

Public repo:

`GwriPennar/quantum-folk-lab`

Current private source areas include:

- `private/learning_content/`
- `private/learning_core/`
- `private/learning_services/`
- `private/streamlit/`

The completed Foundations Hybrid Migration established:

- six portable Foundations content areas
- registry-driven navigation
- portable Markdown and HTML export
- semantic state markers
- progress compatibility
- 24 private learning tests passed
- 14 private Streamlit tests passed
- 45 public tests passed
- 18/18 Playwright captures
- zero semantic mismatches
- EXP-005A registered artefacts unchanged

---

# Objective

Create a public experimental **Learning Console Foundations** release that helps others learn from and extend the work.

Keep it separate from the main README for now.

Use these public areas:

- `learn/`
- `src/quantum_folk_lab/learning/`
- `apps/learning_console/`
- `dev/learning/`

The release should become part of the repository’s incremental experiment / learn / development structure.

Do not publish the whole private application.

---

# Self-gating rule

You must independently evaluate every release gate.

Do not create a ready-for-review PR unless every mandatory gate passes.

If any mandatory gate fails:

1. stop publication work
2. leave the public branch in a clearly documented draft state, or do not create the PR
3. report the exact failing gate
4. report the affected files
5. propose the smallest safe correction
6. do not waive the failure merely to complete the task

Use these gate states:

- `PASS`
- `FAIL`
- `NOT APPLICABLE`
- `NEEDS HUMAN DECISION`

Only `PASS` and justified `NOT APPLICABLE` are acceptable for automatic continuation.

A `NEEDS HUMAN DECISION` gate must stop the release before PR readiness.

---

# Critical boundaries

Do not:

- move or copy the entire `private/` directory
- publish `.guided_progress.json`
- publish progress backups
- publish screenshots, contact sheets, PDFs, browser profiles or Playwright logs
- publish absolute local paths
- publish PIDs, local usernames, machine-specific environment information or backup locations
- publish private prompts or operational transcripts
- publish secrets, tokens, credentials, email addresses or environment values
- publish private corpora, private tune data or client material
- duplicate registered scientific values in Markdown when they can be loaded from the registered artefact
- change or regenerate EXP-005A registered results
- imply quantum advantage
- imply real-corpus tune-family inference
- modify the main README
- merge PRs #10, #11 or #12
- stage, reset, stash, revert or overwrite the intentional local `.gitignore` modification
- publish anything still dependent on ignored private files
- stop or modify unrelated Streamlit processes
- commit generated PDFs, PNGs or evaluation artefacts

The public release must work from a clean clone without access to `private/`.

---

# Proposed public structure

Create or adapt:

```text
learn/
├── README.md
├── registry.yaml
├── glossary.yaml
├── lessons/
│   ├── bits-and-qubits.md
│   ├── gates-and-measurement.md
│   ├── hadamard-and-interference.md
│   ├── entanglement.md
│   └── optimisation-intro.md
├── diagrams/
│   └── source/
└── schemas/
    └── lesson.schema.json

src/quantum_folk_lab/learning/
├── __init__.py
├── models.py
├── registry.py
├── parser.py
├── directives.py
├── validation.py
├── glossary.py
├── semantic_state.py
└── export.py

apps/learning_console/
├── README.md
├── app.py
├── renderers/
├── components/
└── services/

dev/learning/
├── ARCHITECTURE.md
├── MERMAID-POLICY.md
├── CONTRIBUTING-LESSONS.md
├── PUBLIC-RELEASE-SCOPE.md
└── RELEASE-GATES.md
```

Adapt the exact layout only where repository conventions justify it.

---

# Initial public scope

Publish:

1. Bits and qubits
2. Gates and measurement
3. Hadamard and interference
4. Entanglement
5. What is an optimisation problem?
6. Guided glossary
7. portable lesson schema
8. portable registry format
9. parser and validation layer
10. restricted Mermaid/QFL diagram policy
11. static Markdown/HTML export support
12. semantic lesson-state contract
13. public-safe visual components
14. minimal Learning Console application
15. EXP-001 learning integration using existing public Qiskit functionality
16. read-only EXP-005A learning case study using the registered public result
17. contributor documentation
18. public-safe tests and fixtures

Do not publish yet:

- EXP-002 interactive graph lab
- full Researcher dashboard
- optimiser traces
- advanced matrix tooling
- local progress persistence
- screenshot-generation tools
- browser automation
- private evaluation tooling
- private review packs
- private architecture preview toggles
- local rollback/debug controls
- operational backup scripts

---

# Phase 0 — baseline

Before editing:

1. confirm repository root, branch and HEAD
2. report `git status --short --branch`
3. confirm `private/` remains ignored
4. confirm `.gitignore` remains modified and unstaged
5. confirm no review-pack binaries exist under the repository root
6. confirm registered EXP-005A artefacts are unchanged
7. run current private and public tests
8. create a timestamped local-only backup of all private learning architecture files
9. confirm PRs #10–#12 remain open and unmerged

If the baseline differs, stop.

---

# Phase 1 — produce an explicit promotion allowlist

Create a machine-readable allowlist under a local temporary working area, not under `private/`.

For every proposed public file record:

- private source path
- intended public destination
- file type
- purpose
- whether content was copied, adapted or newly written
- privacy review result
- licence/provenance review result
- public dependency review result
- scientific-claim review result

Do not use recursive copy commands over `private/`.

Every public file must be individually allowlisted.

Gate G1 passes only if every public file has an allowlist entry.

---

# Phase 2 — sanitised extraction

Create clean public versions.

For each extracted file:

- remove local paths
- remove private-only settings
- remove private progress logic
- remove architecture-preview controls
- remove backup/debug information
- replace private imports with public package imports
- ensure it does not reference `private/`
- ensure it works without local ignored files
- preserve scientific caveats
- preserve accessible text and semantic markers
- preserve source-backed registered-data loading

Do not modify the original private implementation during extraction unless a safe shared abstraction is clearly needed and fully tested.

Prefer copying reviewed concepts into clean public modules over moving files directly.

---

# Phase 3 — public learning content

Create the public `learn/` area.

`learn/README.md` should explain:

- what the Learning Console is
- its experimental status
- the hybrid architecture
- how lessons relate to experiments
- how to validate and export lessons
- how to run the Learning Console
- limitations
- no quantum-advantage claim
- no real-corpus claim
- contribution route

Do not add a link from the root README.

Lesson Markdown must remain readable outside Streamlit.

Glossary terms must have one canonical public source.

Mermaid/QFL diagrams must have deterministic, safe fallbacks.

---

# Phase 4 — public package extraction

Move reusable content infrastructure into:

`src/quantum_folk_lab/learning/`

Requirements:

- no Streamlit import in models, registry, parser, validation, glossary or export
- no private path assumptions
- no runtime access to `private/`
- no absolute path output
- no arbitrary code execution from Markdown
- no arbitrary HTML or JavaScript
- no unrestricted filesystem references
- unknown directives fail safely
- generated SVG is checked for script and external references

The public package should expose a small stable API, for example:

```python
from quantum_folk_lab.learning import (
    load_registry,
    load_lesson,
    validate_lesson,
    export_lesson,
)
```

Do not expose unnecessary internal implementation details.

---

# Phase 5 — minimal public Learning Console

Create a minimal public app under:

`apps/learning_console/`

It should support:

- Guided Foundations navigation
- the five reading lessons
- glossary
- EXP-001 learning integration
- EXP-005A read-only case study
- static diagrams and visual directives
- semantic lesson markers
- plain-language defaults
- optional technical disclosures

It must not include:

- private progress persistence
- private architecture preview
- private review tooling
- full Researcher dashboard
- EXP-002 interactive lab
- local-only operational controls

Use session-only progress if progress is included at all.

The app must have its own README and documented launch command.

Do not assume port 8503 in public documentation; allow the user to choose or use Streamlit’s default.

---

# Phase 6 — dependency and packaging review

Review project packaging.

Add only dependencies genuinely required for the public feature.

Prefer optional extras, for example:

```text
.[learn]
.[learn,quantum]
```

Do not force Streamlit or Mermaid tooling on users installing only the scientific package unless already justified.

Verify:

- base install still works
- development install still works
- quantum extra still works
- learning extra works
- clean environment install works

Gate G2 passes only if dependency changes are minimal and documented.

---

# Phase 7 — scientific integrity gate

Verify:

- EXP-001 uses genuine local Qiskit execution when quantum dependencies are installed
- missing Qiskit fails clearly rather than fabricating results
- EXP-005A loads registered public data read-only
- registered values match exactly
- exact enumeration remains authoritative
- exact, expectation and samples remain separate
- no quantum-advantage claim
- no production-readiness claim
- no real-corpus inference claim
- synthetic fixture limitations remain visible

Gate G3 must pass with automated tests.

---

# Phase 8 — privacy and public-safety gate

Run an expanded public safety scan over all proposed files.

Check for:

- `C:\Users\`
- `/Users/`
- local repository paths
- email addresses
- tokens
- API keys
- `.env`
- credentials
- private project names
- private corpus references
- private client references
- local PIDs and ports
- progress state
- screenshot/evaluation paths
- binary files
- hidden/generated browser data
- references to `private/`
- unintended personal data

Also manually inspect every proposed file.

Gate G4 passes only if both automated and manual review pass.

---

# Phase 9 — licence and provenance gate

For every public asset and content source confirm:

- original project-authored content or clearly compatible licence
- no copied proprietary diagram or text
- no unlicensed screenshot
- no third-party font or binary asset
- no private dataset content
- public experiment data has existing provenance
- generated SVG contains no embedded external material

Create a concise provenance table in:

`dev/learning/PUBLIC-RELEASE-SCOPE.md`

Gate G5 passes only if provenance is clear.

---

# Phase 10 — clean-clone test

Create a separate temporary clean clone outside the active working directory.

Do not use the ignored private files.

From that clone:

1. install base dependencies
2. install learning extras
3. run public tests
4. run public safety scan
5. validate all lessons
6. export all lessons to Markdown and HTML
7. start the public Learning Console
8. verify it responds
9. open every lesson route
10. exercise EXP-001 if quantum dependencies are installed
11. load EXP-005A case study
12. verify semantic markers
13. verify no private files are required

Gate G6 passes only if the clean clone succeeds independently.

---

# Phase 11 — tests

Add public tests for:

## Content

- schema validity
- unique IDs and routes
- glossary references
- directive registration
- no private paths
- no secrets
- no invalid claims

## Parser and registry

- deterministic order
- route lookup
- next-lesson resolution
- malformed front matter
- unsupported directive handling
- safe file resolution

## Export

- Markdown export
- HTML export
- diagram fallback
- interaction explanation
- heading parity
- scientific caveats

## EXP-001

- catalogue
- theoretical expectation
- missing-Qiskit behaviour
- genuine execution path where available

## EXP-005A

- registered JSON integrity
- exact optima
- expected values
- sampled probabilities
- complement probability
- limitations

## Streamlit

- app startup
- lesson navigation
- semantic markers
- Guided-only boundaries
- no private controls
- no private path rendered

All public tests must pass.

---

# Phase 12 — documentation

Create:

`dev/learning/ARCHITECTURE.md`

Explain:

- content/runtime split
- portable Markdown
- registry
- directives
- Streamlit renderer
- static export
- scientific services
- future migration path

Create:

`dev/learning/CONTRIBUTING-LESSONS.md`

Explain:

- adding a lesson
- front matter
- glossary terms
- supported diagram syntax
- directives
- validation
- scientific-claim requirements
- accessibility
- testing

Create:

`dev/learning/RELEASE-GATES.md`

Document the release gates and how to rerun them.

Keep the root README unchanged.

---

# Phase 13 — branch and PR

Only after gates G1–G6 and all tests pass:

1. create a new public feature branch
2. stage only explicitly allowlisted public files
3. verify no `private/` file is staged
4. verify `.gitignore` remains unstaged
5. commit the public extraction
6. push the branch
7. create a draft PR

Suggested branch:

`feat/public-learning-console-foundations`

Suggested PR title:

`feat: add experimental Learning Console Foundations`

The PR body must include:

- purpose
- experimental status
- public scope
- excluded private scope
- directory structure
- running instructions
- testing
- security/privacy review
- scientific limitations
- clean-clone result
- release-gate table
- follow-up roadmap

Do not modify the root README.

Keep the PR draft initially.

---

# Automated release gate table

Before creating the PR, produce:

```text
G1 File allowlist                     PASS/FAIL
G2 Dependencies and packaging        PASS/FAIL
G3 Scientific integrity              PASS/FAIL
G4 Privacy and public safety         PASS/FAIL
G5 Licence and provenance            PASS/FAIL
G6 Clean-clone independence          PASS/FAIL
G7 Public test suite                 PASS/FAIL
G8 Public app smoke test             PASS/FAIL
G9 No private files staged           PASS/FAIL
G10 Root README unchanged            PASS/FAIL
```

All ten must be `PASS`.

If any gate fails, do not create or update the PR as ready for review.

---

# Final report

Report:

- release decision: `PROCEED` or `STOPPED`
- gate table G1–G10
- branch name
- commit SHA
- PR number and draft status, if created
- public files created
- private source files reviewed
- files excluded and why
- dependencies added
- public test results
- safety scan result
- licence/provenance result
- clean-clone result
- public app smoke result
- EXP-001 verification
- EXP-005A integrity verification
- root README unchanged confirmation
- final active-checkout git status
- confirmation `.gitignore` remains modified and unstaged
- confirmation `private/` remains ignored and unpublished
- confirmation no binary review artefacts were committed
- known limitations
- recommended next public LEARN/DEV increment

Self-gate strictly.

Speed is useful, but public-release safety takes priority over finishing the PR.
