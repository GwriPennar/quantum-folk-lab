from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from quantum_folk_lab import cli as cli_module
from quantum_folk_lab.tune_family import (
    CANONICAL_OPTIMUM,
    EXECUTABLE_SOURCE_COMMIT,
    EXPECTED_LABEL_BITSTRING,
    EXPECTED_OPTIMA,
    EXPECTED_TUNE_ORDER,
    FIXTURE_ID,
    GOVERNING_PLAN_COMMIT,
    GOVERNING_REVIEW_COMMITS,
    IMPLEMENTATION_BASE_COMMIT,
    LAMBDA_BALANCE,
    OPTIMAL_PROBABILITY_THRESHOLD,
    RANDOM_SUCCESS_ALL,
    RANDOM_SUCCESS_BALANCED,
    TAU,
    THRESHOLD_CHECKPOINT_COMMIT,
    THRESHOLD_MANIFEST_PATH,
    bitstring_from_bits,
    canonical_bitstring,
    coefficient_summary,
    decode_qiskit_counts,
    registered_fixture,
    serialise_qubo,
    solve_registered_exact,
    threshold_manifest,
    verify_direct_qubo,
)


def test_registered_fixture_order_and_edges() -> None:
    fixture = registered_fixture()
    assert fixture.fixture_id == FIXTURE_ID
    assert fixture.graph.tune_ids == EXPECTED_TUNE_ORDER
    assert bitstring_from_bits(fixture.evaluation_labels) == EXPECTED_LABEL_BITSTRING
    assert len(fixture.graph.edges) == 28
    assert fixture.tau == TAU
    assert fixture.balance_lambda == LAMBDA_BALANCE
    assert [(edge.left, edge.right, edge.weight) for edge in fixture.graph.edges][:4] == [
        (0, 1, 1.0),
        (0, 2, 0.857143),
        (0, 3, 0.975),
        (0, 4, 0.125),
    ]
    assert fixture.graph.edges[-1].weight == 0.630556


def test_registered_qubo_coefficients() -> None:
    fixture = registered_fixture()
    qubo = serialise_qubo(fixture.model)
    assert isinstance(qubo["offset"], float)
    assert round(qubo["offset"], 6) == 14.937301
    linear = qubo["linear"]
    assert isinstance(linear, dict)
    assert round(linear["x_0_fam_a_base"], 6) == -1.207738
    assert round(linear["x_6_fam_b_inserted"], 6) == -1.733333
    quadratic = qubo["quadratic"]
    assert isinstance(quadratic, dict)
    assert round(quadratic["x_0_fam_a_base|x_4_fam_b_base"], 6) == 1.95
    assert round(quadratic["x_6_fam_b_inserted|x_7_fam_b_deleted"], 6) == -1.061112
    summary = coefficient_summary(fixture.model)
    assert summary["quadratic_count"] == 28


def test_all_256_direct_qubo_comparisons_and_exact_solution() -> None:
    verification = verify_direct_qubo()
    exact = solve_registered_exact()
    assert verification.verified_assignments == 256
    assert verification.maximum_disagreement <= 1e-9
    assert exact.evaluated_assignments == 256
    assert exact.exact_optimal_bitstrings == list(EXPECTED_OPTIMA)
    assert exact.exact_minimum_energy <= 1e-12
    assert exact.all_optima_balanced is True
    assert exact.family_recovery == 1.0
    assert exact.exact_complement_classes == [CANONICAL_OPTIMUM]
    assert canonical_bitstring("11110000") == CANONICAL_OPTIMUM


def test_random_baselines_and_threshold_manifest() -> None:
    exact = solve_registered_exact()
    assert round(exact.random_all_expected_energy, 6) == 12.036707
    assert round(exact.random_balanced_expected_energy, 6) == 11.622336
    assert exact.random_all_success_probability == RANDOM_SUCCESS_ALL
    assert exact.random_balanced_success_probability == RANDOM_SUCCESS_BALANCED
    assert OPTIMAL_PROBABILITY_THRESHOLD == 0.05
    manifest = threshold_manifest("plan", "base")
    assert manifest["optimal_probability_success_threshold"] == 0.05
    assert manifest["qaoa_output_generated_before_manifest"] is False
    assert manifest["tau"] == TAU
    assert manifest["lambda"] == LAMBDA_BALANCE


