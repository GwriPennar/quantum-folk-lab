---
id: guided.foundations.optimisation
version: 1
title: What is an optimisation problem?
mode: guided
section: Foundations
order: 5
route: learn/optimisation-intro
estimated_minutes: 5
status: active
legacy_progress_key: optimisation
foundations_nav: true
prerequisites:
  - guided.foundations.entanglement
learning_objectives:
  - Define candidate solutions, objectives and constraints
  - Connect everyday optimisation to Max-Cut without quantum claims
glossary_terms:
  - objective
  - constraint
  - exact solution
  - QUBO
  - Ising
  - QAOA
visuals: []
interactions: []
check_question: What is an objective score?
learned_summary: An optimisation problem assigns a score to each choice; we seek the best score.
completion:
  type: view_and_reflect
  legacy_key: optimisation
semantic:
  required_markers:
    - Candidate solutions
    - Objective or score
    - Constraints
    - Best solution
    - Bridge toward Max-Cut
  forbidden_markers:
    - quantum advantage
    - registered result JSON
---

# What is an optimisation problem?

## Candidate solutions

An optimisation problem starts with **candidate solutions** — the choices you could make.

## Objective or score

Each candidate gets an **objective or score**. Higher or lower might be better depending on the problem.

## Constraints

**Constraints** rule out candidates that are not allowed. Only feasible candidates compete for the best score.

## Best solution

The **best solution** is the feasible candidate with the optimal score. On small problems we can try every option (brute force / exact search).

## Everyday example

Choosing a route with the shortest travel time: routes are candidates, time is the objective, road closures are constraints.

```mermaid
flowchart LR
  A["Candidates"] --> B["Score each"]
  B --> C["Apply constraints"]
  C --> D["Pick best"]
```

## Bridge toward Max-Cut

Later you will see **Max-Cut** — split graph nodes into two groups to maximise edges crossing between groups. That is an optimisation problem, not a quantum claim at this stage.

No quantum hardware is needed to understand the setup at this stage.

:::disclosure
id: optional-maths
label: Why exact-first matters
level: intermediate
body: For two binary choices, list `00`, `01`, `10` and `11`, score each, discard any invalid choices and select the best score. Complete enumeration is practical here and gives a reference for judging a heuristic.
:::
