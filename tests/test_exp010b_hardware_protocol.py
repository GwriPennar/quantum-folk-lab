from pathlib import Path
from typing import Any

import pytest

from quantum_folk_lab.compact_hardware_protocol import (
    AUTHORIZATION,
    BETA,
    GAMMA,
    ISING_HASH,
    QUBO_HASH,
    Readiness,
    displayed_bitstring,
    select_layout,
    submit_one_job,
)


def ready() -> Readiness:
    return Readiness(QUBO_HASH, ISING_HASH, GAMMA, BETA, True, True)


def test_bit_order() -> None:
    assert displayed_bitstring("0101") == "1010"
    with pytest.raises(ValueError):
        displayed_bitstring("10")


@pytest.mark.parametrize("submit,phrase", [(False, AUTHORIZATION), (True, "wrong")])
def test_guard_precedes_external_calls(tmp_path: Path, submit: bool, phrase: str) -> None:
    calls: list[str] = []
    with pytest.raises(PermissionError):
        submit_one_job(
            submit=submit,
            phrase=phrase,
            readiness=ready(),
            intent=tmp_path / "intent",
            receipt=tmp_path / "receipt",
            credential_reader=lambda: calls.append("credential"),
            runtime_factory=lambda _: calls.append("runtime"),
            submitter=lambda _: "job",
        )
    assert calls == []


@pytest.mark.parametrize("field", ["hash", "angle", "equivalence", "backend"])
def test_readiness_failures_never_read_credentials(tmp_path: Path, field: str) -> None:
    values = ready().__dict__.copy()
    if field == "hash":
        values["qubo_hash"] = "bad"
    elif field == "angle":
        values["gamma"] = 0.0
    elif field == "equivalence":
        values["equivalence_passed"] = False
    else:
        values["backend_gates_passed"] = False
    called = False

    def reader() -> None:
        nonlocal called
        called = True

    with pytest.raises(RuntimeError):
        submit_one_job(
            submit=True,
            phrase=AUTHORIZATION,
            readiness=Readiness(**values),
            intent=tmp_path / "intent",
            receipt=tmp_path / "receipt",
            credential_reader=reader,
            runtime_factory=lambda _: None,
            submitter=lambda _: "job",
        )
    assert not called


def test_mocked_single_submission_and_receipt_blocks_retry(tmp_path: Path) -> None:
    intent, receipt = tmp_path / "intent", tmp_path / "receipt"
    assert (
        submit_one_job(
            submit=True,
            phrase=AUTHORIZATION,
            readiness=ready(),
            intent=intent,
            receipt=receipt,
            credential_reader=lambda: "secret",
            runtime_factory=lambda _: "runtime",
            submitter=lambda _: "mock-job",
        )
        == "mock-job"
    )
    assert intent.exists() and receipt.exists()
    with pytest.raises(RuntimeError):
        submit_one_job(
            submit=True,
            phrase=AUTHORIZATION,
            readiness=ready(),
            intent=intent,
            receipt=receipt,
            credential_reader=lambda: None,
            runtime_factory=lambda _: None,
            submitter=lambda _: "second",
        )


def test_selector_is_deterministic() -> None:
    base: dict[str, Any] = {
        "operational": True,
        "simulator": False,
        "qubits": 8,
        "transpiled": True,
        "two_qubit_depth": 8,
        "depth": 40,
        "duration_us": 50.0,
        "two_qubit_error": 0.01,
        "readout_error": 0.02,
        "usage": 1.0,
        "unavailable": False,
    }
    records = [
        dict(base, backend="fixture-b", layout=(1, 2, 3, 4), two_qubit_count=14),
        dict(base, backend="fixture-a", layout=(0, 1, 2, 3), two_qubit_count=12),
    ]
    assert select_layout(records)["backend"] == "fixture-a"
