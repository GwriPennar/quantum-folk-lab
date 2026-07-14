# OpenAI Build Week 2026 — Quantum Folk Lab Governing Plan

## 1. Status and authority

This document is the governing proposal for an OpenAI Build Week product increment in Quantum Folk Lab. It authorises no implementation by itself. The human decisions in section 24 approve the product direction and establish implementation bounds; implementation begins only after final human review of this amended plan. Delivery uses the controlled pull-request sequence in section 22, with explicit tests and rollback boundaries.

The plan is subordinate to the repository's existing scientific records, public-release gates, privacy rules, and human review decisions. In particular, it does not reopen EXP-005A, change its registered artefacts or results, or publish private material. The root `README.md` remains unchanged during planning and core implementation; only the final release PR may reconsider G12 through the specific human decision gate defined below.

## 2. Verified repository baseline

- Repository: `GwriPennar/quantum-folk-lab`.
- Governing base: `main` at `281ba4013112a071bba4a70579c24d051da36c51` (`feat: experimental public Foundations Learning Console (#13)`).
- Public Foundations baseline: five lessons in `learn/`, portable parsing/validation/export in `src/quantum_folk_lab/learning/`, and the minimal Streamlit renderer in `apps/learning_console/`.
- Scientific baseline: completed EXP-001 local circuit demonstrations, EXP-002 exact/Qiskit Max-Cut reference, and EXP-005A exact and genuine local-Qiskit tune-family workflow.
- Local-only condition: the unstaged `.gitignore` addition `private/` is not part of this plan or any future publication.

Any implementation PR must state its exact base commit and revalidate these boundaries after rebasing or merging `main`.

## 3. Submission thesis

Quantum Folk Lab makes a small quantum-optimisation experiment understandable end to end: a user follows a culturally grounded synthetic music example from pairwise musical evidence to a transparent optimisation model, exact classical truth, optional genuine local Qiskit simulation, honest comparison, and a portable learning record.

The submission is about explainability and reproducible scientific workflow, not quantum advantage, automated musicology, or general-purpose music generation.

## 4. Target user and problem

The primary user is a quantum-curious learner, educator, or technically literate musician who can engage with a short guided demo but should not need prior QUBO, Ising, or Qiskit expertise.

The problem is not access to another optimiser. It is the missing connective tissue between a recognisable musical question and the repository's already rigorous but separate research and teaching components. The user needs to see what assumptions enter the model, which result is ground truth, what the circuit actually does, and which claims the evidence does not support.

The first release is a guided demonstration, not an open-ended research workbench. Researcher-facing controls and arbitrary uploads would make validation, licensing, runtime, and interpretation too fragile for Build Week.

## 5. Current repository capabilities

Capabilities already present on `main` are:

- EXP-001: local Qiskit/Aer circuit construction, transpilation, measurement, finite-shot reporting, and clear failure when optional quantum dependencies are missing.
- EXP-002: the four-node `cycle4` Max-Cut reference, exhaustive exact solution, checked QUBO/Ising conventions, genuine p=1 local Qiskit QAOA, and separate expected-versus-sampled metrics.
- EXP-003/004 foundations: deterministic synthetic melodies, interval/contour/rhythm similarity, similarity-graph construction, a two-family QUBO, exact enumeration, and label-invariant evaluation.
- EXP-005A: the registered eight-tune `synthetic-two-family-v1-seed42` fixture; exact direct/QUBO/Ising verification over 256 assignments; complement handling; random baselines; a genuine local Qiskit estimator/sampler route; provenance-rich result schemas; and `tune-family-*` CLI commands.
- CLI: `qfl` commands for diagnostics, quantum basics, Max-Cut, synthetic generation, exact/classical comparison, and registered tune-family exact/QUBO/QAOA comparison.
- Learning Console: a public Streamlit app that renders five registry-driven portable lessons, glossary content, semantic markers, and an optional EXP-001 Hadamard service.
- Portable learning infrastructure: Markdown/YAML parsing, registry and glossary models, schema validation, semantic-state validation, and static Markdown/HTML export independent of Streamlit.
- Safety and quality controls: public-safety scanning, no-secrets tests, learning clean-clone/path-leak tests, exact and quantum test markers, Ruff/mypy configuration, and release gates G1–G12.

