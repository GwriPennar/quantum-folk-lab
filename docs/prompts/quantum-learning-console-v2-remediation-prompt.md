# Quantum Folk Lab Learning Console — Review Pack v2 Remediation Prompt

## Purpose

Implement a focused second-pass improvement of the private Streamlit **Quantum Folk Lab Learning Console** after Review Pack v2.

The existing dual-mode architecture is the baseline and must be preserved:

1. **Guided Learner** — beginner-first, visual, plain-language, progressive disclosure.
2. **Researcher** — full technical depth, experiment detail, provenance and governance.

This is not a redesign from scratch. It is a remediation and quality pass that fixes the most important defects, replaces placeholder teaching states with real visual components, improves interaction quality and strengthens regression coverage.

The private application remains local and gitignored. This public Markdown file is only the implementation specification.

---

# Governing principles

## Preserve the dual-experience contract

Guided Learner and Researcher are different experiences over the same project, not two unrelated applications.

Guided Learner must:

- lead with visual explanation
- use plain language before equations
- offer one clear next action
- hide seeds, matrices, raw JSON and optimiser detail by default
- explain uncertainty and sampling honestly
- never imply quantum advantage
- retain optional access to deeper material

Researcher must:

- preserve all prior dashboard capability
- expose exact, expected and sampled metrics
- expose QUBO and Ising data
- expose circuit, backend, seed, shots and optimiser metadata
- preserve provenance, registered artefacts, CLI, Git and governance material
- never be simplified merely to match Guided Learner

## Scientific integrity

Do not change, regenerate, retune or reinterpret registered EXP-005A results.

Exact brute-force enumeration remains authoritative.

Do not claim:

- quantum advantage
- superiority over the exact classical baseline
- real-corpus tune-family inference
- production readiness
- broader generalisation than the registered synthetic fixture supports

## Local/private boundary

The implementation is under the ignored `private/` tree.

Do not:

- stage or publish anything under `private/`
- remove or overwrite the intentional local `.gitignore` entry for `private/`
- stage, reset, stash or revert the local `.gitignore` modification
- merge or modify unrelated documentation pull requests
- create another clone or worktree
- expose local absolute paths, secrets or environment values
- stop or modify services on ports 8501 or 8502
- change public experiment code or registered result artefacts as part of this UI pass

Use port 8503 for the private Streamlit app.

---

# Baseline status

The current private app already includes:

- a sidebar Experience selector
- Guided Learner as the default mode
- an 11-lesson guided pathway
- mode-aware Home, Learn, Labs and Reference routing
- Guided EXP-001 and EXP-002 flows
- a completed EXP-005A case study
- a read-only loader for the registered EXP-005A JSON
- Researcher Home, Learn, Labs and Reference views
- private dual-mode tests
- Review Pack v2 screenshot automation and PDF generation

Do not discard these foundations.

---

# Review Pack v2 findings to address

## P1 — Researcher Advanced depth binding

The current Researcher UI presents `Simple`, `Intermediate` and `Advanced`, but some lab logic still depends on legacy `Full detail` behaviour.

This can leave technical content hidden even when the user selects Advanced.

### Required outcome

Selecting **Advanced** in Researcher mode must consistently make the full technical layer available.

Advanced must reveal, where applicable:

- exact metrics
- expected metrics
- sampled metrics
- exact-state or assignment tables
- QUBO matrix
- Ising coefficients or matrix representation
- Hamiltonian/operator information
- circuit width, depth and operation counts
- transpilation or backend metadata
- seeds
- shots
- optimiser parameters
- optimiser history
- execution classification
- provenance and registered artefact information

The interface may still use expanders to control page length, but Advanced must not silently suppress technical content because of a stale string comparison.

### Implementation guidance

Create one canonical depth model, for example:

```python
from enum import StrEnum

class DetailLevel(StrEnum):
    SIMPLE = "Simple"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


def is_technical(level: str) -> bool:
    return level == DetailLevel.ADVANCED
```

Adapt this to the existing project style. Do not duplicate competing detail-level checks across views.

### Tests

Add tests proving:

- Guided Learner does not expose technical-only content by default
- Researcher Simple hides Advanced-only content
- Researcher Intermediate exposes intermediate explanations without full raw detail
- Researcher Advanced exposes all expected technical sections
- no legacy `Full detail` branch remains active unless it is deliberately retained as a backward-compatible alias

---

# Guided visual component pass

The principal remaining weakness is that several Guided lessons are still text-first or reuse a general lesson page for distinct concepts.

Build reusable visual components rather than adding more prose.

## Shared component contract

