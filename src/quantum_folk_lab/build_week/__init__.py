"""OpenAI Build Week Guided Experiment services."""

from .ai import DEFAULT_OPENAI_MODEL, ExplanationResult, explain_result
from .explanations import deterministic_explanation
from .export import export_json, export_markdown
from .landscape import (
    ExactLandscape,
    LandscapeEntry,
    RegisteredQAOAEvidence,
    build_exact_landscape,
    parse_registered_qaoa_evidence,
)
from .models import DemoState, ExecutionClassification, LearnerLevel, ResultEnvelope
from .quantum import quantum_capability, run_quick_qiskit
from .workflow import run_guided_exact

__all__ = [
    "DEFAULT_OPENAI_MODEL",
    "ExplanationResult",
    "DemoState",
    "ExecutionClassification",
    "ExactLandscape",
    "LandscapeEntry",
    "LearnerLevel",
    "RegisteredQAOAEvidence",
    "ResultEnvelope",
    "deterministic_explanation",
    "build_exact_landscape",
    "export_json",
    "export_markdown",
    "explain_result",
    "quantum_capability",
    "parse_registered_qaoa_evidence",
    "run_guided_exact",
    "run_quick_qiskit",
]