There is currently no integrated tune-family product journey in the Learning Console, no Build Week-specific demo-state schema, no portable experiment narrative/export, and no runtime AI product capability. The current `solve-qaoa` path is explicitly a deterministic classical fallback; only the separate registered Qiskit routes may be described as genuine local QAOA.

## 6. Proposed end-to-end user journey

The central journey is one fixed, reliable walkthrough:

1. **Meet the fixture.** The user sees eight named, deterministic synthetic tune variants grouped only for later evaluation; no private or copyrighted source material is loaded.
2. **Choose the question.** The first release offers one task: divide the variants into two unlabeled families using the registered, constrained formulation. Parameters are explained but not freely editable in the primary demo.
3. **Inspect musical evidence.** The console shows interval, contour, and rhythm similarity concepts and a small pairwise/graph summary derived from public functions.
4. **Build the model.** A plain-language view explains binary variables, same/different penalties, the balance term, QUBO energy, and complement symmetry. Technical detail is progressively disclosed.
5. **Establish truth.** Exact enumeration runs first and is labelled the authoritative answer for this eight-variable fixture.
6. **Choose execution.** The user may stop at the classical result or run the existing genuine local Qiskit route when the optional quantum environment is installed. Missing Qiskit produces an educational capability message, never fabricated results.
7. **Compare honestly.** The console separates exact optimum, expected energy, finite-shot distribution, best sampled solution, complement-class probability, circuit metrics, and limitations.
8. **Interpret.** A deterministic explanation is always available. When configured, the approved **Explain this result** GPT-5.6 capability may explain only a validated, versioned result envelope at the selected learner level and must identify the fields grounding important statements.
9. **Export.** The user exports a portable Markdown/HTML reproducibility record containing fixture ID, configuration, execution classification, seeds, software/circuit metadata where applicable, results, claims boundary, and validation outcome.

No step requires an LLM. No LLM computes energies, alters measurements, selects the authoritative result, or writes back to registered research artefacts.

## 7. Build Week product increment

The proposed increment is a new **Guided Experiment** mode within the existing public Learning Console. It orchestrates existing public domain, exact, and Qiskit APIs around new validated, versioned demo-state and result-envelope contracts and portable explanation/export content.

New work would comprise:

- a Build Week demo fixture reference and schema that points to existing deterministic generation without editing EXP-005A registrations;
- a deterministic workflow service that derives model and exact results from public APIs;
- an optional adapter to the existing genuine local-Qiskit function using p=1, recorded seeds, an initial default of 256 sampler shots, and a bounded tested optimisation configuration clearly distinct from the registered 4,096-shot result;
- registry-integrated portable learning content for the experiment story;
- Streamlit views for steps, evidence, comparison, and export;
- the approved, non-required **Explain this result** GPT-5.6 capability behind a validated structured interface and deterministic fallback;
- demo acceptance tests and submission packaging.

The increment must not overwrite, regenerate, or silently reuse the registered EXP-005A result as though it were a new live run.

## 8. Explicit non-goals

- Quantum advantage, scalability, production-readiness, or hardware-performance claims.
- IBM Runtime, cloud backends, QPU execution, credentials, or repository-stored API keys.
- Arbitrary tune upload, private corpora, copyrighted corpus ingestion, arbitrary MIDI ingestion, generative composition, a full synthesis engine, or general tune-family discovery. A small deterministic monophonic preview is permitted only as a removable stretch feature.
- A free-form optimisation-model generator or unconstrained AI agent.
- Editing registered EXP-005A fixtures, manifests, configurations, numerical results, or provenance.
- Publishing private Learning Console material or progress state.
- Changing the root `README.md` during planning or core implementation. A concise `OpenAI Build Week 2026` section may be considered only through the final release-PR human gate after the product is runnable and reviewed.
- Depending on or reusing Sonorix or Cortex Foundry code, data, prompts, credentials, architecture, or intellectual property.
- EXP-006 noise modelling, EXP-007 hardware work, authentication, persistence, telemetry, or multi-user infrastructure.

