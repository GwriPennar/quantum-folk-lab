"""Exact-first orchestration for the fixed Guided Experiment."""

from __future__ import annotations

import platform
from dataclasses import asdict

from quantum_folk_lab import __version__
from quantum_folk_lab.tune_family import (
    EXPECTED_OPTIMA,
    coefficient_summary,
    registered_fixture,
    solve_registered_exact,
    verify_direct_qubo,
    verify_qubo_ising,
)

from .explanations import deterministic_explanation
from .fixture import fixture_summary, musical_evidence
from .models import (
    RESULT_ENVELOPE_SCHEMA,
    ExecutionClassification,
    LearnerLevel,
    ResultEnvelope,
)

PRE_BUILD_WEEK_COMMIT = "281ba4013112a071bba4a70579c24d051da36c51"
GOVERNING_PLAN_COMMIT = "3950a1f4f6c7c3f65c613133dec6dd8075739f57"


def run_guided_exact(source_commit: str = "working-tree") -> ResultEnvelope:
    fixture = registered_fixture()
    summary = fixture_summary()
    pairs = musical_evidence()
    direct_qubo = verify_direct_qubo()
    qubo_ising = verify_qubo_ising()
    exact = solve_registered_exact(fixture)
    if exact.exact_optimal_bitstrings != list(EXPECTED_OPTIMA):
        raise AssertionError("registered exact optimum changed")
    evidence = {
        "pair_count": len(pairs),
        "graph_edge_count": sum(pair.graph_edge for pair in pairs),
        "features": ["interval", "contour", "rhythm"],
        "labels_used_only_for_evaluation": True,
        "pairs": [asdict(pair) for pair in pairs],
    }
    envelope = ResultEnvelope(
        schema_version=RESULT_ENVELOPE_SCHEMA,
        run_identifier="build-week-exact-synthetic-two-family-v1-seed42",
        fixture_identifier=fixture.fixture_id,
        fixture_description=str(summary["description"]),
        tune_ordering=fixture.graph.tune_ids,
        parameters={
            "tau": fixture.tau,
            "lambda": fixture.balance_lambda,
            "graph_threshold": fixture.graph_threshold,
        },
        bit_ordering_convention=(
            "Human bitstrings are left-to-right in tune order; bit i maps to tune i."
        ),
        complement_canonicalisation_rule=(
            "A bitstring and its global complement are the same unlabeled partition; "
            "the lexicographically smaller string is canonical."
        ),
        evidence_summary=evidence,
        qubo_summary=coefficient_summary(fixture.model),
        exact_result={
            "minimum_energy": (
                0.0 if abs(exact.exact_minimum_energy) < 1e-12 else exact.exact_minimum_energy
            ),
            "optimal_assignments": exact.exact_optimal_bitstrings,
            "canonical_complement_class": exact.canonical_optimum,
            "evaluated_assignments": exact.evaluated_assignments,
            "family_recovery": exact.family_recovery,
            "all_optima_balanced": exact.all_optima_balanced,
        },
        execution_classification=ExecutionClassification.CURRENT_EXACT,
        validation_state={
            "passed": True,
            "direct_qubo": direct_qubo.to_dict(),
            "qubo_ising": qubo_ising.to_dict(),
        },
        claims_boundary=(
            "Exact enumeration is authoritative for this fixed eight-variable fixture.",
            "The fixture is deterministic and synthetic, not authentic cultural data.",
            "No quantum speed, scale, production, or hardware claim is supported.",
            "Historical registered evidence must never be presented as a current run.",
        ),
        software_provenance={
            "package": f"quantum-folk-lab {__version__}",
            "python": platform.python_version(),
            "pre_build_week_commit": PRE_BUILD_WEEK_COMMIT,
            "governing_plan_commit": GOVERNING_PLAN_COMMIT,
            "executable_source_commit": source_commit,
            "entry_point": "quantum_folk_lab.build_week.run_guided_exact",
        },
    )
    explanations = {
        level.value: deterministic_explanation(envelope, level) for level in LearnerLevel
    }
    return ResultEnvelope(**{**envelope.__dict__, "explanations": explanations})
