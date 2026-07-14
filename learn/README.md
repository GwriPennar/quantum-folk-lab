# learn/ — Portable Foundations lessons

Public experimental Learning Console content for Quantum Folk Lab.

## Contents

| Path | Role |
|------|------|
| `registry.yaml` | Canonical lesson order, routes, IDs |
| `glossary.yaml` | Shared terminology |
| `lessons/*.md` | Portable Markdown + YAML front matter |
| `schemas/lesson.schema.json` | Front-matter schema |
| `diagrams/source/` | Mermaid source files (optional reference) |

## Lessons

1. Bits and qubits
2. Gates and measurement
3. Hadamard and interference
4. Entanglement
5. What is an optimisation problem?

## Authoring

See [`dev/learning/CONTRIBUTING-LESSONS.md`](../dev/learning/CONTRIBUTING-LESSONS.md).

## Runtime

Python package: `quantum_folk_lab.learning`  
Streamlit app: `apps/learning_console/`

This tree must remain usable from a clean clone with no access to ignored `private/` directories.
