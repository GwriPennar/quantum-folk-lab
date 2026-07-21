---
id: guided.foundations.bits_qubits
version: 2
title: Bits and qubits
mode: guided
section: Foundations
order: 1
route: learn/bits-and-qubits
estimated_minutes: 5
status: active
legacy_progress_key: bits_qubits
foundations_nav: true
next_lesson: guided.foundations.gates
learning_objectives:
  - Distinguish classical bits from qubits before measurement
  - Explain why measurement yields classical outcomes
glossary_terms:
  - bit
  - qubit
  - measurement
visuals:
  - bit-vs-qubit
interactions: []
check_question: What is the difference between a classical bit and a qubit before measurement?
learned_summary: A classical bit is definitely 0 or 1. A qubit is described by amplitudes until measurement.
completion:
  type: view_and_reflect
  legacy_key: bits_qubits
semantic:
  required_markers:
    - Bit versus qubit
    - Measurement produces a classical result
  forbidden_markers:
    - Input state for X gate
    - Technical metadata
---

# Bits and qubits

## Bit versus qubit

A **classical bit** is definitely 0 or 1. A **qubit** is described by amplitudes until you measure it.

Rather than picturing a qubit as simply "both 0 and 1 at the same time", think of it as a state described by amplitudes. Those amplitudes carry probability and phase information, and measurement produces one classical outcome.

```mermaid
flowchart LR
  A["Classical bit"] --> B["Definitely 0 or 1"]
  C["Qubit before measurement"] --> D["Amplitudes alpha, beta"]
  D --> E["Measurement"]
  E --> F["Classical 0 or 1"]
```

:::visual
id: bit-vs-qubit
:::

## Measurement

When you measure, you always get a classical 0 or 1. The probabilities are given by |α|² and |β|².

**What this means:** Before measurement, the qubit is described by amplitudes. Measurement produces a classical result.

:::disclosure
id: optional-notation
label: Show the notation
level: intermediate
:::
