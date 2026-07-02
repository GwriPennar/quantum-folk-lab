from __future__ import annotations

import builtins
from typing import Any

import pytest

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_aer")

from quantum_folk_lab.maxcut import CYCLE4, assignment_to_qiskit_key, decode_counts
from quantum_folk_lab.maxcut_ising import (
    build_cut_operator,
    build_minimization_operator,
    pauli_cut_expectation,
    qubo_value,
    verify_equivalence,
)
from quantum_folk_lab.maxcut_qaoa import (
    build_measured_qaoa_circuit,
    build_qaoa_ansatz,
    run_maxcut_qaoa,
)

pytestmark = pytest.mark.quantum


def test_qubo_and_ising_equivalence_all_cycle4_assignments() -> None:
    rows = verify_equivalence(CYCLE4)
    assert len(rows) == 16
    optimal = [row for row in rows if row.direct_cut == 4.0]
    assert [row.bitstring for row in optimal] == ["0101", "1010"]
    for row in rows:
        assert row.direct_cut == row.qubo_value
        assert row.pauli_cut_expectation == row.direct_cut
        assert row.minimization_energy == -row.direct_cut


def test_operator_convention_and_basis_values() -> None:
    cut_operator = build_cut_operator(CYCLE4)
    min_operator = build_minimization_operator(CYCLE4)
    assert cut_operator.num_qubits == 4
    assert min_operator.num_qubits == 4
    assert pauli_cut_expectation(CYCLE4, (0, 1, 0, 1)) == 4.0
    assert qubo_value(CYCLE4, (0, 0, 0, 0)) == 0.0


def test_qiskit_bit_order_conversion_and_count_decode() -> None:
    assert assignment_to_qiskit_key((0, 1, 0, 1)) == "1010"
    decoded = decode_counts({"1010": 3, "0101": 5})
    assert decoded == {"0101": 3, "1010": 5}


def test_qaoa_ansatz_and_measured_circuit() -> None:
    ansatz = build_qaoa_ansatz(CYCLE4, depth=1)
    assert ansatz.num_qubits == 4
    assert ansatz.num_parameters == 2
    measured = build_measured_qaoa_circuit(CYCLE4, [0.25, 0.5], depth=1)
    assert measured.num_qubits == 4
    assert measured.num_clbits == 4
    assert measured.depth() is not None


def test_registered_cycle4_qaoa_run_samples_optimum() -> None:
    result = run_maxcut_qaoa(CYCLE4, depth=1, shots=512, seed=42, optimiser_max_iterations=30)
    assert result.genuine_qiskit_circuit is True
    assert result.exact_max_cut == 4.0
    assert result.exact_optimal_bitstrings == ["0101", "1010"]
    assert result.sampled_best_bitstring in {"0101", "1010"}
    assert result.sampled_best_cut == 4.0
    assert result.sampled_best_approximation_ratio == 1.0
    assert result.expected_approximation_ratio < 1.0
    assert result.optimal_sample_count > 0
    assert result.optimal_sample_probability > 0.0
    assert result.pass_or_caution == "pass"


def test_missing_qiskit_error_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.startswith("qiskit"):
            raise ModuleNotFoundError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(RuntimeError, match="EXP-002 requires optional local Qiskit dependencies"):
        build_qaoa_ansatz(CYCLE4)