## 9. Architecture

The increment should preserve the current portable-content/Python-renderer boundary:

```text
learn/ portable experiment lesson + glossary/registry references
        |
        v
quantum_folk_lab.learning parser, validation, semantic state, export
        |
        +------------------------------+
        |                              |
        v                              v
validated demo-state service     optional AI explainer adapter
        |                         (validated input/output only)
        v                              |
domain -> similarity -> QUBO -> exact -+
                              |
                              +-> optional existing local Qiskit QAOA
        |
        v
Streamlit guided renderer -> portable reproducibility export
```

The scientific service layer must not import Streamlit. UI code consumes immutable or serialisable result models. Exact and quantum execution classifications must be typed values, not prose inferred by the renderer. Export should reuse `quantum_folk_lab.learning.export` patterns and remain testable without Streamlit or Qiskit.

The implementation should reuse `registered_fixture`, exact verification, complement canonicalisation, Qiskit count decoding, and result serialization rather than duplicate formulae in UI code. A new adapter may select and reshape fields but must preserve provenance and numerical precision.

## 10. AI and Codex role

### Codex as development agent

Codex may analyse the public repository, implement approved narrow slices, write tests and documentation, run local validation, review diffs, and check reproducibility. Codex must follow branch/PR boundaries, must not inspect `private/`, and must not change scientific registrations without a separately approved experiment plan.

### GPT-5.6 as product capability

The approved product-level capability is provisionally titled **Explain this result** and supports the learner levels **First encounter**, **Technical learner**, and **Research detail**. It is optional at runtime: the scientific journey and a deterministic explanation must work without an external AI call or configured API credential. The capability may receive only a validated, versioned result envelope containing approved scientific fields. It may:

- explain the musical question and optimisation representation;
- compare exact and quantum outputs without changing their authority;
- explain sampling uncertainty, complement symmetry, and limitations;
- adapt vocabulary and depth to the selected learner level;
- produce structured output conforming to an explanation schema;
- identify the result-envelope fields grounding important statements.

It may not compute or revise energies, infer missing scientific values, create or change a fixture or QUBO, modify measured or registered results, choose the authoritative solution, claim quantum advantage, accept arbitrary repository or private-file context, or become required for the deterministic workflow. Its output must pass schema, prohibited-claim, grounding, and semantic checks before display; invalid or unavailable output falls back to deterministic content. Prompt text and model output are not scientific evidence.

Before code is written, implementation must pass a decision gate that verifies the appropriate currently supported GPT-5.6 API model identifier from authoritative OpenAI documentation; this plan deliberately does not guess it. The implementation must record the chosen model/configuration, preserve a deterministic no-key path, and keep credentials out of the repository, logs, exports, screenshots, and demonstration materials.

## 11. Musical-data policy

The primary demo uses only the deterministic public synthetic fixture. The UI may render symbolic descriptions derived from its integer pitch offsets and durations, but must not imply cultural authenticity or real-world family classification.

A safely licensed miniature fixture is future work only after a separate provenance review records source, licence, permitted transformations, attribution, cultural context, and redistribution terms. User uploads and any private corpus are out of scope. No file path, identifier, or aggregate derived from `private/` may enter public code, tests, fixtures, screenshots, prompts, exports, or submission materials.

## 12. Classical and quantum computation boundaries

Classical computation remains responsible for fixture generation, feature extraction, similarity, graph construction, QUBO construction, exhaustive enumeration, verification, baselines, metrics, validation, and report assembly. Exact enumeration is the authoritative reference for the bounded fixture.

Genuine quantum simulation means only the existing Qiskit `QAOAAnsatz`/estimator/sampler path executing locally with explicit execution classification, seeds, optimiser settings, shots, and circuit metrics. The older deterministic `solve-qaoa` fallback remains classical and must never be relabelled.

