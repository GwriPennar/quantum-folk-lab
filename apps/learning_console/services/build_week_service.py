"""Streamlit-independent façade for the public Guided Experiment."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

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

    def explanation(self, level: LearnerLevel) -> str:
        return self.result.explanations[level.value]

    def json_export(self) -> bytes:
        return export_json(self.result).encode("utf-8")

    def markdown_export(self, level: LearnerLevel) -> bytes:
        return export_markdown(self.result, level).encode("utf-8")


def load_guided_experiment() -> GuidedExperimentView:
    root = Path(__file__).resolve().parents[3]
    registered_path = (
        root / "experiments" / "EXP-005A-tune-family-qaoa" / "results" / "tune-family-qaoa-p1.json"
    )
    registered_payload = json.loads(registered_path.read_text(encoding="utf-8"))
    return GuidedExperimentView(
        result=run_guided_exact(),
        quantum=quantum_capability(),
        landscape=build_exact_landscape(),
        registered_qaoa=parse_registered_qaoa_evidence(registered_payload),
    )


def execute_quick_qiskit() -> dict[str, object]:
    return run_quick_qiskit()
