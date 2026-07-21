---
id: guided.foundations.hadamard
version: 2
title: Hadamard and interference
mode: guided
section: Foundations
order: 3
route: learn/hadamard
estimated_minutes: 6
status: active
legacy_progress_key: superposition_interference
foundations_nav: true
prerequisites:
  - guided.foundations.gates
next_lesson: guided.foundations.entanglement
learning_objectives:
  - Explain equal measurement probabilities after H
  - Distinguish Theory from Samples
  - Describe double-H interference
glossary_terms:
  - amplitude
  - probability
  - phase
  - interference
  - shot
  - sample
visuals:
  - hadamard-probability-split
  - z-phase-reveal
  - double-h-interference
interactions:
  - quantum-prediction
check_question: Why does H then H return to |0⟩?
learned_summary: Amplitudes can add or cancel through interference.
completion:
  type: prediction_and_result
  legacy_key: superposition_interference
semantic:
  required_markers:
    - Hadamard probability split
    - Theory
    - Samples
    - Double-H interference
  forbidden_markers:
    - Input state for X gate
    - Eight-tune synthetic problem
---

# Hadamard and interference

The **Hadamard** gate changes a definite starting state into a quantum state with equal measurement probabilities.

```mermaid
flowchart LR
  A["Start in |0⟩"] --> B["Apply H"]
  B --> C["P(0) = 50% theory"]
  B --> D["P(1) = 50% theory"]
```

## Hadamard probability split

:::visual
id: hadamard-probability-split
:::

Equal probabilities do not reveal all of the phase information in the state. Compare **Theory** with **Samples** when you run the circuit.

:::interaction
id: quantum-prediction
experiment: hadamard
shots_default: 4096
:::

## Why a second Hadamard matters

Amplitudes can reinforce and cancel. The second Hadamard is not merely another random split.

:::visual
id: z-phase-reveal
:::

## Double-H interference

:::visual
id: double-h-interference
:::

:::disclosure
id: optional-maths
label: Why phase matters
level: intermediate
body: Probabilities use squared amplitude magnitudes, so two states can look identical when measured immediately yet interfere differently after another gate. Relative phase controls whether amplitudes reinforce or cancel.
:::

Static export note: the prediction interaction is available in the public Learning Console app; exported HTML explains the activity without claiming live widgets.