The Guided Experiment must distinguish three evidence states in its model, labels, UI, and export:

1. the exact result computed during the current session, which is authoritative;
2. an optional quick Qiskit result computed during the current session using p=1, recorded seeds, 256 sampler shots by default, and a bounded tested optimisation configuration;
3. the existing registered 4,096-shot EXP-005A reference evidence, which is historical evidence and never a live run.

Missing Qiskit dependencies produce a useful capability explanation, not an error cascade or fabricated output.

The comparison must distinguish:

- exact optimum energy and complement class;
- statevector expected energy or derived gap;
- finite-shot sampled distribution and best sample;
- probability assigned to the optimum complement class;
- runtime/circuit metadata and limitations.

Sampling an optimum once is not equivalent to an expected optimum, speedup, or advantage. For eight variables, exhaustive classical solution is simpler and authoritative.

## 13. Learning Console integration

Make **Guided Experiment** the prominent product mode in the public Learning Console, with the intended hierarchy **Guided Experiment**, **Foundations**, **Glossary**. The exact Streamlit navigation mechanism is an implementation choice, but the experiment must feel like one coherent journey rather than developer controls. Foundations remain supporting learning material. Preserve portable Markdown as the source of explanatory prose and Python as the source of computation and interactive widgets.

The UI should use progressive disclosure: question and outcome first; evidence/model next; equations, bit ordering, circuit metrics, and provenance deeper. It should reuse glossary terms and semantic markers, expose an explicit “exact reference” before quantum execution, and preserve a useful non-Qiskit path.

Static export must remain possible from validated models without launching Streamlit. Progress persistence is out of scope. The root `README.md` remains untouched during core implementation. The release PR must ask for a specific human decision on a concise, clearly labelled `OpenAI Build Week 2026` section linking the runnable Learning Console and dedicated setup guide and explaining the submission increment.

## 14. Scientific claims and interpretation rules

Allowed claims must be directly supported by a named public function, test, or result field. Required labels include “deterministic synthetic fixture,” “exact classical reference,” “local ideal simulation,” and “no claim of quantum advantage” where relevant.

The product must not claim that it discovers real folk families, models culture objectively, outperforms classical methods, demonstrates hardware behaviour, or proves scalability. It must explain complement symmetry and must not present `00001111` as uniquely meaningful when `11110000` represents the same unlabeled partition.

AI prose, screenshots, demo narration, and submission copy are held to the same rules as code. A claim-policy test should reject advantage language, misclassified classical fallback, and conflation of expected and sampled metrics.

## 15. Privacy, publication and commercial-IP boundaries

- `private/` is neither an input nor an implementation reference and remains ignored, uninspected, unstaged, and unpublished.
- The public-safety scanner and clean-clone tests are mandatory publication gates.
- No credentials, personal paths, emails, progress files, screenshots with private context, or generated operational logs enter Git.
- Sonorix is separate commercial IP and must not be inspected, named as an internal dependency, copied, adapted, or used as design provenance.
- Cortex Foundry may motivate general methodological discipline only; the Build Week product must stand alone and share no code or hidden dependency with it.
- PRs #10–#12 and #14 are outside this work and must not be modified or closed.

## 16. Workstreams

Seven controlled workstreams describe the work, but they are grouped into the four delivery PRs in section 22 rather than mapped one-to-one to administrative PRs:

1. **Governance and contracts:** approve this plan; define demo-state, result-envelope, execution-classification, claim-policy, and export schemas.
2. **Fixture and deterministic workflow:** reference the synthetic fixture; compose similarity, graph, QUBO, exact, and validation APIs without changing registered artefacts.
3. **Quantum adapter and comparison:** wrap the genuine local Qiskit path, preserve provenance, bound demo runtime, and present expected/sampled metrics separately.
4. **Portable experiment learning content:** add the guided narrative, glossary links, semantic markers, and static export representation.
5. **Learning Console product flow:** render the stepped journey, capability states, comparison, limitations, and export.
6. **Grounded GPT-5.6 explanation:** implement the approved narrow capability only behind validated structured boundaries, after confirming the supported model identifier, with deterministic fallback.
7. **Demo, submission, and independent review:** acceptance tests, clean-clone rehearsal, narrative/screenshots, claim audit, provenance pack, and final human review.

