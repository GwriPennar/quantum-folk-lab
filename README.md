# Quantum Folk Lab

> Learn quantum computing by checking the exact answer first — folk-music problems, transparent
> experiments, real IBM hardware and no hype.

Quantum Folk Lab is an Education product for learners and educators. Folk music supplies the
structured choice problems: the console reveals known classical truth, compares a bounded quantum
method, and then shows what governed IBM hardware did and did not reproduce.

## Three-step learner journey

1. **Reveal the exact answer.**
2. **Compare the quantum method.**
3. **Inspect real IBM hardware evidence.**

## Four proof points

- The Guided Experiment checks all **256 assignments exactly** before interpretation.
- The compact experiment uses **public folk-tune-family data** in a 16-state problem.
- The IBM landscape reached rho **`0.96`** and was independently reproduced with cross-run rho
  approximately **`0.978`**.
- **GPT-5.6 may explain governed evidence but cannot alter it.**

<!-- A human-reviewed 256 Reveal screenshot should be inserted here after visual approval. -->

## Launch the Learning Console

```bash
pip install -e ".[learning]"
streamlit run apps/learning_console/app.py
```

Open **Experiments** and begin with **Start here · Guided experiment**. Reveal all 256 answers,
then compare registered local simulation, the real folk-data compact experiment, the first IBM
validation, and the replicated hardware landscape. **Foundations** and **Glossary** provide the
beginner path. No IBM credential or OpenAI API key is required; optional Qiskit remains
button-gated and optional GPT-5.6 fails closed to deterministic explanation.

## Governed IBM evidence

The read-only Learning Console panel distinguishes three layers:

- **EXP-010C — first hardware validation:** the exact optimum `1010` remained the most likely state.
- **EXP-010D — controlled 25-cell landscape:** ideal/hardware rho `0.96`, classified
  **LANDSCAPE SUPPORTED**.
- **EXP-011 — independent 81-cell replication:** full rho `0.9047`, embedded-25 rho `0.9315`, and
  cross-run rho `0.9777`, classified **STRONGLY REPLICATED**.

Both landscape reports retain the predeclared control warning. Read the authoritative
[EXP-010D report](experiments/EXP-010D-hardware-parameter-landscape-run/RESULT-REPORT.md) and
[EXP-011 report](experiments/EXP-011-dense-hardware-landscape-run/RESULT-REPORT.md).

## Built with Codex and GPT-5.6

Codex accelerated bounded implementation, tests, CI diagnosis, experiment packaging, visual
verification, and pull-request review under human-defined scientific gates. Gwri retained product,
scientific, hardware-authorization, interpretation, and merge authority. GPT-5.6 is an optional,
filtered explanation layer: it does not calculate results, and invalid or unavailable output fails
closed. **The AI can explain the experiment. It cannot rewrite the evidence.**

## Honest limits

Exact classical evaluation remains authoritative, and the project makes no quantum-advantage
claim. These deliberately small experiments do not demonstrate speedup, scalability,
generalisation, musical quality, musical truth, or commercial superiority. The application has no
audio and makes no live IBM call.

## Deeper research documentation

Start with the [Build Week judging guide](docs/build-week/JUDGING-GUIDE.md),
[Codex contribution log](docs/build-week/CODEX-CONTRIBUTION-LOG.md),
[Codex and GPT-5.6 evidence](docs/build-week/CODEX-AND-GPT56-EVIDENCE.md), and
[before and after](docs/build-week/BEFORE-AND-AFTER.md). Detailed experiments and developer
commands continue below.

### Research question

Given a small set of synthetic symbolic melodies and interpretable pairwise similarities, can a
two-family QUBO formulation recover known tune families, and how do local QAOA-style samples
compare with exact classical optima?

```mermaid
flowchart LR
  A["Folk-music problem"] --> B["Exact classical truth"]
  B --> C["Bounded quantum comparison"]
  C --> D["Governed hardware evidence"]
  D --> E["Validated explanation"]
```

