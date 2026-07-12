"""Optional EXP-001 Hadamard demo using public quantum_folk_lab APIs."""

from __future__ import annotations

from typing import Any


def run_hadamard(*, shots: int = 1024) -> dict[str, Any]:
    from quantum_folk_lab.simulation import run_basics_experiment

    result = run_basics_experiment("hadamard", shots, 42, 42)
    payload = result.to_dict() if hasattr(result, "to_dict") else dict(result)
    return {
        "experiment": "hadamard",
        "shots": shots,
        "empirical_probabilities": payload.get("empirical_probabilities")
        or payload.get("probabilities"),
        "note": "Finite-shot Samples approximate Theory; sampling noise is expected.",
    }
