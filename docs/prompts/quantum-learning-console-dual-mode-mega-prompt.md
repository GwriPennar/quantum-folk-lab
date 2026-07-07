# Quantum Folk Lab Learning Console — Dual-Mode Improvement Mega Prompt

Use this prompt in Cursor to improve the existing private Streamlit Quantum Folk Lab Learning Console.

---

Improve the existing private Streamlit Quantum Folk Lab Learning Console into a dual-experience application:

1. Guided Learner mode for someone new to quantum computing.
2. Researcher mode preserving and extending the current technical console.

This is an implementation task, not another review-only task.

## Core objective

The current application is technically accurate and useful as a research companion, but it is too dense and text-led for a beginner.

Do not remove the existing researcher experience.

Instead:

- preserve the current technical content and controls under Researcher mode;
- add a visual, structured and less intimidating Guided Learner mode;
- share the same experiment code and registered results between both modes;
- improve navigation, visual explanations, next-step guidance and accessibility;
- update the app to reflect that EXP-005A is now implemented, reviewed and merged.

The intended owner is new to quantum computing but also wants access to the complete research detail.

## Safety and repository boundaries

The Streamlit app is private and currently excluded from the public repository.

Do not:

- stage or commit anything under `private/` to the public Git repository;
- alter the public repository `.gitignore`;
- publish the private Streamlit app;
- expose local filesystem paths;
- expose environment variables, credentials, tokens or private data;
- modify registered scientific results;
- retune or rerun EXP-005A merely to improve its outcome;
- change public `quantum_folk_lab` package APIs unless strictly necessary;
- add IBM Runtime, cloud QPU or hardware execution;
- modify the public experiment history or provenance;
- stop other Streamlit instances or use ports 8501 or 8502.

Continue using the existing local Streamlit port, currently expected to be 8503.

Before editing:

1. Inspect the current private app structure.
2. Record the files that will be changed.
3. Create a timestamped local-only backup of the private Streamlit application outside the public repository root.
4. Exclude caches, virtual environments, secrets and generated results from the backup.
5. Confirm no private file is staged in Git.

## Implementation approach

Implement the work in coherent phases.

Do not perform a destructive rewrite.

Reuse existing components, themes, plots, Qiskit adapters, experiment runners and session-state behaviour where possible.

Keep the live app runnable after each phase.

Create reusable UI components rather than duplicating large HTML or CSS strings across pages.

## Phase 1: Global dual-experience structure

Add a clearly visible sidebar selector:

`Experience`

Options:

- `Guided Learner`
- `Researcher`

Use `st.session_state` to remember the selection during the browser session.

Use a single configuration constant for the default:

```python
DEFAULT_EXPERIENCE = "Guided Learner"
```

Make it easy to change later.

### Guided Learner mode

Guided Learner mode should:

- show one recommended next action;
- use plain language before technical terminology;
- use visuals before equations;
- hide developer and governance detail by default;
- hide seeds, raw JSON, matrices, module paths and CLI instructions;
- collapse research roadmap and Git metadata;
- use progressive disclosure:
  - `What this means`
  - `Show the maths`
  - `Show circuit details`
  - `Open Researcher view`
- never permanently lock technical content.

### Researcher mode

Researcher mode should preserve the current capabilities:

- Home project status and roadmap;
- Learn topics;
- Simple / Intermediate / Advanced technical depth;
- full Labs controls;
- exact, expected and sampled metrics;
- raw matrices;
- QUBO and Ising detail;
- circuit and transpiler metadata;
- seeds;
- optimiser data;
- JSON and provenance;
- Git and PR material;
- CLI and test references;
- research decisions;
- EXP-005A governance and results.

Do not simplify away researcher content.

Where current code is reused by both modes, use shared rendering functions with mode-aware options.

## Phase 2: Guided Home redesign

Redesign Guided Learner Home around one clear entry point.

At the top, add a large visual hero card:

Title:

`New to quantum computing? Start here.`

Text:

`Learn what a qubit is, make a prediction, and run your first circuit.`

Primary action:

`Start lesson 1: Bits and qubits`

The action must open the beginner Quantum foundations lesson directly.

Below it, show:

1. `Continue learning`
2. current guided progress
3. the next recommended lesson
4. a small map of the overall journey

Suggested journey:

```text
Bits and qubits
    ↓
Gates and measurement
    ↓
Superposition and interference
    ↓
Entanglement
    ↓
Optimisation
    ↓
Max-Cut
    ↓
QUBO and Ising
    ↓
QAOA
    ↓
Quantum Folk case study
```