Each visual should support this teaching sequence:

1. **Before**
2. **Operation or change**
3. **After**
4. **What measurement can reveal**
5. **Optional maths**

Each component must:

- work without animation as a static fallback
- use text labels as well as colour
- avoid relying solely on red/green distinctions
- render sensibly at desktop and narrow widths
- avoid scientific overstatement
- include an accessible caption or explanation
- be deterministic for screenshots and tests

Prefer native Streamlit, HTML/CSS, SVG, Plotly or Matplotlib components already compatible with the project. Avoid introducing a large front-end framework.

## 1. Bit versus qubit

Create a clear visual contrast:

- classical bit: one definite state, 0 or 1
- qubit before measurement: a quantum state that can produce different measurement outcomes

Do not describe a qubit as simply “both 0 and 1 at the same time” without qualification.

Suggested visual:

- left: a two-position switch for a bit
- right: a probability/amplitude dial or state sphere-style diagram for a qubit
- final panel: measurement returns a classical 0 or 1

## 2. X gate

Show:

```text
|0⟩ → X → |1⟩
|1⟩ → X → |0⟩
```

Use a before/after state card and a compact circuit thumbnail.

The learner should be able to toggle the input state and observe the output state.

## 3. Hadamard probability split

Show:

```text
|0⟩ → H → equal measurement probabilities for 0 and 1
```

Explain that equal probabilities do not by themselves show the phase information carried by the state.

Include:

- one-path-to-two-outcomes visual
- 50/50 theoretical bars
- optional sampled bars after repeated measurement
- a clear label distinguishing theory from samples

## 4. Z phase reveal sequence

Create a dedicated phase visual. Do not merely reuse the general superposition lesson screenshot.

Show a sequence such as:

```text
|0⟩ → H → Z → H → measurement
```

Explain that Z changes relative phase, not the immediate 50/50 measurement probabilities in the computational basis after the first H.

The second H converts the phase difference into a measurable outcome difference.

The visual should show:

- state/path split
- phase sign change
- recombination
- final outcome

## 5. Double-H interference

Create a dedicated `H → H` sequence:

```text
|0⟩ → H → H → |0⟩
```

Use wave/path reinforcement and cancellation language carefully.

The learner should see that the second H is not simply “another random split”; amplitudes interfere.

## 6. Bell-state correlation

Create a dedicated Bell-pair visual before EXP-001 asks the learner to run the circuit.

Show:

```text
|00⟩ → H on q0 → CNOT(q0, q1) → Bell state
```

Then show repeated measurement outcomes:

- `00`
- `11`

Explain:

- each individual outcome is uncertain
- the two results are correlated
- this does not transmit a usable message faster than light

Do not use a visual that implies one qubit sends an ordinary hidden signal to the other.

## 7. Circuit thumbnails

Create a reusable circuit-thumbnail component for Guided lessons and EXP-001.

It must support at least:

- identity/measurement
- X
- H
- H-H
- H-Z-H
- Bell-state H+CNOT

The thumbnail should appear before the learner is asked to predict an outcome.

---

# EXP-001 remediation

Preserve the established flow:

```text
See circuit → Predict → Run → Explain → Next circuit
```

## Required changes

### Circuit first

Before the prediction form, show:

- circuit thumbnail
- one-sentence plain-language description
- what the learner is being asked to predict

The learner should never be asked to predict an unseen circuit.

### Prediction feedback

Use supportive, specific feedback.

For an incorrect prediction:

- acknowledge the reasoning attempt
- explain the relevant gate behaviour
- distinguish theoretical expectation from sampled variation
- avoid punitive red-error styling

### Theory versus samples

Make the distinction persistent and explicit:

- **Theory** — what ideal quantum mechanics predicts
- **Samples** — what was observed over a finite number of shots

Do not imply that a finite sampled histogram is the exact state.

### Shots explanation

Keep the repeated-trials analogy, but add the limitation:

- more shots reduce random sampling noise
- more shots do not remove model, device or implementation error

### Next-circuit logic

Recommend the next incomplete circuit, not merely the next fixed item.

Avoid marking a lesson complete solely because the page was opened. Completion should correspond to a meaningful action such as making a prediction and viewing the result.

### Researcher preservation

Researcher EXP-001 must retain:

- seed controls
- shots controls
- circuit metadata
- backend/execution details
- raw or detailed result access
- full notation and caveats

---

# EXP-002 interactive Max-Cut pass

The current Guided Step 1 uses a bitstring/select control. Replace or supplement this with a genuinely visual node-colouring interaction.

## Step 1 — Colour the graph

