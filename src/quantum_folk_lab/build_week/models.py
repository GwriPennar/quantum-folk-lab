"""Versioned, serialisable contracts for the Guided Experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

DEMO_STATE_SCHEMA = "qfl.build_week.demo_state.v1"
RESULT_ENVELOPE_SCHEMA = "qfl.build_week.result_envelope.v1"
EXPORT_FORMAT_VERSION = "qfl.build_week.export.v1"


class ExecutionClassification(StrEnum):
    CURRENT_EXACT = "current-exact-classical-computation"
    CURRENT_QISKIT = "current-local-qiskit-quick-run"
    HISTORICAL_QISKIT = "historical-registered-qiskit-evidence"
    DETERMINISTIC_EXPLANATION = "deterministic-explanation"
    GPT56_EXPLANATION = "gpt-5.6-explanation"
    UNAVAILABLE = "unavailable-optional-capability"


class LearnerLevel(StrEnum):
    FIRST_ENCOUNTER = "first_encounter"
    TECHNICAL_LEARNER = "technical_learner"
    RESEARCH_DETAIL = "research_detail"


@dataclass(frozen=True)
class DemoState:
    schema_version: str = DEMO_STATE_SCHEMA
    current_step: int = 1
    completed_steps: tuple[int, ...] = ()
    learner_level: LearnerLevel = LearnerLevel.FIRST_ENCOUNTER

    def __post_init__(self) -> None:
        if self.schema_version != DEMO_STATE_SCHEMA:
            raise ValueError("unsupported demo-state schema")
        if not 1 <= self.current_step <= 12:
            raise ValueError("current_step must be between 1 and 12")
        if any(step < 1 or step > 12 for step in self.completed_steps):
            raise ValueError("completed steps must be between 1 and 12")

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["learner_level"] = self.learner_level.value
        payload["completed_steps"] = list(self.completed_steps)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> DemoState:
        return cls(
            schema_version=str(payload["schema_version"]),
            current_step=int(payload["current_step"]),
            completed_steps=tuple(int(step) for step in payload.get("completed_steps", [])),
            learner_level=LearnerLevel(str(payload["learner_level"])),
        )


@dataclass(frozen=True)
class EvidencePair:
    left_tune: str
    right_tune: str
    interval_similarity: float
    contour_similarity: float
    rhythm_similarity: float
    combined_similarity: float
    graph_edge: bool

    def __post_init__(self) -> None:
        values = (
            self.interval_similarity,
            self.contour_similarity,
            self.rhythm_similarity,
            self.combined_similarity,
        )
        if any(value < 0.0 or value > 1.0 for value in values):
            raise ValueError("similarities must be between zero and one")


@dataclass(frozen=True)
class ResultEnvelope:
    schema_version: str
    run_identifier: str
    fixture_identifier: str
    fixture_description: str
    tune_ordering: tuple[str, ...]
    parameters: dict[str, float]
    bit_ordering_convention: str
    complement_canonicalisation_rule: str
    evidence_summary: dict[str, object]
    qubo_summary: dict[str, object]
    exact_result: dict[str, object]
    execution_classification: ExecutionClassification
    validation_state: dict[str, object]
    claims_boundary: tuple[str, ...]
    software_provenance: dict[str, str]
    export_format_version: str = EXPORT_FORMAT_VERSION
    explanations: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.schema_version != RESULT_ENVELOPE_SCHEMA:
            raise ValueError("unsupported result-envelope schema")
        if self.execution_classification is not ExecutionClassification.CURRENT_EXACT:
            raise ValueError("deterministic core emits only current exact computation")
        if len(self.tune_ordering) != 8 or len(set(self.tune_ordering)) != 8:
            raise ValueError("the registered fixture must contain eight ordered tunes")
        if not bool(self.validation_state.get("passed")):
            raise ValueError("result envelope requires passed validation")
        optima = self.exact_result.get("optimal_assignments")
        if not isinstance(optima, list) or not optima:
            raise ValueError("exact result must contain optimal assignments")

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["execution_classification"] = self.execution_classification.value
        payload["tune_ordering"] = list(self.tune_ordering)
        payload["claims_boundary"] = list(self.claims_boundary)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ResultEnvelope:
        return cls(
            schema_version=str(payload["schema_version"]),
            run_identifier=str(payload["run_identifier"]),
            fixture_identifier=str(payload["fixture_identifier"]),
            fixture_description=str(payload["fixture_description"]),
            tune_ordering=tuple(str(item) for item in payload["tune_ordering"]),
            parameters={str(k): float(v) for k, v in dict(payload["parameters"]).items()},
            bit_ordering_convention=str(payload["bit_ordering_convention"]),
            complement_canonicalisation_rule=str(payload["complement_canonicalisation_rule"]),
            evidence_summary=dict(payload["evidence_summary"]),
            qubo_summary=dict(payload["qubo_summary"]),
            exact_result=dict(payload["exact_result"]),
            execution_classification=ExecutionClassification(
                str(payload["execution_classification"])
            ),
            validation_state=dict(payload["validation_state"]),
            claims_boundary=tuple(str(item) for item in payload["claims_boundary"]),
            software_provenance={
                str(k): str(v) for k, v in dict(payload["software_provenance"]).items()
            },
            export_format_version=str(payload.get("export_format_version", EXPORT_FORMAT_VERSION)),
            explanations={str(k): str(v) for k, v in dict(payload.get("explanations", {})).items()},
        )
