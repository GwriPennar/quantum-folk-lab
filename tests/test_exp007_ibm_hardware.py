from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from quantum_folk_lab.quantum.ibm_runtime import (
    build_hello_folk_circuit,
    extract_v2_counts,
    load_api_token,
    run_hardware_smoke,
)


@pytest.mark.parametrize("field", ["api" + "key", "api" + "_key", "token"])
def test_load_api_token_accepts_one_supported_field(tmp_path: Path, field: str) -> None:
    credential = tmp_path / "auth.json"
    credential.write_text(json.dumps({field: " test-secret "}), encoding="utf-8")
    assert load_api_token(credential) == "test-secret"


@pytest.mark.parametrize(
    "payload",
    [[], {}, {"token": ""}, {"token": 123}, {"token": "a", "api" + "key": "b"}],
)
def test_load_api_token_rejects_unexpected_structure(tmp_path: Path, payload: object) -> None:
    credential = tmp_path / "auth.json"
    credential.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="credential|token"):
        load_api_token(credential)


def test_build_hello_folk_circuit_is_a_measured_bell_pair() -> None:
    pytest.importorskip("qiskit")
    circuit = build_hello_folk_circuit()
    assert circuit.num_qubits == 2
    assert circuit.num_clbits == 2
    assert circuit.name == "hello_folk_music_world"
    assert circuit.count_ops() == {"measure": 2, "h": 1, "cx": 1}


def test_extract_v2_counts_uses_named_measure_register() -> None:
    measure = SimpleNamespace(get_counts=lambda: {"00": 7, "11": 9})
    pub_result = SimpleNamespace(data=SimpleNamespace(measure=measure))
    assert extract_v2_counts(pub_result) == {"00": 7, "11": 9}


def test_hardware_execution_requires_explicit_confirmation() -> None:
    with pytest.raises(PermissionError, match="confirm-qpu"):
        run_hardware_smoke(token="not-used", shots=256, confirm_qpu=False)