def test_committed_manifest_schema_and_provenance() -> None:
    path = Path("experiments/EXP-005A-tune-family-qaoa/threshold-manifest.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["fixture_identifier"] == FIXTURE_ID
    assert payload["governing_plan_path"] == "docs/plans/EXP-005A-current-qiskit-local-plan.md"
    assert payload["governing_plan_commit"] == GOVERNING_PLAN_COMMIT
    assert payload["governing_review_commits"] == list(GOVERNING_REVIEW_COMMITS)
    assert payload["implementation_base_commit"] == IMPLEMENTATION_BASE_COMMIT
    assert payload["source_base_commit"] == IMPLEMENTATION_BASE_COMMIT
    assert payload["threshold_checkpoint_commit"] == THRESHOLD_CHECKPOINT_COMMIT
    assert payload["checkpoint_commit"] == THRESHOLD_CHECKPOINT_COMMIT
    assert payload["executable_source_commit"] == EXECUTABLE_SOURCE_COMMIT
    assert payload["threshold_manifest_path"] == THRESHOLD_MANIFEST_PATH
    assert payload["governing_plan_commit"] not in payload["governing_review_commits"]
    assert payload["implementation_base_commit"] != payload["governing_plan_commit"]
    assert payload["optimal_probability_success_threshold"] == 0.05
    assert payload["qaoa_output_generated_before_manifest"] is False


def test_committed_result_first_class_provenance_schema() -> None:
    path = Path("experiments/EXP-005A-tune-family-qaoa/results/tune-family-qaoa-p1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_schema_version"] == "exp005a.tune_family_qaoa.v1"
    assert payload["run_identifier"] == "synthetic-two-family-v1-seed42-p1-shots4096-seed42"
    assert payload["base_commit"] == IMPLEMENTATION_BASE_COMMIT
    assert payload["implementation_base_commit"] == IMPLEMENTATION_BASE_COMMIT
    assert payload["checkpoint_commit"] == THRESHOLD_CHECKPOINT_COMMIT
    assert payload["executable_source_commit"] == EXECUTABLE_SOURCE_COMMIT
    assert payload["source_commit"] == EXECUTABLE_SOURCE_COMMIT
    assert payload["threshold_manifest_path"] == THRESHOLD_MANIFEST_PATH
    assert payload["governing_plan_commit"] == GOVERNING_PLAN_COMMIT
    assert payload["governing_review_commits"] == list(GOVERNING_REVIEW_COMMITS)
    assert payload["fixture_identifier"] == FIXTURE_ID
    assert payload["execution_classification"] == "genuine-local-qiskit"
    assert payload["threshold_manifest"]["optimal_probability_success_threshold"] == 0.05


def test_qiskit_count_key_decoding_examples() -> None:
    assert decode_qiskit_counts({"11110000": 3}) == {"00001111": 3}
    assert decode_qiskit_counts({"00001111": 2}) == {"11110000": 2}
    assert decode_qiskit_counts({"10110010": 5}) == {"01001101": 5}


def test_tune_family_qaoa_and_compare_cli_emit_generated_provenance(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class FakeResult:
        exact: dict[str, object] = {"exact_solver_is_ground_truth": True}
        classical_baselines: dict[str, object] = {
            "classical_fallback": {"execution_classification": "classical-fallback"}
        }

        def __init__(self, payload: dict[str, object]) -> None:
            self._payload = payload

        def to_dict(self) -> dict[str, object]:
            return self._payload

    def fake_run_tune_family_qaoa(**kwargs: Any) -> FakeResult:
        manifest = kwargs["threshold_manifest"]
        assert manifest["governing_plan_commit"] == GOVERNING_PLAN_COMMIT
        assert manifest["governing_review_commits"] == list(GOVERNING_REVIEW_COMMITS)
        assert manifest["implementation_base_commit"] == IMPLEMENTATION_BASE_COMMIT
        assert manifest["threshold_checkpoint_commit"] == THRESHOLD_CHECKPOINT_COMMIT
        assert manifest["optimal_probability_success_threshold"] == 0.05
        payload = {
            "result_schema_version": "exp005a.tune_family_qaoa.v1",
            "run_identifier": "synthetic-two-family-v1-seed32",
            "base_commit": kwargs["base_commit"],
            "implementation_base_commit": kwargs["base_commit"],
            "checkpoint_commit": kwargs["checkpoint_commit"],
            "executable_source_commit": kwargs["executable_source_commit"],
            "source_commit": kwargs["source_commit"],
            "threshold_manifest_path": kwargs["threshold_manifest_path"],
            "governing_plan_commit": kwargs["governing_plan_commit"],
            "governing_review_commits": list(kwargs["governing_review_commits"]),
            "fixture_identifier": FIXTURE_ID,
            "execution_classification": "genuine-local-qiskit",
            "sampled": {"shots": kwargs["shots"]},
            "threshold_manifest": manifest,
        }
        return FakeResult(payload)

    monkeypatch.setattr(cli_module, "run_tune_family_qaoa", fake_run_tune_family_qaoa)

    monkeypatch.setattr(sys, "argv", ["qfl", "tune-family-qaoa", "--shots", "32"])
    cli_module.main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["base_commit"] == IMPLEMENTATION_BASE_COMMIT
    assert payload["checkpoint_commit"] == THRESHOLD_CHECKPOINT_COMMIT
    assert payload["executable_source_commit"] == EXECUTABLE_SOURCE_COMMIT
    assert payload["threshold_manifest_path"] == THRESHOLD_MANIFEST_PATH
    assert payload["governing_plan_commit"] == GOVERNING_PLAN_COMMIT
    assert payload["governing_review_commits"] == list(GOVERNING_REVIEW_COMMITS)
    assert payload["sampled"]["shots"] == 32

    monkeypatch.setattr(sys, "argv", ["qfl", "tune-family-compare", "--shots", "32"])
    cli_module.main()
    comparison = json.loads(capsys.readouterr().out)
    qaoa = comparison["qaoa"]
    assert qaoa["base_commit"] == IMPLEMENTATION_BASE_COMMIT
    assert qaoa["checkpoint_commit"] == THRESHOLD_CHECKPOINT_COMMIT
    assert qaoa["executable_source_commit"] == EXECUTABLE_SOURCE_COMMIT
    assert qaoa["threshold_manifest_path"] == THRESHOLD_MANIFEST_PATH
    assert qaoa["governing_plan_commit"] == GOVERNING_PLAN_COMMIT
    assert qaoa["governing_review_commits"] == list(GOVERNING_REVIEW_COMMITS)
    assert comparison["interpretation"]["no_maxcut_approximation_ratio_used"] is True
