from __future__ import annotations

import builtins
from typing import Any

import pytest

pytest.importorskip("qiskit")

from quantum_folk_lab.tune_family import (
    build_ising_model,
    registered_fixture,
    sparse_pauli_terms,
    verify_qubo_ising,
)
from quantum_folk_lab.tune_family_qaoa import (
    build_measured_qaoa_circuit,
    build_qaoa_ansatz,
    build_sparse_pauli_operator,
    require_qiskit_qaoa,
)

pytestmark = pytest.mark.quantum


def test_exp005a_ising_operator_structure_and_all_basis_equivalence() -> None:
    fixture = registered_fixture()
    ising = build_ising_model(fixture.model)
    verification = verify_qubo_ising()
    assert verification.verified_assignments == 256
    assert verification.maximum_disagreement <= 1e-8
    assert len(ising.linear_z) == 8
    assert len(ising.quadratic_zz) == 28
    terms = sparse_pauli_terms(fixture.model, include_constant=False)
    assert len(terms) == 36
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