### Scope-priority tiers

**P0 — submission blocking**

- validated demo/result contract;
- exact classical journey;
- coherent Guided Experiment UI;
- deterministic explanation;
- reproducibility export;
- setup documentation;
- tests and public-safety checks.

**P1 — high-value submission features**

- bounded genuine local-Qiskit quick run;
- grounded GPT-5.6 explanation;
- clear Codex/GPT-5.6 evidence;
- judge-runnable packaging.

**P2 — removable stretch**

- deterministic musical playback;
- additional visual polish;
- extra learner-level refinements.

A P2 feature must never delay a P0 feature. P1 work may be reduced if it threatens a coherent, validated P0 journey.

## 17. Proposed experiment or demo fixture

Use the approved `synthetic-two-family-v1-seed42` fixture with the existing eight public tune identifiers and registered formulation (`tau=0.25`, balance penalty `lambda=0.1`) as the sole core demo. The Guided Experiment may recompute its model and exact solution through existing public APIs. It must not change the fixture or EXP-005A configuration, overwrite or regenerate registered artefacts, or present registered evidence as a newly executed result.

The primary live path recomputes the authoritative exact result. The optional quick Qiskit run uses the approved bounds in section 12 and remains separate from the registered EXP-005A 4,096-shot evidence. The registered evidence may be displayed only as a clearly labelled historical reference and never as a current-session run.

The core demo describes variants textually or with a simple public-safe symbolic representation. As P2, it may add a reproducible deterministic monophonic preview derived only from the fixture's public synthetic notes, clearly labelled as a preview rather than generated music and tested at its output-contract boundary. It must not add uploads, arbitrary MIDI ingestion, generative composition, a corpus, a full synthesis engine, or Sonorix code or architecture. If playback threatens P0 delivery, remove it and revise the Devpost elevator pitch to remove any promise that users can hear the result.

## 18. Testing and validation strategy

Each PR must add tests at the lowest applicable layer:

- schema/model tests for versioned demo state, versioned result envelope, execution classification, provenance, and invalid/partial states;
- deterministic fixture-to-exact golden invariants without duplicating registered result files;
- all-assignment direct/QUBO/Ising equivalence remains covered by existing tests;
- adapter tests that prove classical fallback and genuine Qiskit classifications cannot be confused;
- a bounded quantum smoke test under the existing `quantum` marker;
- Learning Console service tests independent of Streamlit, plus renderer smoke tests where feasible;
- lesson registry, semantic parity, glossary, clean-clone, static export, and no-private/path-leak tests;
- claim-policy tests for advantage language and expected/sampled conflation;
- public-safety scan, `git diff --check`, Ruff, relevant pytest suites, and existing CI gates.

AI tests, if applicable, use fixed structured fixtures and adversarial invalid outputs; they do not require a live API in ordinary CI. The deterministic explanation path is the acceptance baseline.

## 19. Demo acceptance criteria

The increment is accepted for submission only when a fresh user can complete this coherent path:

1. install the documented dependencies from a fresh public checkout;
2. start the Learning Console;
3. enter **Guided Experiment**;
4. understand the fixed synthetic musical question;
5. inspect the derived musical evidence;
6. run the exact solution;
7. see unambiguously that the exact result is authoritative;
8. either run the bounded quick Qiskit route or receive a clear capability message;
9. obtain a deterministic explanation;
10. optionally obtain a grounded GPT-5.6 explanation when configured;
11. export a reproducibility record;
12. understand the scientific limitations.

The demo must never depend on a successful external AI call or a long quantum optimisation run. Expected and sampled metrics, complement symmetry, execution classification, and limitations must be visually distinct. The export must include fixture/configuration identifiers, seeds, execution class, results, validation state, software/circuit metadata when relevant, and the claims boundary. Public-safety, learning, exact, adapter, and claim-policy tests must pass from a clean public tree. Registered EXP-005A artefacts/results, `private/`, and unrelated PRs remain unchanged; the root README changes only if the final release gate is explicitly approved.