### Developer quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
qfl doctor
qfl compare --seed 42
```

## EXP-001: Local Qiskit Circuit Infrastructure

EXP-001 is complete and validates local Qiskit circuit construction, transpilation, measurement, and finite-shot reporting with Aer simulation only. It requires optional quantum dependencies but no IBM account, no token, and no QPU access.

```powershell
py -3.13 -m venv .venv-qiskit
.\.venv-qiskit\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,quantum]"
qfl basics-list
qfl basics-run --experiment zero --shots 1024
qfl basics-run --experiment hadamard --shots 4096
qfl basics-run --experiment bell --shots 4096
```

The circuit-infrastructure commands fail clearly when Qiskit is not installed; they do not substitute classical pseudo-results.


## EXP-002: Max-Cut Reference

EXP-002 is complete and uses the four-node `cycle4` Max-Cut benchmark as a transparent reference problem. It compares exact enumeration, verified QUBO/Ising algebra, statevector expectation during QAOA parameter optimisation, and finite-shot sampling from a genuine local Qiskit circuit.

```powershell
qfl maxcut-list
qfl maxcut-exact --graph cycle4
qfl maxcut-qaoa --graph cycle4 --depth 1 --shots 4096
qfl maxcut-compare --graph cycle4 --depth 1 --shots 4096
```

The exact maximum cut is `4.0` with complementary optima `0101` and `1010`. The registered p=1 QAOA run samples an optimal bitstring, but its expected approximation ratio is about `0.75`; this distinction is deliberate. Brute force is superior for this tiny instance, and no quantum advantage is claimed.

## Experiments

| Experiment | Status | Purpose |
| --- | --- | --- |
| EXP-001 quantum basics | complete | local Qiskit circuit and measurement infrastructure |
| EXP-002 Max-Cut reference | complete | exact Max-Cut, verified QUBO/Ising mapping, and genuine local Qiskit QAOA |
| EXP-003 synthetic tune families | complete | deterministic labelled benchmark |
| EXP-004 QUBO family partition | complete | transparent two-family binary model |
| EXP-005A tune-family QAOA | complete | verified tune-family QUBO/Ising mapping and genuine local Qiskit p=1 QAOA |
| EXP-006 noise sensitivity | planned | local noise-model comparison |
| EXP-007A IBM smoke test | complete | one-job connectivity evidence with disclosed 256-shot deviation |
| EXP-008–009 real-data gates | complete | licence/provenance selection and rejection of weak formulations |
| EXP-010A–C compact hardware study | complete | exact compact encoding, fail-closed preparation, and controlled validation |
| EXP-010D landscape | complete | 25-cell IBM parameter-landscape support with retained warning |
| EXP-011 dense replication | complete | independent 81-cell IBM landscape replication with retained warning |

## Core Commands

```bash
qfl generate-synthetic --seed 42
qfl solve-exact --seed 42
qfl solve-qaoa --seed 42
qfl compare --seed 42
python scripts/check_public_safety.py
```

The existing `solve-qaoa` path is a deterministic classical fallback over QUBO energies and should not be interpreted as genuine Qiskit QAOA. EXP-005A adds separate `tune-family-*` commands for exact verification and genuine local Qiskit QAOA execution.

## Research Discipline

- Exact classical enumeration remains the ground truth for registered small fixtures.
- All basis states are checked for small benchmark instances before QAOA claims are interpreted.
- Expected energy and best sampled solution are reported separately.
- Classical fallback sampling must never be presented as genuine QAOA.
- Plans and implementations receive separate review before results are published.

## Responsible Scope

Music is used here as an interpretable sequence testbed. The repository does not imply that quantum computing automatically discovers deeper cultural patterns or currently outperforms classical methods. Future public-data work must pass licence, provenance, privacy, and cultural-context review before ingestion.

## Limitations

The learning fixture and exact 256 Reveal are deliberately small. Local ideal simulation does not
represent hardware noise, topology, drift, or readout error. The two governed IBM landscape jobs
provide bounded evidence for one frozen four-qubit structure, not general usefulness. Hardware
access remains absent from the app and disabled from ordinary test and documentation paths.

## Licence

MIT.