Move these into collapsed secondary sections in Guided mode:

- project status;
- research roadmap;
- PR and governance notes;
- branch and commit metadata;
- document links;
- CLI information.

Move branch and commit information into:

`Developer information`

Do not show local filesystem paths.

### Researcher Home

Retain the existing researcher dashboard, but improve scanability.

Use tabs or grouped sections:

- `Research status`
- `Experiments`
- `Decisions and governance`
- `Documents`

Update all EXP-005A status text from “planned” or “not implemented” to the actual completed state.

## Phase 3: Guided navigation and learning path

Replace the nine equal-weight beginner topic choices with grouped navigation.

Use:

### Foundations

1. Bits and qubits
2. Gates and measurement
3. Superposition and interference
4. Entanglement

### Optimisation

5. What is an optimisation problem?
6. Max-Cut
7. QUBO and Ising
8. QAOA

### Research case studies

9. EXP-002 Max-Cut
10. EXP-005A Quantum Folk case study
11. Bit ordering

Git and development workflow should not appear as the first Guided Learner topic.

Move Git, PRs, CLI and tests into the Researcher and Developer reference areas.

For desktop:

- use a vertical stepper or grouped navigation;
- indicate completed, current and upcoming lessons.

For narrow screens:

- use a dropdown or accordion;
- do not allow a nine-item horizontal radio strip to wrap over multiple lines.

Add a breadcrumb or progress header:

```text
Guided Learner › Foundations › Bits and qubits
```

Add a clear footer to every lesson:

- what the learner just learned;
- one short check-for-understanding question;
- the recommended next step;
- a primary `Continue` button;
- an optional `Open Researcher detail` link.

## Phase 4: Unified explanation levels

Avoid having unrelated systems called Simple and Guided.

Use the global experience mode as the primary distinction.

Within Guided Learner mode, provide optional controls:

- `Show a little more detail`
- `Show the maths`
- `Show the code`

Within Researcher mode, retain:

- Simple
- Intermediate
- Advanced

The Guided Learner experience must not unexpectedly switch into equations, raw code or matrices.

## Phase 5: Reusable visual learning components

Create a small private component library, using the existing design language where possible.

Suggested components:

- `ExperienceSelector`
- `LearningHero`
- `LessonStepper`
- `LessonBreadcrumb`
- `ConceptCard`
- `BeforeAfterState`
- `ProbabilityBars`
- `CircuitThumbnail`
- `MetricLegend`
- `StepPipeline`
- `NextStepCard`
- `GlossaryTooltip`
- `ResearchDetailExpander`
- `QAOALoopDiagram`
- `BitOrderingDiagram`
- `MaxCutComparison`
- `ExperimentStatusCard`

Use consistent semantic styling:

- violet: quantum concepts and theory;
- green: exact classical ground truth;
- cyan: measured samples and shots;
- amber: caution, uncertainty or misconceptions;
- grey: planned, historical or supporting detail.

Do not rely on colour alone.

Include icons, labels and text for accessibility.

## Phase 6: Visual-first quantum foundations

Each Guided lesson should follow this order:

1. Picture or interactive visual
2. Plain-language explanation
3. Small interaction or prediction
4. What changed?
5. Optional mathematics
6. Optional code
7. Next step

### Classical bit versus qubit

Add a side-by-side visual:

- classical bit:
  definite 0 or 1;
- qubit:
  amplitudes and resulting measurement probabilities.

Avoid implying that a qubit is simply “both values at once”.

Use accurate language:

`Before measurement, the qubit is described by amplitudes. Measurement produces a classical result.`

### X gate

Show:

```text
Before: |0⟩
Apply X
After: |1⟩
```

Include simple before/after probability bars.

### Hadamard gate

Show before running:

- one probability bar at 0;
- H gate;
- equal probability bars for 0 and 1.

Explain:

`H changes a definite state into a balanced superposition.`

### Z gate and phase

Do not explain phase only as a hidden sign in text.

Add a visual sequence:

```text
Balanced superposition
    ↓
Z changes relative phase
    ↓
Probabilities initially look unchanged
    ↓
A later H reveals the phase through interference
```

### Double Hadamard

Add an interference animation or stepped diagram showing amplitudes recombining.

### Bell state

Before the result heatmap, show a correlation visual:

