# Quantum Folk Lab

Quantum Folk Lab is a reproducible research repository investigating QUBO, Ising and QAOA formulations for tune-family inference and related computational-musicology optimisation problems.

The repository develops controlled synthetic benchmarks, exact classical validation, QUBO-to-Ising verification, and local Qiskit QAOA reference experiments. It makes no claim of quantum advantage, production readiness, or real-corpus tune-family discovery. Current tune-family work uses only deterministic synthetic melodies: no private corpora, no real tune collections, and no credentials are included.

## Research Question

Given a small set of synthetic symbolic melodies and interpretable pairwise similarities, can a two-family QUBO formulation recover known tune families, and how do local QAOA-style samples compare with exact classical optima?

```mermaid
flowchart LR
  A["Local Qiskit circuit infrastructure"] --> B["Reference optimisation benchmarks"]
  B --> C["Synthetic melody families"]
  C --> D["Interval, contour, rhythm similarity"]
  D --> E["Sparse weighted graph"]
  E --> F["Two-family QUBO"]
  F --> G["Exact classical solver"]
  F --> H["Verified local QAOA"]
  G --> I["Evaluation"]
  H --> I
```

## Quick Start

PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
qfl doctor
qfl compare --seed 42
```

Bash:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
qfl doctor
qfl compare --seed 42
```

## OpenAI Build Week 2026

Quantum Folk Lab now offers a guided Education journey from synthetic musical evidence to a
verified exact partition, optional local-Qiskit comparison, grounded optional GPT-5.6 Sol
explanation, and reproducibility export.

- **Before Build Week:** the public Foundations console and registered research experiments
  already existed at commit `281ba40`.
- **Built during Build Week:** the validated exact-first service and Guided Experiment were added
  after governing-plan commit `3950a1f`.

```powershell
python -m pip install -e ".[learning]"
streamlit run apps/learning_console/app.py
```

The complete journey needs neither Qiskit nor an OpenAI credential. Optional capabilities use
`.[quantum]` and `.[ai]`. See the [Build Week judging guide](docs/build-week/JUDGING-GUIDE.md).
Exact enumeration remains authoritative; no quantum advantage is claimed.

### Built with Codex and GPT-5.6

Codex accelerated repository inspection, bounded implementation, test construction, runtime
verification, CI diagnosis, visual review, and PR preparation across the deterministic exact-first
core, Guided Experiment, validated GPT-5.6 boundary, and in-app 256 Reveal. Gwri retained and
approved the governing product, engineering, and scientific decisions: Education positioning, the
fixed synthetic fixture, exact enumeration as authority, separation of exact truth from registered
QAOA and the live quick run, no hardware or advantage claim, optional GPT-5.6 with deterministic
fallback, rejection or deferral of unsafe scope, and every final merge.

GPT-5.6 optionally explains validated results at different learner levels; deterministic code
calculates the result. Its input is filtered, and output is schema-, grounding-, number-, and
claim-checked. It cannot alter registered values, and invalid or unavailable output fails closed to
the deterministic explanation. **The AI can explain the experiment. It cannot rewrite the
evidence.**

Evidence: [Codex contribution log](docs/build-week/CODEX-CONTRIBUTION-LOG.md),
[Codex and GPT-5.6 evidence](docs/build-week/CODEX-AND-GPT56-EVIDENCE.md),
[before and after](docs/build-week/BEFORE-AND-AFTER.md), and
[judging guide](docs/build-week/JUDGING-GUIDE.md).

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
| EXP-007 IBM hardware | optional | dry-run first, explicit QPU confirmation required |

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

EXP-001 uses ideal local simulation. Ideal simulator results do not represent real hardware noise, queueing, topology, calibration drift, or readout error. IBM Quantum hardware support is deliberately optional and disabled by default.

## Licence

MIT.
