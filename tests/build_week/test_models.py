from __future__ import annotations

import pytest

from quantum_folk_lab.build_week.models import (
    DEMO_STATE_SCHEMA,
    RESULT_ENVELOPE_SCHEMA,
    DemoState,
    ExecutionClassification,
    LearnerLevel,
    ResultEnvelope,
)
from quantum_folk_lab.build_week.workflow import run_guided_exact


def test_demo_state_round_trip_and_validation() -> None:
    state = DemoState(
        current_step=4,
        completed_steps=(1, 2, 3),
        learner_level=LearnerLevel.TECHNICAL_LEARNER,
    )
    assert state.schema_version == DEMO_STATE_SCHEMA
    assert DemoState.from_dict(state.to_dict()) == state
    with pytest.raises(ValueError):
        DemoState(current_step=13)


def test_result_envelope_round_trip() -> None:
    envelope = run_guided_exact()
    assert envelope.schema_version == RESULT_ENVELOPE_SCHEMA
    assert envelope.execution_classification is ExecutionClassification.CURRENT_EXACT
    assert ResultEnvelope.from_dict(envelope.to_dict()) == envelope


def test_invalid_result_schema_rejected() -> None:
    payload = run_guided_exact().to_dict()
    payload["schema_version"] = "unknown"
    with pytest.raises(ValueError):
        ResultEnvelope.from_dict(payload)
