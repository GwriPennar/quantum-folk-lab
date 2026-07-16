from __future__ import annotations

import json

import pytest

from quantum_folk_lab.build_week.claims import claim_violations, validate_claims
from quantum_folk_lab.build_week.export import export_json, export_markdown
from quantum_folk_lab.build_week.models import LearnerLevel
from quantum_folk_lab.build_week.workflow import run_guided_exact
from quantum_folk_lab.tune_family import EXPECTED_OPTIMA, EXPECTED_TUNE_ORDER, FIXTURE_ID


def test_exact_workflow_invariants_and_evidence() -> None:
    envelope = run_guided_exact(source_commit="test-source")
    assert envelope.fixture_identifier == FIXTURE_ID
    assert envelope.tune_ordering == EXPECTED_TUNE_ORDER
    assert envelope.exact_result["optimal_assignments"] == list(EXPECTED_OPTIMA)
    assert envelope.exact_result["canonical_complement_class"] == "00001111"
    assert envelope.exact_result["evaluated_assignments"] == 256
    assert envelope.evidence_summary["pair_count"] == 28
    assert envelope.evidence_summary["labels_used_only_for_evaluation"] is True
    assert envelope.validation_state["passed"] is True


def test_explanations_differ_by_level_and_are_safe() -> None:
    explanations = run_guided_exact().explanations
    assert set(explanations) == {level.value for level in LearnerLevel}
    assert len(set(explanations.values())) == 3
    assert "2^8" in explanations[LearnerLevel.RESEARCH_DETAIL.value]
    assert all(not claim_violations(text) for text in explanations.values())


@pytest.mark.parametrize(  # type: ignore[untyped-decorator]
    "text",
    [
        "This demonstrates quantum advantage.",
        "The tool is production-ready and scalable.",
        "The registered result was computed now as a live run.",
        "Classical fallback is genuine QAOA.",
        "This is the only correct assignment.",
    ],
)
def test_claim_policy_rejects_unsafe_statements(text: str) -> None:
    with pytest.raises(ValueError):
        validate_claims(text)


def test_json_and_markdown_exports_are_deterministic_and_public_safe() -> None:
    envelope = run_guided_exact(source_commit="test-source")
    json_text = export_json(envelope)
    markdown = export_markdown(envelope, LearnerLevel.TECHNICAL_LEARNER)
    assert json.loads(json_text)["fixture_identifier"] == FIXTURE_ID
    assert "authoritative" in markdown
    assert "C:\\Users\\" not in json_text + markdown
    assert "private/" not in json_text + markdown
    assert json_text == export_json(run_guided_exact(source_commit="test-source"))


def test_deterministic_core_does_not_import_optional_products() -> None:
    import quantum_folk_lab.build_week.workflow as workflow

    source = workflow.__loader__.get_source(workflow.__name__)  # type: ignore[union-attr]
    assert source is not None
    assert "streamlit" not in source.lower()
    assert "qiskit" not in source.lower()
    assert "openai" not in source.lower()
