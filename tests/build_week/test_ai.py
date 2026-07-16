from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

from quantum_folk_lab.build_week.ai import (
    DEFAULT_OPENAI_MODEL,
    explain_result,
    selected_model,
)
from quantum_folk_lab.build_week.models import LearnerLevel
from quantum_folk_lab.build_week.workflow import run_guided_exact


class FakeResponses:
    def __init__(self, output: str) -> None:
        self.output = output
        self.request: dict[str, Any] = {}

    def create(self, **kwargs: Any) -> SimpleNamespace:
        self.request = kwargs
        return SimpleNamespace(output_text=self.output)


def valid_output() -> str:
    return json.dumps(
        {
            "title": "A synthetic tune-family result",
            "summary": "The canonical exact split is 00001111.",
            "musical_question": "Eight synthetic variants are divided into two unlabeled groups.",
            "what_the_model_did": "It checked 256 assignments using fixed evidence.",
            "what_the_exact_result_means": "00001111 and its complement are equivalent.",
            "quantum_comparison": "A local simulation can be compared separately.",
            "limitations": "This fixture is synthetic and exact enumeration is authoritative.",
            "next_learning_step": "Inspect the interval, contour, and rhythm evidence.",
            "grounded_fields": [
                "fixture_identifier",
                "exact_result.canonical_complement_class",
            ],
        }
    )


def test_default_and_override_model() -> None:
    assert selected_model({}) == DEFAULT_OPENAI_MODEL == "gpt-5.6-sol"
    assert selected_model({"QFL_OPENAI_MODEL": "gpt-test"}) == "gpt-test"


def test_no_key_uses_deterministic_fallback() -> None:
    result = explain_result(run_guided_exact(), LearnerLevel.FIRST_ENCOUNTER, environment={})
    assert result.source == "deterministic"
    assert result.fallback_reason == "the OpenAI credential is not configured"


def test_valid_structured_response_is_grounded() -> None:
    fake = SimpleNamespace(responses=FakeResponses(valid_output()))
    result = explain_result(
        run_guided_exact(), LearnerLevel.TECHNICAL_LEARNER, client=fake, environment={}
    )
    assert result.source == "gpt-5.6"
    assert "00001111" in result.text
    assert fake.responses.request["model"] == "gpt-5.6-sol"
    sent = json.loads(fake.responses.request["input"])
    assert "environment" not in sent
    assert "OPENAI_" + "API" + "_KEY" not in fake.responses.request["input"]
    assert fake.responses.request["text"]["format"]["strict"] is True


def test_invalid_outputs_fail_closed() -> None:
    envelope = run_guided_exact()
    cases = [
        "not-json",
        json.dumps({"title": "missing fields"}),
        valid_output().replace("fixture_identifier", "invented.field"),
        valid_output().replace("This fixture is synthetic", "Quantum advantage is proven"),
        valid_output().replace("00001111", "99999999"),
    ]
    for raw in cases:
        fake = SimpleNamespace(responses=FakeResponses(raw))
        result = explain_result(envelope, LearnerLevel.RESEARCH_DETAIL, client=fake, environment={})
        assert result.source == "deterministic"
        assert result.fallback_reason
