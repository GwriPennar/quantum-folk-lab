"""Streamlit-independent façade for the public Guided Experiment."""

from __future__ import annotations

import json
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from quantum_folk_lab.build_week import (
    ExactLandscape,
    LearnerLevel,
    RegisteredQAOAEvidence,
    ResultEnvelope,
    build_exact_landscape,
    export_json,
    export_markdown,
    parse_registered_qaoa_evidence,
    quantum_capability,
    run_guided_exact,
    run_quick_qiskit,
)
from quantum_folk_lab.build_week.quantum import QuantumCapability


@dataclass(frozen=True)
class GuidedExperimentView:
    result: ResultEnvelope
    quantum: QuantumCapability
    landscape: ExactLandscape
    registered_qaoa: RegisteredQAOAEvidence
    registered_measurements: tuple[RegisteredMeasurement, ...]
    registered_distinct_state_count: int

    def explanation(self, level: LearnerLevel) -> str:
        return self.result.explanations[level.value]

    def json_export(self) -> bytes:
        return export_json(self.result).encode("utf-8")

    def markdown_export(self, level: LearnerLevel) -> bytes:
        return export_markdown(self.result, level).encode("utf-8")


@dataclass(frozen=True)
class RegisteredMeasurement:
    """One display-safe row from the registered simulated measurement counts."""

    bitstring: str
    count: int
    is_exact_optimum: bool

    def chart_row(self) -> dict[str, object]:
        status = "Exact optimum" if self.is_exact_optimum else "Other grouping"
        return {
            "bitstring": self.bitstring,
            "count": self.count,
            "status": status,
            "optimum_note": "EXACT OPTIMUM" if self.is_exact_optimum else "",
            "zero": 0,
        }


def top_registered_measurements(
    measurement_counts: Mapping[str, Any],
    exact_optima: Collection[str],
    *,
    limit: int = 10,
) -> tuple[RegisteredMeasurement, ...]:
    """Return a stable, non-mutating top-count view of registered evidence."""

    if limit < 1:
        raise ValueError("limit must be positive")
    optimum_set = set(exact_optima)
    ranked = sorted(
        ((str(bitstring), int(count)) for bitstring, count in measurement_counts.items()),
        key=lambda item: (-item[1], item[0]),
    )
    return tuple(
        RegisteredMeasurement(
            bitstring=bitstring,
            count=count,
            is_exact_optimum=bitstring in optimum_set,
        )
        for bitstring, count in ranked[:limit]
    )


def load_guided_experiment() -> GuidedExperimentView:
    root = Path(__file__).resolve().parents[3]
    registered_path = (
        root / "experiments" / "EXP-005A-tune-family-qaoa" / "results" / "tune-family-qaoa-p1.json"
    )
    registered_payload = json.loads(registered_path.read_text(encoding="utf-8"))
    measurement_counts = dict(registered_payload["measurement_counts"])
    exact_optima = tuple(
        str(value) for value in registered_payload["exact"]["exact_optimal_bitstrings"]
    )
    return GuidedExperimentView(
        result=run_guided_exact(),
        quantum=quantum_capability(),
        landscape=build_exact_landscape(),
        registered_qaoa=parse_registered_qaoa_evidence(registered_payload),
        registered_measurements=top_registered_measurements(measurement_counts, exact_optima),
        registered_distinct_state_count=len(measurement_counts),
    )


def execute_quick_qiskit() -> dict[str, object]:
    return run_quick_qiskit()
