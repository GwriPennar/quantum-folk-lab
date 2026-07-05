from __future__ import annotations

import json
from pathlib import Path

from quantum_folk_lab.tune_family import (
    CANONICAL_OPTIMUM,
    EXPECTED_LABEL_BITSTRING,
    EXPECTED_OPTIMA,
    EXPECTED_TUNE_ORDER,
    FIXTURE_ID,
    LAMBDA_BALANCE,
    OPTIMAL_PROBABILITY_THRESHOLD,
    RANDOM_SUCCESS_ALL,
    RANDOM_SUCCESS_BALANCED,
    TAU,
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
    assert payload["governing_plan_commit"] == "e2ed10d692b5ac03cd2964c691ba37de8de4eacd"
    assert payload["optimal_probability_success_threshold"] == 0.05
    assert payload["qaoa_output_generated_before_manifest"] is False


def test_qiskit_count_key_decoding_examples() -> None:
    assert decode_qiskit_counts({"11110000": 3}) == {"00001111": 3}
    assert decode_qiskit_counts({"00001111": 2}) == {"11110000": 2}
    assert decode_qiskit_counts({"10110010": 5}) == {"01001101": 5}