Allow the learner to click or otherwise directly toggle graph nodes between two groups.

Update live:

- node group/colour
- crossing edges
- non-crossing edges
- current cut score
- best score seen by the learner in the session
- exact optimum score, but only after an appropriate reveal or comparison action

Every colour distinction must also have a label, outline, pattern or group marker.

If direct click handling is not reliable in the current Streamlit stack, implement the best robust equivalent, such as one toggle per node beside a live graph. Do not fake click interaction in screenshots.

## Good cut versus bad cut

Add a dedicated side-by-side visual:

- poor partition with few crossing edges
- better partition with more crossing edges

Label crossing edges clearly.

Do not rely on a small text table as the primary explanation.

## Step 2 — Classical exhaustive answer

Explain that, for this deliberately small graph, the classical program can check every assignment.

Show:

- number of assignments checked
- best score
- exact optimal assignments
- why exact enumeration is the authority for this teaching example

Keep the full assignment table behind optional disclosure in Guided mode and fully accessible in Researcher mode.

## Step 3 — Meet QAOA

Create a dedicated QAOA loop diagram:

```text
choose parameters
→ prepare quantum state
→ run circuit / estimate objective
→ classical optimiser updates parameters
→ repeat
```

Clarify that QAOA is a hybrid quantum-classical procedure.

Do not describe the classical optimiser as an incidental detail.

## Step 4 — Compare answers

Use a persistent three-part legend across the full EXP-002 story:

- **Exact answer**
- **Quantum expectation**
- **Measured samples**

Show a plain-language comparison such as:

```text
Your cut: 3 crossing edges
Exact best cut: 4 crossing edges
Most common sampled cut: 4 crossing edges
```

Where energy is displayed, connect it carefully to the cut objective and preserve the exact sign convention used by the implementation.

## Researcher preservation

Researcher EXP-002 must retain:

- exact assignment table
- exact optimum data
- expected objective/energy data
- sampled histogram and probabilities
- QUBO and Ising representations
- optimiser trace/history
- circuit and backend metadata
- seeds and shots
- scientific interpretation and limitations

---

# EXP-005A storytelling pass

Do not change the registered values.

The Guided case study should tell a four-part story.

## Part 1 — The problem

Explain that the fixture contains eight synthetic tunes constructed as two families.

Use a simple visual arrangement of eight labelled tune cards or nodes.

Do not imply that the synthetic fixture represents the full complexity of Welsh folk music.

## Part 2 — The exact answer

Show the two exact optima prominently:

```text
00001111
11110000
```

Explain complement symmetry:

- flipping every bit changes the labels of the two groups
- it does not change the underlying partition
- the two bitstrings therefore represent the same family split up to group naming

Use a two-column partition visual rather than presenting only binary strings.

## Part 3 — What QAOA sampled

Show one clear visual for the registered optimum complement-class probability:

```text
0.531005859375
```

Also show the two optimum-state probabilities when the learner opens more detail:

- `P(00001111) = 0.259521484375`
- `P(11110000) = 0.271484375`

Explain that these sum to the complement-class probability.

Show balanced-sample probability separately and explain what it measures:

```text
0.7119140625
```

Do not visually conflate “balanced sample” with “exact optimum”.

## Part 4 — What this does not prove

Place the limitations beside the result, not only at the bottom of a long page.

State clearly:

- exact brute-force enumeration is authoritative
- the execution was genuine local Qiskit p=1
- the experiment does not demonstrate quantum advantage
- the fixture is synthetic
- the result does not establish tune-family inference on a real corpus

## Registered values

The UI and tests must preserve these values exactly:

- fixture: `synthetic-two-family-v1-seed42`
- tune count: `8`
- `tau = 0.25`
- `lambda = 0.1`
- threshold: `0.05`
- exact optima: `00001111`, `11110000`
- assignments checked: `256`
- direct/QUBO maximum disagreement: `5.329070518200751e-15`
- QUBO/Ising maximum disagreement: `2.4868995751603507e-14`
- shots: `4096`
- expected energy: `5.2872120969`
- expected gap: `5.2872120969`
- `P(00001111) = 0.259521484375`
- `P(11110000) = 0.271484375`
- optimum complement-class probability: `0.531005859375`
- balanced-sample probability: `0.7119140625`

Load them read-only from the registered local result artefact.

Do not duplicate these values as an independently maintained second source of truth where avoidable.

---

# Guided Home refinement

Reduce competing calls to action.

## Primary state

Show one dominant action:

```text
Continue: <next lesson title>
About <estimated time>
```

For a first-time user:

