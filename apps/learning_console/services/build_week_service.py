"""Streamlit-independent façade for the public Guided Experiment."""

from __future__ import annotations

from dataclasses import dataclass

from quantum_folk_lab.build_week import (
    LearnerLevel,
    ResultEnvelope,
    export_json,
    export_markdown,
    quantum_capability,
    run_guided_exact,
    run_quick_qiskit,
)
from quantum_folk_lab.build_week.quantum import QuantumCapability


@dataclass(frozen=True)
class GuidedExperimentView:
    result: ResultEnvelope
    quantum: QuantumCapability

    def explanation(self, level: LearnerLevel) -> str:
        return self.result.explanations[level.value]

    def json_export(self) -> bytes:
        return export_json(self.result).encode("utf-8")

    def markdown_export(self, level: LearnerLevel) -> bytes:
        return export_markdown(self.result, level).encode("utf-8")


def load_guided_experiment() -> GuidedExperimentView:
    return GuidedExperimentView(run_guided_exact(), quantum_capability())


def execute_quick_qiskit() -> dict[str, object]:
    return run_quick_qiskit()