- `00` and `11` highlighted;
- `01` and `10` crossed out or dimmed;
- plain-language description:
  `The two results are individually uncertain but strongly correlated.`

### Circuit thumbnails

Add a small circuit image to every EXP-001 lesson before the user enters the Lab.

Use existing Qiskit circuit drawing where safe, or lightweight SVG/HTML.

Avoid heavy new dependencies.

## Phase 7: EXP-001 Guided Lab improvements

Preserve the existing:

`Predict → Run → Explain`

flow.

Improve it into:

```text
1. See the circuit
2. Make a prediction
3. Run the simulator
4. Explain what happened
5. Try the next circuit
```

Add a visible pipeline with progress checkmarks.

In Guided Learner mode:

- hide seed fields under `Advanced run settings`;
- hide the notation line until requested;
- explain shots using a repeated coin-toss analogy;
- default to the next incomplete recommended circuit;
- show a `Suggested next` chip;
- show before/after state visuals;
- show theoretical and sampled probabilities clearly;
- replace unexplained `pass` and `caution` language with:
  - `Matches the expected pattern`
  - `Looks noisy, which can happen with finite samples`
- keep the technical validation badge inside Researcher detail.

After completion, add:

`Next circuit: Hadamard`

or the appropriate next recommended circuit.

When a prediction is wrong, treat it as a teaching opportunity:

`That prediction was reasonable. Compare it with what the gate actually changed.`

Do not frame it as failure.

## Phase 8: Visual optimisation pathway

### Optimisation primer

Add a visual explanation of:

- choices;
- objective score;
- constraints;
- trying all solutions on a small problem.

Use a simple non-quantum example first.

### Max-Cut visual primer

Add a side-by-side four-node graph:

- poor partition;
- good partition.

Show the number of cut edges directly on each diagram.

Add an optional toy interaction:

- click a node to switch sides;
- update the cut score immediately;
- no Qiskit required.

### QUBO and Ising

In Guided mode, combine them into one lesson:

`The same optimisation problem written in two different languages.`

Show:

```text
Binary choices: 0 and 1
        ↓
QUBO score
        ↓
Convert variables
        ↓
Ising spins: -1 and +1
```

Do not start with matrices or Hamiltonian sums.

Put matrices and exact algebra under:

- `Show the maths`
- Researcher mode

### Bit ordering

Create an explicit diagram aligning:

- node index;
- qubit index;
- classical bit;
- displayed bitstring position.

Use a four-bit interactive example.

Make it clear which end of a displayed string corresponds to qubit 0.

Do not rely on prose alone.

## Phase 9: QAOA visual explanation

Create a reusable QAOA loop diagram used in both Learn and Labs.

Guided explanation:

```text
1. Prepare a broad set of possibilities
2. Cost layer marks better and worse answers
3. Mixer layer moves probability between answers
4. Repeat the layers
5. A classical optimiser adjusts the angles
6. Measure candidate bitstrings
```

Visual flow:

```text
Initial state
   ↓
Cost layer γ
   ↓
Mixer layer β
   ↓
Repeat p times
   ↓
Measure
   ↓
Classical optimiser updates γ and β
   ↺
```

Explain that QAOA is hybrid:

`The quantum circuit generates and scores probability patterns. A classical optimiser chooses the circuit angles.`

Hide these names in Guided mode unless expanded:

- COBYLA
- SparsePauliOp
- ansatz
- transpiler metadata

Retain them in Researcher mode.

## Phase 10: EXP-002 narrated laboratory

Restructure Guided EXP-002 as a four-stage story.

### Step 1: Colour the graph

Allow the learner to toggle node assignments.

Show the cut score live.

Avoid starting with a bitstring selectbox alone.

### Step 2: Let the classical computer try every answer

Show:

- number of possible assignments;
- best cut score;
- optimal partition pair.

Do not show the full 16-row exact table by default.

Put it under:

`Show all classical assignments`

### Step 3: Meet QAOA

Show the QAOA loop diagram.

Use safe beginner defaults.

Hide optimiser and seed controls under advanced settings.

Show an explicit progress state while QAOA is running.

### Step 4: Compare the answers

Add a persistent three-answer legend:

- `Exact answer` — known best solution from brute force
- `Quantum expectation` — average objective represented by the final state
- `Measured samples` — bitstrings observed from finite shots

Use consistent colours, icons and wording everywhere.

Under every metric, include one plain-language interpretation.

Examples:

