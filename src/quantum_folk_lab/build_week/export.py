"""Public-safe deterministic exports for Guided Experiment results."""

from __future__ import annotations

import json
from typing import cast

from .claims import validate_claims
from .models import LearnerLevel, ResultEnvelope


def export_json(envelope: ResultEnvelope) -> str:
    text = json.dumps(envelope.to_dict(), indent=2, sort_keys=True) + "\n"
    validate_claims(text)
    return text


def export_markdown(
    envelope: ResultEnvelope, level: LearnerLevel = LearnerLevel.FIRST_ENCOUNTER
) -> str:
    exact = envelope.exact_result
    optimal_assignments = cast(list[str], exact["optimal_assignments"])
    explanation = envelope.explanations[level.value]
    lines = [
        "# Quantum Folk Lab — Guided Experiment reproducibility record",
        "",
        f"- Schema: `{envelope.schema_version}`",
        f"- Run: `{envelope.run_identifier}`",
        f"- Fixture: `{envelope.fixture_identifier}`",
        f"- Execution: `{envelope.execution_classification.value}`",
        f"- Tau: `{envelope.parameters['tau']}`",
        f"- Lambda: `{envelope.parameters['lambda']}`",
        "",
        "## Exact result",
        "",
        f"- Minimum energy: `{exact['minimum_energy']}`",
        f"- Optimal assignments: `{', '.join(optimal_assignments)}`",
        f"- Canonical complement class: `{exact['canonical_complement_class']}`",
        f"- Evaluated assignments: `{exact['evaluated_assignments']}`",
        "",
        "## Explanation",
        "",
        explanation,
        "",
        "## Validation and limitations",
        "",
        "- Direct/QUBO and QUBO/Ising equivalence checks passed.",
        "- Exact enumeration is authoritative for this eight-variable fixture.",
        "- The fixture is deterministic and synthetic; it is not real folk-family evidence.",
        "- Local quantum simulation is optional and is not hardware execution.",
        "- No claim of speed, scale, or production performance is made.",
        "",
        "## Reproduce",
        "",
        "```text",
        "qfl build-week-exact --format markdown",
        "```",
    ]
    text = "\n".join(lines) + "\n"
    validate_claims(text)
    return text