```text
Start lesson 1: Bits and qubits
```

## Secondary state

Below the main action, show only:

- pathway progress
- most recently completed lesson
- one upcoming lesson

Move the full pathway into a collapsed or secondary section.

## Status language

Use consistent states:

- Not started
- In progress
- Completed
- Optional case study

Avoid showing a lesson as complete simply because it was selected.

## Mode explanation

Near the Experience selector, explain:

```text
Guided Learner
Concepts, predictions and step-by-step experiments

Researcher
Full metrics, matrices, metadata and provenance
```

Keep this compact.

---

# Visual identity of each mode

The modes should feel deliberately different while remaining one application.

## Guided Learner

Prefer:

- larger visual components
- shorter line lengths
- fewer controls at once
- one primary action per section
- plain-language labels
- supportive feedback
- progress and next-step cues

## Researcher

Prefer:

- compact metric cards
- comparison tables
- technical tabs
- dense but ordered metadata
- provenance panels
- copy/export controls where safe and useful
- explicit source and execution classification

Do not use decorative styling that reduces legibility or scientific seriousness.

---

# Progress persistence

Add optional local-only persistence for Guided progress.

## Requirements

Store only learning-state information, such as:

- current lesson
- completed lessons
- last meaningful Guided action
- optional learner preferences

Do not treat saved UI state as a scientific artefact.

Do not overwrite registered experiment results.

The persistence file must remain under the ignored private area.

Provide:

- graceful handling when no progress file exists
- schema/version field
- atomic write where practical
- reset progress control
- fallback to session-only behaviour if persistence fails
- no absolute path shown in the UI

Make persistence optional and easy to disable for automated screenshots.

---

# Responsive and accessibility pass

## Narrow layouts

At narrow widths:

- stack action buttons vertically
- avoid wide rows of metric cards
- avoid horizontal controls that require sideways scrolling
- preserve graph legibility
- enlarge tap targets
- keep the main action discoverable
- ensure expanders and select controls fit the viewport

## Colour and labels

Every chart or graph that uses colour must also use at least one of:

- direct labels
- marker shape
- pattern
- edge style
- textual legend

## Keyboard and semantics

Use standard Streamlit controls where possible.

For custom HTML/SVG:

- add meaningful text alternatives
- preserve logical reading order
- avoid click-only controls without a keyboard-equivalent fallback

## Motion

Any animation must have a static fallback and should respect reduced-motion preferences where practical.

---

# Screenshot and regression automation

Review Pack v2 captured all requested inventory positions, but several were substituted because dedicated states did not yet exist.

Strengthen the automation before producing Review Pack v3.

## Capture validation

For every screenshot, record and validate:

- experience mode
- page
- lesson or experiment
- selected detail level
- expected heading
- required visible text
- expected open expander or tab
- viewport size
- absence of errors and overlays
- image dimensions
- perceptual hash

## Duplicate detection

Add perceptual or structural duplicate checks so that near-identical screenshots for different requested concepts are flagged.

Use statuses such as:

- `ok`
- `substituted`
- `missing`
- `duplicate`
- `failed`

A screenshot must not be labelled `ok` merely because a file was created.

## Error rejection

Reject screenshots containing:

- traceback
- connection error
- `ModuleNotFoundError`
- Streamlit exception panel
- stale page heading
- wrong mode
- wrong selected lesson
- open menu or overlay
- absolute local path
- partially rendered page

## Deterministic state

Provide a safe screenshot mode that can:

- disable persistent progress
- initialise known session state
- use stable seeds
- wait for expected UI markers
- avoid editing registered scientific data

---

# Review Pack v3

After implementation and validation, create a local-only Review Pack v3.

## Presentation improvements

Compared with v2:

- crop screenshots to useful application content
- use landscape pages for wide desktop captures
- enlarge screenshot text
- place before/after states side by side
- annotate key improvements with restrained callouts
- reduce blank page space
- separate the main review from the raw screenshot appendix
- include a one-page v2-to-v3 change summary

## Required evidence

Include at minimum:

### Guided Learner

- refined first-visit Home
- refined continue state
- bit versus qubit visual
- X-gate interactive visual
- Hadamard split
- Z-phase sequence
- double-H interference
- Bell correlation visual
- EXP-001 circuit-before-prediction
- EXP-001 theory versus samples
- interactive Max-Cut node grouping
- good versus bad cut visual
- QAOA loop
- EXP-002 three-way comparison
- EXP-005A partition/complement visual
- EXP-005A probability visual
- limitations beside result
- narrow/mobile versions

### Researcher

