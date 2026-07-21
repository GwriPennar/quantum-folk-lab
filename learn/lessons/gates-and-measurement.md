---
id: guided.foundations.gates
version: 1
title: Gates and measurement
mode: guided
section: Foundations
order: 2
route: learn/gates-and-measurement
estimated_minutes: 6
status: active
legacy_progress_key: gates_measurement
foundations_nav: true
prerequisites:
  - guided.foundations.bits_qubits
next_lesson: guided.foundations.hadamard
learning_objectives:
  - Describe what a gate does to qubit amplitudes
  - Explain measurement after a gate operation
glossary_terms:
  - gate
  - circuit
  - measurement
visuals:
  - circuit-thumbnail
  - ideal-vs-noisy
interactions:
  - x-gate-input
check_question: What does the X gate do to |0⟩?
learned_summary: Gates change amplitudes; measurement samples a classical 0 or 1.
completion:
  type: view_and_reflect
  legacy_key: gates_measurement
semantic:
  required_markers:
    - X gate
    - Before, operation, after
    - Measurement produces a classical result
  forbidden_markers:
    - Eight-tune synthetic problem
    - registered result JSON
---

# Gates and measurement

## X gate

The **X gate** is quantum NOT — it swaps |0⟩ and |1⟩ amplitudes.

```mermaid
flowchart LR
  A["Before"] --> B["Apply X gate"]
  B --> C["After"]
  C --> D["Measure"]
  D --> E["Classical 0 or 1"]
```

:::visual
id: circuit-thumbnail
:::

:::visual
id: x-gate-visual
:::

:::interaction
id: x-gate-input
:::

## Before, operation, after

Think in three steps: **before** the gate (input state), **operation** (the gate changes amplitudes), **after** (new amplitudes, still quantum until measurement).

## Measurement

Gates are reversible on amplitudes. **Measurement** is different — it produces one classical outcome with probabilities from the current amplitudes.

**What this means:** Before measurement, the qubit is described by amplitudes. Measurement produces a classical result.

:::disclosure
id: optional-notation
label: Why measurement matters
level: intermediate
body: A gate changes amplitudes predictably, but measurement samples one classical outcome. Repeating the same preparation and measurement is how we estimate the underlying probabilities.
:::

## Ideal simulation and physical hardware

An ideal simulator applies the circuit without device errors. Physical qubits, gates and measurements are imperfect; **noise** is the collective name for those errors and disturbances. Noise can blur or reorder a result, but disagreement alone does not identify one cause.

:::visual
id: ideal-vs-noisy
:::

**What this means:** Hardware evidence must be judged against exact truth. This is comparison evidence, not an advantage claim.
