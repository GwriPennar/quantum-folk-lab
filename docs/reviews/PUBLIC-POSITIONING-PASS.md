# Public Positioning Pass

## Purpose

This pass reframes public repository wording around reproducible quantum optimisation research rather than personal learning, tutorial, toy, or beginner-project language. It does not change mathematical formulations, experiment results, thresholds, code behaviour, tests, or scientific conclusions.

Adopted positioning:

> Quantum Folk Lab is a reproducible research repository investigating QUBO, Ising and QAOA formulations for tune-family inference and related computational-musicology optimisation problems.

## Files Reviewed

- `README.md`
- `pyproject.toml`
- `CITATION.cff`
- `CONTRIBUTING.md`
- `.github/` issue templates and CI workflow
- public documentation under `docs/`
- experiment README and result summaries under `experiments/`
- notebook README and notebook JSON files
- public source docstrings and CLI-facing strings under `src/`
- public tests and scripts

## Phrases Removed Or Reframed

| Previous wording category | Action | Replacement positioning |
| --- | --- | --- |
| `learning and research repository` / `learning and research sandbox` | Reframed in README and package metadata | reproducible quantum optimisation research repository |
| `learning path` / `Learning Roadmap` | Reframed in architecture and roadmap docs | research platform / research roadmap |
| EXP-001 as a `learning experiment` | Reframed in experiment documentation | local Qiskit/Aer reference experiment and circuit-infrastructure validation |
| `Learning Goals` | Reframed in EXP-001 | validation goals |
| `educational` circuit or validation language | Reframed where not part of historical audit wording | bounded reference benchmark / controlled local-simulation validation |
| `learning step` in later experiment stubs | Reframed | bounded research step |
| notebook `learning companions` | Reframed | reproducibility companions |
| `sandbox` in package metadata and architecture | Reframed | research repository / research platform |
| `demonstrates` in public limitation strings | Reframed where safe | validates |

## Limitations Retained

The pass intentionally preserved or strengthened these limitations:

- no quantum-advantage claim;
- no production-readiness claim;
- synthetic tune-family fixtures only;
- no public private or copyrighted tune corpus;
- no IBM Runtime or hardware requirement for current local work;
- brute force is superior for the registered small fixtures;
- exact classical enumeration remains ground truth;
- expected energy and sampled best solution remain separate;
- classical fallback sampling must not be presented as genuine QAOA.

## Historical Or Technical Wording Retained

The remaining targeted-term search hits are intentional:

- `example` in `CONTRIBUTING.md`, EXP-005A plans, and review files is technical language for representative synthetic cases, worked bitstring decoding, or historical review-table entries.
- `docs/learning-roadmap.md` remains as a path reference in historical review files. The file content now presents itself as a research roadmap, but the path is retained for link stability.
- Historical review recommendations and chronology were not rewritten when doing so would obscure the audit trail.

## GitHub Metadata

Suggested repository description:

> Reproducible quantum optimisation research for tune-family inference using QUBO, Ising models and local Qiskit QAOA.

Suggested topics:

- `quantum-computing`
- `qiskit`
- `qaoa`
- `qubo`
- `ising-model`
- `quantum-optimization`
- `computational-musicology`
- `music-information-retrieval`
- `reproducible-research`
- `python`

## Validation Results

- `python -m pytest -m "not quantum"`: `18 passed, 15 deselected`
- `python -m ruff check .`: passed
- `python -m ruff format --check .`: passed after formatting the touched `quantum_basics.py` string layout
- `python scripts/check_public_safety.py`: passed
- `python -m mypy`: failed with the known optional-Qiskit missing-stub and unused-ignore pattern in `quantum_basics.py`, `maxcut_ising.py`, `simulation.py`, `qubo/qiskit_adapter.py`, and `maxcut_qaoa.py`

The `mypy` issue is pre-existing and unrelated to this wording-only pass. No unrelated quantum code was modified to address it.

## Implementation Boundary

No EXP-005A implementation was started. No QUBO, Ising, QAOA, CLI behaviour, notebook computation, result-generation logic, dependency semantics, test expectation, mathematical formulation, or experiment result was changed.