- Simple, Intermediate and Advanced comparison
- Advanced EXP-001 metadata
- Advanced EXP-002 matrices and optimiser information
- EXP-005A registered values and provenance
- CLI, Git and governance
- evidence that Advanced binding is fixed

## Honest status

Do not fabricate missing features.

If an intended feature remains incomplete, label it clearly and include it in the findings table.

---

# Testing requirements

Expand the private test suite beyond the existing dual-mode smoke tests.

## Unit and content tests

Test:

- default experience is Guided Learner
- mode switching persists within session
- detail-level mapping is canonical
- Advanced enables technical content
- Guided hides technical content by default
- all Guided lessons have a visual component or an explicitly declared fallback
- EXP-001 circuit thumbnail appears before prediction
- EXP-002 legend labels are present
- EXP-005A registered values exactly match the source JSON
- complement probabilities sum correctly within strict tolerance
- progress persistence schema and reset behaviour
- no absolute local paths are rendered

## Integration/smoke tests

Test:

- app starts on port 8503
- Home, Learn, Labs and Reference load in both modes
- no traceback appears
- EXP-001 can complete one prediction/run flow
- EXP-002 Guided steps can be traversed
- Researcher Advanced exposes technical sections
- EXP-005A loads from the local registered result artefact

## Regression boundary tests

Confirm:

- no files under `private/` are tracked
- registered public result JSON is unchanged
- public package tests remain green
- ports 8501 and 8502 are untouched

---

# Implementation sequence

Use small, testable phases.

## Phase 0 — safety and baseline

- confirm repository root and branch
- confirm local `main` is aligned with `origin/main`
- confirm `.gitignore` is modified and unstaged as expected
- confirm `private/` is ignored
- create a timestamped local-only backup of the active private Streamlit app
- run existing private and relevant public tests
- confirm port 8503 status

Stop and report if the safety boundary differs from expectations.

## Phase 1 — correctness

- replace legacy depth binding with canonical Simple/Intermediate/Advanced logic
- fix Researcher Advanced content visibility
- add regression tests

Keep the app runnable before proceeding.

## Phase 2 — reusable visuals

- circuit thumbnail component
- bit/qubit visual
- X gate
- Hadamard
- Z phase
- double H
- Bell correlation

Keep components reusable and deterministic.

## Phase 3 — EXP-001 integration

- show circuit before prediction
- improve feedback
- clarify theory versus samples
- improve next-circuit logic

## Phase 4 — EXP-002 interaction

- visual node grouping
- good/bad cut visual
- QAOA loop
- persistent three-way legend
- improved comparison summary

## Phase 5 — EXP-005A story

- problem visual
- complement partition visual
- probability visual
- limitations placement
- full Researcher provenance preserved

## Phase 6 — Home, persistence and responsive pass

- simplify Guided Home
- add optional local progress persistence
- improve narrow layouts
- accessibility checks

## Phase 7 — automation and Review Pack v3

- strengthen screenshot assertions
- add duplicate detection
- capture full inventory
- generate and validate Review Pack v3

Do not proceed to a later phase while an earlier phase has failing tests or a broken app.

---

# Completion criteria

The remediation is complete only when all of the following are true:

1. Researcher Advanced reliably exposes full technical content.
2. Z-phase, double-H and Bell correlation have distinct visual components.
3. EXP-001 shows the circuit before prediction.
4. EXP-002 offers a visual graph-grouping interaction or a robust direct equivalent.
5. The exact/expectation/sampled distinction is persistent and clear.
6. EXP-005A complement symmetry is visually explained.
7. Registered EXP-005A values remain unchanged and source-backed.
8. Guided Home has one dominant next action.
9. Narrow layouts are usable.
10. Progress persistence is optional, local and safe.
11. Screenshot automation detects stale, duplicate and substituted states.
12. All private tests pass.
13. Relevant public tests pass.
14. Nothing under `private/` is staged or published.
15. The local `.gitignore` boundary remains intact.
16. Review Pack v3 is generated with honest completion status.

---

# Final implementation report

At completion, report:

- phases completed
- files created and modified under the private app
- backup location
- tests run and results
- app status on port 8503
- Researcher Advanced binding result
- new Guided visual components
- EXP-001 changes
- EXP-002 interaction changes
- EXP-005A presentation changes
- persistence behaviour
- responsive/accessibility changes
- screenshot counts and statuses
- Review Pack v3 path, size and page count
- known remaining gaps
- `git status --short --branch`
- confirmation that no private file was staged or published
- confirmation that registered EXP-005A artefacts were unchanged

Do not report a feature as complete unless it was implemented, exercised and tested.
