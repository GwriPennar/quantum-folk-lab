import ast
from pathlib import Path

from scripts.run_exp010d_preflight import load_and_validate_rows, parameterised_circuit


def test_frozen_workload_is_complete() -> None:
    rows = load_and_validate_rows()
    assert len(rows) == 32
    assert sum(row["kind"] == "landscape" for row in rows) == 24
    assert sum(row["kind"] == "centre" for row in rows) == 4
    assert sum(row["kind"] == "control" for row in rows) == 4


def test_circuit_is_parameterised_once() -> None:
    circuit, gamma, beta = parameterised_circuit()
    assert circuit.parameters == {gamma, beta}
    assert circuit.num_qubits == 4
    assert circuit.num_clbits == 4


def test_preflight_has_no_submission_or_credential_surface() -> None:
    source = Path("scripts/run_exp010d_preflight.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert "service.backend(" in source
    for forbidden in (
        "Sampler",
        "Estimator",
        "Session",
        "Batch",
        "save_account",
        "submission-intent",
        "submission-receipt",
    ):
        assert forbidden not in source
    assert tree is not None
