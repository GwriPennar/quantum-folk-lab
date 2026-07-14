---
id: guided.foundations.entanglement
version: 1
title: Entanglement
mode: guided
section: Foundations
order: 4
route: learn/entanglement
estimated_minutes: 6
status: active
legacy_progress_key: entanglement
foundations_nav: true
prerequisites:
  - guided.foundations.hadamard
next_lesson: guided.foundations.optimisation
learning_objectives:
  - Explain Bell-state correlations
  - Distinguish individual randomness from joint correlation
glossary_terms:
  - entanglement
  - circuit
visuals:
  - bell-correlation
interactions: []
check_question: In a Bell state, which joint outcomes appear?
learned_summary: Entangled qubits show correlated outcomes even when each bit alone looks random.
completion:
  type: view_and_reflect
  legacy_key: entanglement
semantic:
  required_markers:
    - Bell state
    - Individual uncertainty
    - Pairwise correlation
    - 00 and 11 outcomes
    - No faster-than-light communication
  forbidden_markers:
    - Eight-tune synthetic problem
    - registered result JSON
---

# Entanglement

## Bell state circuit

A **Bell state** prepares two qubits so their joint outcomes are correlated.

```mermaid
flowchart TB
  A["Start |00⟩"] --> B["Apply H on qubit 0"]
  B --> C["Apply CNOT"]
  C --> D["Measure both qubits"]
```

:::visual
id: bell-correlation
:::

## Individual uncertainty

Each qubit alone looks **individually uncertain** — you might see 0 or 1 with equal probability.

## Pairwise correlation

The two results are **pairwise correlated**. In the Bell state you will see **00 and 11 outcomes**, not 01 or 10.

## No faster-than-light communication

Entanglement does **not** allow faster-than-light communication. You cannot control which correlated outcome appears.

When you are ready for hands-on practice, see the public EXP-001 quantum fundamentals experiment in this repository.

:::disclosure
id: optional-notation
label: Show the notation
level: intermediate
:::