## 20. Submission artefacts

The submission targets the **Education** category and requires:

- a working public project;
- a concise Build Week setup and judging guide;
- a sample-data and fixture explanation;
- an architecture diagram matching implemented boundaries;
- a public demonstration video under three minutes with clear audio narration explaining how GPT-5.6 and Codex were used;
- a repository URL suitable for judging and testing;
- an evidence record showing where Codex accelerated development and where Gwri made key scientific and product decisions;
- the `/feedback` Codex session ID from the primary session in which most core functionality was developed;
- the final Devpost narrative;
- public-safe screenshots or stills needed for the project page;
- a reproducibility export produced by the application;
- test and release-gate evidence;
- dependency and local-run instructions, with the final README link governed by the release decision gate;
- attribution/licensing notes and an explicit no-advantage statement;
- a list of development uses of Codex distinct from runtime product capabilities.

Submission copy is reviewed against implemented evidence immediately before publication. The draft under `private/submission/` remains local and unpublished until the final release-evidence stage.

### Build Week compliance

- Position the submission in the Education track and deliver a working, runnable product rather than a plan or disconnected prototype.
- Present one complete, coherent product experience with a public video, repository, setup/judging documentation, and reproducibility evidence.
- Record distinct evidence for Codex development acceleration and the grounded GPT-5.6 product capability, including Gwri's scientific and product decisions.
- Preserve this Codex session as the primary development session unless Gwri explicitly directs otherwise, and capture its `/feedback` session ID for submission.
- Start the Codex/Gwri decision-and-contribution evidence record in the deterministic-core PR, update it during the Guided Product work, and capture `/feedback` plus final evidence before the release deadline rather than deferring all evidence work to the final PR.
- Treat the final submission deadline as an external delivery constraint: P0 completeness, validation, review, and evidence take precedence over stretch work.

## 21. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Scope expands into a general music lab | Fixed fixture, one task, one guided route, and explicit non-goals. |
| UI duplicates scientific logic | Services call existing domain/exact/Qiskit APIs; renderers receive validated models. |
| “AI-assisted” becomes vague or decorative | Deterministic product is complete; runtime AI requires a named benefit and approval gate. |
| AI fabricates or overstates results | Structured read-only result envelope, output schema, claim validation, citations to fields, deterministic fallback. |
| Quantum result is oversold | Exact-first presentation, execution classification, separate expected/sampled metrics, mandatory limitations. |
| Live Qiskit path is slow or brittle | Bounded demo configuration, capability detection, rehearsed no-Qiskit path, optional approved historical-result view. |
| Registered science drifts | Treat EXP-005A artefacts as immutable; derive live state via public APIs; diff/test guardrails. |
| Private or commercial material leaks | No private inputs, clean-clone development, safety scan, path/leak tests, human publication review. |
| Learning content and UI diverge | Registry/schema/semantic validation and portable export tests remain authoritative. |
| Build Week ends with disconnected features | Demo acceptance criteria require one complete end-to-end journey before optional AI or polish. |
| Qiskit deprecations destabilise the demo | Pin to current declared ranges, use existing adapter boundary, track warnings, avoid unplanned migration during core build. |

## 22. Sequenced implementation plan

1. **Governing-plan PR:** this document only, with independent plan review and no implementation.
2. **Validated deterministic-core PR:** versioned demo-state and result-envelope schemas; fixture adapter; musical-evidence derivation; exact classical workflow; deterministic explanation; reproducibility data model; tests; and the initial Codex/Gwri contribution evidence record.
3. **Guided product PR:** coherent Learning Console journey; comparison views; optional bounded local-Qiskit adapter; constrained GPT-5.6 explainer after the model-identifier gate; optional deterministic musical preview only if the core is stable; and integration/UI tests.
4. **Release and submission PR:** setup and judging guide; deployment or judge-runnable path; final README/G12 decision; demo evidence; screenshots; limitations; submission-support documentation; and full validation.

