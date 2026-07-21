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

VARIANT_DISPLAY_NAMES = (
    "Afon · original phrase",
    "Bryn · shifted phrase",
    "Celyn · one-note change",
    "Daran · rhythm change",
    "Eira · original phrase",
    "Ffion · shifted phrase",
    "Glyn · inserted note",
    "Haf · shortened phrase",
)


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


@dataclass(frozen=True)
class PartitionView:
    bitstring: str
    first_group: tuple[str, ...]
    second_group: tuple[str, ...]


@dataclass(frozen=True)
class QuickQiskitSummary:
    shots: int
    distinct_states: int
    most_frequent_state: str
    most_frequent_count: int
    most_frequent_is_optimum: bool
    optimum_count: int
    optimum_probability: float
    top_states: tuple[RegisteredMeasurement, ...]


def partition_from_indices(indices: Collection[int]) -> PartitionView:
    """Translate one balanced learner choice into stable labels and a bitstring."""

    selected = set(indices)
    if len(selected) != 4 or any(
        index < 0 or index >= len(VARIANT_DISPLAY_NAMES) for index in selected
    ):
        raise ValueError("choose exactly four distinct variants")
    bitstring = "".join("1" if index in selected else "0" for index in range(8))
    return PartitionView(
        bitstring=bitstring,
        first_group=tuple(VARIANT_DISPLAY_NAMES[index] for index in sorted(selected)),
        second_group=tuple(
            name for index, name in enumerate(VARIANT_DISPLAY_NAMES) if index not in selected
        ),
    )


def partitions_are_equivalent(candidate: str, reference: str) -> bool:
    """Compare unlabeled two-family partitions, accepting a global complement."""

    if len(candidate) != len(reference) or set(candidate + reference) - {"0", "1"}:
        return False
    complement = "".join("1" if bit == "0" else "0" for bit in reference)
    return candidate in {reference, complement}


def summarise_quick_qiskit(payload: Mapping[str, Any]) -> QuickQiskitSummary:
    """Validate and reduce a live local result without changing its scientific values."""

    raw_counts = payload.get("measurement_counts")
    if not isinstance(raw_counts, Mapping) or not raw_counts:
        raise ValueError("local result did not contain measurement counts")
    counts = {str(state): int(count) for state, count in raw_counts.items()}
    if any(len(state) != 8 or set(state) - {"0", "1"} for state in counts):
        raise ValueError("local result contained an invalid state label")
    if any(count < 0 for count in counts.values()):
        raise ValueError("local result contained a negative count")
    shots = int(payload.get("shots", sum(counts.values())))
    if shots < 1 or sum(counts.values()) != shots:
        raise ValueError("local measurement counts do not match the shot total")
    optima = {"00001111", "11110000"}
    ranked = top_registered_measurements(counts, optima, limit=min(10, len(counts)))
    most_frequent = ranked[0]
    optimum_count = sum(counts.get(state, 0) for state in optima)
    return QuickQiskitSummary(
        shots=shots,
        distinct_states=len(counts),
        most_frequent_state=most_frequent.bitstring,
        most_frequent_count=most_frequent.count,
        most_frequent_is_optimum=most_frequent.is_exact_optimum,
        optimum_count=optimum_count,
        optimum_probability=optimum_count / shots,
        top_states=ranked,
    )


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
