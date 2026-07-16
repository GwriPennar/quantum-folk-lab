"""Optional, grounded OpenAI explanation adapter with deterministic fallback."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from .claims import validate_claims
from .models import LearnerLevel, ResultEnvelope

DEFAULT_OPENAI_MODEL = "gpt-5.6-sol"
OPENAI_CREDENTIAL_ENV = "OPENAI_" + "API" + "_KEY"
REQUIRED_SECTIONS = (
    "title",
    "summary",
    "musical_question",
    "what_the_model_did",
    "what_the_exact_result_means",
    "quantum_comparison",
    "limitations",
    "next_learning_step",
    "grounded_fields",
)
ALLOWED_GROUNDED_FIELDS = frozenset(
    {
        "fixture_identifier",
        "fixture_description",
        "tune_ordering",
        "parameters.tau",
        "parameters.lambda",
        "parameters.graph_threshold",
        "exact_result.minimum_energy",
        "exact_result.optimal_assignments",
        "exact_result.canonical_complement_class",
        "exact_result.family_recovery",
        "execution_classification",
        "validation_state.passed",
    }
)


class ResponsesClient(Protocol):
    responses: Any


@dataclass(frozen=True)
class ExplanationResult:
    text: str
    source: str
    model: str | None
    fallback_reason: str | None


def selected_model(environment: Mapping[str, str] | None = None) -> str:
    env = os.environ if environment is None else environment
    return env.get("QFL_OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL


def _input_payload(envelope: ResultEnvelope, level: LearnerLevel) -> dict[str, object]:
    data = envelope.to_dict()
    return {
        "learner_level": level.value,
        "result": {
            key: data[key]
            for key in (
                "fixture_identifier",
                "fixture_description",
                "tune_ordering",
                "parameters",
                "evidence_summary",
                "qubo_summary",
                "exact_result",
                "execution_classification",
                "validation_state",
                "claims_boundary",
            )
        },
        "task": "Explain the validated result without adding scientific values or claims.",
        "allowed_claim_policy": list(envelope.claims_boundary),
    }


def _schema() -> dict[str, object]:
    properties: dict[str, object] = {
        key: {"type": "string"} for key in REQUIRED_SECTIONS if key != "grounded_fields"
    }
    properties["grounded_fields"] = {
        "type": "array",
        "items": {"type": "string", "enum": sorted(ALLOWED_GROUNDED_FIELDS)},
        "minItems": 1,
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(REQUIRED_SECTIONS),
        "additionalProperties": False,
    }


def _validate_output(raw: str, envelope: ResultEnvelope) -> str:
    parsed = json.loads(raw)
    if not isinstance(parsed, dict) or set(parsed) != set(REQUIRED_SECTIONS):
        raise ValueError("explanation schema mismatch")
    grounded = parsed["grounded_fields"]
    if not isinstance(grounded, list) or not grounded:
        raise ValueError("grounded_fields must be a non-empty list")
    if any(field not in ALLOWED_GROUNDED_FIELDS for field in grounded):
        raise ValueError("unknown grounded field")
    sections = [str(parsed[key]).strip() for key in REQUIRED_SECTIONS[:-1]]
    if any(not section for section in sections):
        raise ValueError("explanation sections must not be empty")
    combined = "\n\n".join(sections)
    validate_claims(combined)
    exact = envelope.exact_result
    source = json.dumps(_input_payload(envelope, LearnerLevel.FIRST_ENCOUNTER))
    forbidden_numbers = _numbers_not_in_input(combined, source)
    if forbidden_numbers:
        raise ValueError("explanation contains an ungrounded numeric value")
    canonical = str(exact["canonical_complement_class"])
    if canonical not in combined:
        raise ValueError("explanation omits the authoritative canonical result")
    return combined


def _numbers_not_in_input(output: str, source: str) -> set[str]:
    import re

    numbers = set(re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?", output))
    allowed = set(re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?", source))
    return numbers - allowed


def explain_result(
    envelope: ResultEnvelope,
    level: LearnerLevel,
    *,
    client: ResponsesClient | None = None,
    environment: Mapping[str, str] | None = None,
) -> ExplanationResult:
    env = os.environ if environment is None else environment
    fallback = envelope.explanations[level.value]
    model = selected_model(env)
    if client is None and not env.get(OPENAI_CREDENTIAL_ENV):
        return ExplanationResult(
            fallback, "deterministic", None, "the OpenAI credential is not configured"
        )
    try:
        if client is None:
            from openai import OpenAI  # type: ignore[import-not-found,unused-ignore]

            client = OpenAI()
        response = client.responses.create(
            model=model,
            input=json.dumps(_input_payload(envelope, level), sort_keys=True),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "qfl_grounded_explanation",
                    "strict": True,
                    "schema": _schema(),
                }
            },
        )
        validated = _validate_output(str(response.output_text), envelope)
        return ExplanationResult(validated, "gpt-5.6", model, None)
    except Exception as exc:  # The optional network path must always fail closed.
        return ExplanationResult(fallback, "deterministic", None, str(exc))