- `1.0 would mean the expected result matches the exact optimum.`
- `This was the best bitstring actually observed in the sample.`
- `Exact search is the ground truth for this small graph.`

Highlight optimal bitstrings in the distribution.

Annotate:

- exact optimum;
- best sampled result;
- probability assigned to optimal solutions.

Keep the full exact table, QUBO matrix, Ising operator, optimiser history and raw metadata in Researcher mode.

## Phase 11: EXP-005A current status and research case study

The app currently describes EXP-005A as a plan or future experiment.

Update it to the completed state.

EXP-005A was merged through PR #7.

Final squash-merge SHA:

`d0b3ab9b134807ff4136c4346cc3a55bc29a9837`

Final implementation branch head before squash:

`26cc6f49fa2563324dd3680f468dd33e35754fe9`

Closure-review merge:

`bc8e409c0cd955430401a47eb240fd600bdba52a`

Mandatory pre-QAOA checkpoint:

`4cd27253385c349c4a4b87f67388452ea8b2cef4`

### Registered EXP-005A result

Preserve exactly:

- fixture:
  `synthetic-two-family-v1-seed42`
- tune count:
  `8`
- `tau`:
  `0.25`
- `lambda`:
  `0.1`
- threshold:
  `0.05`
- exact optima:
  - `00001111`
  - `11110000`
- exact assignments checked:
  `256`
- direct/QUBO maximum disagreement:
  `5.329070518200751e-15`
- QUBO/Ising maximum disagreement:
  `2.4868995751603507e-14`
- shots:
  `4096`
- expected energy:
  `5.2872120969`
- expected gap:
  `5.2872120969`
- probability `00001111`:
  `0.259521484375`
- probability `11110000`:
  `0.271484375`
- optimal complement-class probability:
  `0.531005859375`
- balanced-sample probability:
  `0.7119140625`
- execution:
  genuine local Qiskit p=1
- exact brute-force enumeration remains authoritative.

Do not alter, regenerate or retune this registered result.

Load it read-only from the registered public result artefact where possible.

### Guided EXP-005A case study

Add an optional final Guided case study:

`Can a quantum optimisation circuit recover two synthetic tune families?`

Show:

- eight simple tune cards;
- two intended families;
- one bit per tune;
- the optimal partition visually;
- complement symmetry:
  swapping all 0s and 1s describes the same partition;
- exact baseline;
- sampled QAOA probability on the optimum class;
- expected performance caveat.

Use plain language:

`The samples often landed on the correct family split, but the average expected objective was still far from the exact optimum.`

State prominently:

- this is synthetic data;
- exact search is faster and authoritative at this size;
- no quantum advantage is claimed;
- no real tune-family inference is claimed.

### Researcher EXP-005A view

Add a complete Researcher results page with:

- fixture provenance;
- plan and review commits;
- checkpoint chronology;
- threshold manifest;
- direct/QUBO validation;
- QUBO/Ising validation;
- exact assignment distribution;
- baselines;
- local Qiskit configuration;
- expected versus sampled interpretation;
- circuit metrics;
- full result JSON;
- review closure status;
- limitations and claims boundary.

## Phase 12: Reference redesign

Guided Reference should contain:

- searchable glossary;
- recommended reading order;
- beginner external guides;
- help with notation;
- “I am stuck” guidance.

Add inline glossary tooltips for first use of:

- qubit
- amplitude
- measurement
- shots
- bitstring
- QUBO
- Ising
- QAOA
- optimiser
- exact
- expected
- sampled

Researcher Reference should retain:

- Git and PR workflow;
- worktrees;
- CLI;
- tests;
- package extras;
- validation commands;
- experiment provenance.

Remove duplicated Git content by using one shared rendering implementation.

Guided mode should link to it only as optional developer material.

## Phase 13: Responsive design and accessibility

Test desktop and narrow widths.

Requirements:

- no multi-line nine-topic radio strip;
- primary buttons become full width on narrow screens;
- forms stack cleanly;
- charts remain readable;
- sidebars do not dominate the viewport;
- no horizontal overflow;
- no meaning conveyed only through colour;
- appropriate text contrast;
- keyboard-accessible controls;
- descriptive labels;
- alt text or captions for diagrams;
- animations optional;
- respect reduced-motion preferences where possible.

Animations should be short and user-triggered:

`Play 5-second demonstration`

Do not autoplay distracting loops.

## Phase 14: Error and empty states

Improve empty Lab states.

Replace generic submission messages with visual prompts such as:

`Make a prediction to unlock the result.`