An independent final review may occur on the release PR or through one additional review-only PR if time permits. Do not create administrative PRs that do not improve evidence, correctness, or the runnable product.

Every PR must declare changed files, non-goals, tests, rollback (revert that PR without invalidating earlier layers), and whether it changes the public dependency surface. Optional work cannot block the exact-first core journey.

Within the Guided Product PR, Qiskit, GPT-5.6, and musical-preview adapters must remain separable from the P0 UI and deterministic services. If a P1 or P2 adapter is not ready, remove it from that PR rather than delaying review of the coherent P0 product.

## 23. Stop conditions

Stop the affected workstream and request human direction if:

- implementation would require inspecting or publishing `private/`, Sonorix, or other non-public material;
- the exact reference, direct/QUBO/Ising equivalence, bit ordering, or complement handling disagrees with the verified public baseline;
- a proposed change would alter registered EXP-005A artefacts or numerical results without a separately approved experimental plan;
- the demo requires cloud/QPU access, credentials in Git, real tune data, or an unreviewed licence;
- runtime AI cannot be prevented from changing or obscuring validated scientific fields;
- the no-key/no-Qiskit route is not coherent;
- the bounded live Qiskit path cannot meet the approved reliability/runtime budget;
- public-safety, clean-clone, semantic, exact, quantum, or claim gates fail;
- root `README.md` would need modification before the final release gate, or PRs #10–#12/#14 would need modification;
- the core journey cannot be completed before optional AI, upload, audio, persistence, or visual-polish work begins.

## 24. Approved human decisions

1. **Core fixture — APPROVED.** Use `synthetic-two-family-v1-seed42` as the sole core fixture. Recompute the model and authoritative exact result through existing public APIs without changing the fixture, EXP-005A configuration, or registered artefacts, and never relabel registered evidence as a new execution.
2. **Qiskit demonstration budget — APPROVED WITH BOUND.** The exact path always works without Qiskit. The optional genuine local-Qiskit quick run uses the existing route, p=1, recorded seeds, 256 sampler shots by default, and a bounded tested optimisation configuration. Exact-current, Qiskit-current, and registered-4,096-shot evidence are separate states; missing dependencies produce a capability explanation.
3. **Runtime GPT-5.6 capability — APPROVED.** Implement the narrow **Explain this result** feature for First encounter, Technical learner, and Research detail using only an approved validated result envelope. It cannot compute, infer, revise, or authorise scientific values and is never required. Verify the currently supported GPT-5.6 API model identifier from authoritative documentation before coding; do not guess it. Keep credentials out of all repository and evidence surfaces.
4. **Product route — APPROVED.** Make **Guided Experiment** prominent in the hierarchy **Guided Experiment**, **Foundations**, **Glossary**, as one coherent journey. Choose the exact Streamlit navigation during implementation; keep Foundations available and leave the root README unchanged through core work.
5. **Musical rendering — APPROVED AS P2 STRETCH.** A tested, reproducible monophonic preview derived only from public synthetic notes is allowed. It is not generated music and must be removed, with any Devpost hearing claim revised, if it threatens P0 delivery. No uploads, arbitrary MIDI, composition, corpus, synthesis engine, or Sonorix reuse.
6. **Submission and repository material — APPROVED.** Target Education and produce the working project, judging guide, fixture explanation, sub-three-minute narrated video, judge-ready repository URL, Codex/Gwri decision evidence, primary-session `/feedback` ID, Devpost narrative, public-safe stills, and application reproducibility export. Keep `private/submission/` local until final release evidence.
7. **README and G12 — APPROVED CONTROLLED RECONSIDERATION.** Do not change the root README during planning or core implementation. The final release PR must ask for human approval of one concise `OpenAI Build Week 2026` section linking the runnable console and setup guide and explaining the increment; it is never automatic.
8. **Delivery sequence — APPROVED.** Use the four PRs in section 22, with independent final review on the release PR or one evidence-bearing review-only PR if time permits. Avoid administrative PRs without correctness, evidence, or runnable-product value.
