from __future__ import annotations

import builtins
from typing import Any, cast

import pytest

pytest.importorskip("qiskit")

from quantum_folk_lab.tune_family import (
    EXECUTABLE_SOURCE_COMMIT,
    GOVERNING_PLAN_COMMIT,
    GOVERNING_REVIEW_COMMITS,
    IMPLEMENTATION_BASE_COMMIT,
    OPTIMAL_PROBABILITY_THRESHOLD,
    THRESHOLD_CHECKPOINT_COMMIT,
    THRESHOLD_MANIFEST_PATH,
    build_ising_model,
    registered_fixture,
    sparse_pauli_terms,
    threshold_manifest,
    verify_qubo_ising,
)
from quantum_folk_lab.tune_family_qaoa import (
    build_measured_qaoa_circuit,
    build_qaoa_ansatz,
    build_sparse_pauli_operator,
    require_qiskit_qaoa,
    run_tune_family_qaoa,
)

pytestmark = pytest.mark.quantum


def test_exp005a_ising_operator_structure_and_all_basis_equivalence() -> None:
    fixture = registered_fixture()
    ising = build_ising_model(fixture.model)
    verification = verify_qubo_ising()
    assert verification.verified_assignments == 256
    assert verification.maximum_disagreement <= 1e-8
    assert len(ising.linear_z) == 0
    assert len(ising.quadratic_zz) == 28
    terms = sparse_pauli_terms(fixture.model, include_constant=False)
    assert len(terms) == 28
    operator = build_sparse_pauli_operator(include_constant=False)
    assert operator.num_qubits == 8


def test_exp005a_qaoa_ansatz_construction_and_binding() -> None:
    ansatz = build_qaoa_ansatz(depth=1)
    assert ansatz.num_qubits == 8
    assert ansatz.num_parameters == 2
    measured = build_measured_qaoa_circuit([0.2, 0.2], depth=1)
    assert measured.num_qubits == 8
    assert measured.num_clbits == 8
    assert measured.width() == 16
    assert measured.depth() is not None


def test_exp005a_missing_qiskit_error_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.startswith("qiskit"):
            raise ModuleNotFoundError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(RuntimeError, match="EXP-005A genuine local Qiskit QAOA requires"):
        require_qiskit_qaoa()


def test_exp005a_genuine_qiskit_estimator_sampler_smoke() -> None:
    manifest = threshold_manifest()
    result = run_tune_family_qaoa(
        threshold_manifest=manifest,
        shots=16,
        optimiser_max_iterations=1,
        initial_points=((0.2, 0.2),),
    )
    payload = result.to_dict()
    classical_baselines = cast(dict[str, Any], payload["classical_baselines"])
    classical_fallback = cast(dict[str, Any], classical_baselines["classical_fallback"])
    measurement_counts = cast(dict[str, int], payload["measurement_counts"])
    sampled = cast(dict[str, Any], payload["sampled"])
    circuit_metrics = cast(dict[str, Any], payload["circuit_metrics"])
    threshold_payload = cast(dict[str, Any], payload["threshold_manifest"])
    assert payload["execution_classification"] == "genuine-local-qiskit"
    assert classical_fallback["execution_classification"] == "classical-fallback"
    assert sum(measurement_counts.values()) == 16
    assert sampled["shots"] == 16
    assert sampled
    assert isinstance(payload["expected_energy"], float)
    assert circuit_metrics["logical_problem_qubits"] == 8
    assert payload["base_commit"] == IMPLEMENTATION_BASE_COMMIT
    assert payload["implementation_base_commit"] == IMPLEMENTATION_BASE_COMMIT
    assert payload["checkpoint_commit"] == THRESHOLD_CHECKPOINT_COMMIT
    assert payload["executable_source_commit"] == EXECUTABLE_SOURCE_COMMIT
    assert payload["source_commit"] == EXECUTABLE_SOURCE_COMMIT
    assert payload["threshold_manifest_path"] == THRESHOLD_MANIFEST_PATH
    assert payload["governing_plan_commit"] == GOVERNING_PLAN_COMMIT
    assert payload["governing_review_commits"] == list(GOVERNING_REVIEW_COMMITS)
    assert (
        threshold_payload["optimal_probability_success_threshold"] == OPTIMAL_PROBABILITY_THRESHOLD
    )