For Qiskit missing:

- show a clear blocking banner in Labs;
- explain that Qiskit is the local simulator software;
- provide one safe installation route;
- link to Researcher Reference;
- do not expose local paths.

For long QAOA execution:

- show progress stages, not only an indefinite spinner.

For network or Streamlit connection errors:

- do not capture them as valid review screenshots;
- provide a clean retry message.

## Phase 15: Session behaviour

Keep progress session-local unless persistence already exists safely.

Track:

- selected experience;
- current lesson;
- completed Guided lessons;
- completed EXP-001 circuits;
- last successful Lab;
- recommended next step.

Add a clear distinction between:

- learning progress;
- technical application session/cache.

Use separate labels.

Do not write personal learning data to disk without explicit approval.

## Phase 16: Testing

Add or update tests for:

- Guided Learner default;
- Researcher mode selection;
- mode persisted in session state;
- researcher-only content hidden in Guided mode;
- researcher content still available;
- navigation grouping;
- next-step selection;
- EXP-001 recommended circuit;
- metric legend labels;
- EXP-005A registered values loaded unchanged;
- no private path leakage;
- screenshot route assertions where practical.

Run existing private app tests.

Also run appropriate public package tests only when the app integration requires them.

Do not change public scientific test expectations.

## Phase 17: Screenshot automation and new review pack

The previous screenshot pack contained several incorrectly labelled or stale captures and one EXP-002 screenshot with a connection-error modal.

Fix the screenshot automation.

For every screenshot:

1. navigate to the target page;
2. wait for Streamlit rerun completion;
3. wait for the expected visible heading;
4. assert the expected topic is selected;
5. reject the capture if an error modal or traceback is visible;
6. crop or avoid excessive blank page space;
7. use safe demo content;
8. exclude filesystem paths and Git metadata from Guided screenshots.

Capture at minimum:

### Guided Learner

- Home first visit
- Home continue state
- Foundations lesson
- Hadamard visual
- Bell visual
- Guided EXP-001 before run
- Guided EXP-001 result
- Optimisation primer
- Max-Cut good/bad example
- QUBO–Ising conversion
- QAOA loop
- Guided EXP-002 steps 1–4
- Guided EXP-005A case study
- Guided glossary
- narrow/mobile Home
- narrow/mobile Learn
- narrow/mobile Lab

### Researcher

- Researcher Home
- Researcher Quantum Advanced
- Researcher EXP-002 result detail
- Researcher EXP-005A provenance and result
- Researcher CLI/test reference

Generate a new privacy-safe review pack:

`review-pack-v2`

Include:

- updated README;
- revised page map;
- mode comparison;
- screenshots;
- file-change summary;
- accessibility notes;
- test results;
- known limitations;
- privacy review.

Do not include full private source files unless already approved.

## Acceptance criteria

The work is complete only when:

1. Guided Learner and Researcher modes both work.
2. Researcher mode retains all current technical capability.
3. Guided Home has one obvious Start action.
4. Guided navigation presents a clear ordered learning path.
5. Quantum concepts have visuals before mathematical notation.
6. EXP-001 has a complete visual Predict → Run → Explain → Next flow.
7. EXP-002 is presented as a four-step narrated experience.
8. Exact, expected and sampled results have a consistent persistent legend.
9. Seeds, raw matrices, JSON and module paths are hidden by default in Guided mode.
10. Researcher mode can still access all of them.
11. EXP-005A is shown as implemented and merged, not planned.
12. EXP-005A registered values remain exactly unchanged.
13. The Guided EXP-005A case study clearly states all scientific limitations.
14. Mobile navigation no longer relies on the wrapped nine-topic strip.
15. Inline glossary help is available.
16. Every lesson has a clear next step.
17. No private path, token, secret or credential is exposed.
18. Nothing under `private/` is staged in the public Git repository.
19. Existing public experiment code and results remain unchanged.
20. The new screenshot review pack contains correctly labelled, error-free captures.

## Final response

Return:

- summary of the implemented dual-mode design;
- backup location;
- files changed;
- new files created;
- Guided Learner features completed;
- Researcher features preserved or extended;
- EXP-005A status update;
- confirmation registered values were unchanged;
- test results;
- app launch command and URL;
- screenshot pack location;
- privacy checks performed;
- confirmation nothing under `private/` was staged or published;
- remaining known issues;
- recommended next small iteration.

Do not claim a feature is complete unless it is implemented and tested.
