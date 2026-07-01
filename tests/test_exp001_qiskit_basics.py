from __future__ import annotations

import pytest

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_aer")

from quantum_folk_lab.quantum_basics import build_circuit
from quantum_folk_lab.simulation import run_all_basics, run_basics_experiment

pytestmark = pytest.mark.quantum


def test_zero_state_measurement_is_deterministic() -> None:
    result = run_basics_experiment("zero", shots=128)
    assert result.measurement_counts == {"0": 128}
    assert result.pass_or_caution == "pass"


def test_x_gate_measurement_is_deterministic() -> None:
    result = run_basics_experiment("x", shots=128)
    assert result.measurement_counts == {"1": 128}
    assert result.pass_or_caution == "pass"


def test_hadamard_is_balanced_with_finite_shots() -> None:
    result = run_basics_experiment("hadamard", shots=4096)
    assert {"0", "1"}.issubset(result.measurement_counts)
    assert abs(result.empirical_probabilities["0"] - 0.5) <= 0.08
    assert result.pass_or_caution == "pass"


def test_double_hadamard_returns_to_zero() -> None:
    result = run_basics_experiment("double-hadamard", shots=128)
    assert result.measurement_counts == {"0": 128}
    assert result.pass_or_caution == "pass"


def test_z_phase_cases() -> None:
    z_zero = run_basics_experiment("z-zero", shots=128)
    z_after_h = run_basics_experiment("z-after-h", shots=4096)
    assert z_zero.measurement_counts == {"0": 128}
    assert abs(z_after_h.empirical_probabilities["0"] - 0.5) <= 0.08


def test_bell_state_correlation_in_ideal_simulation() -> None:
    result = run_basics_experiment("bell", shots=4096)
    assert result.measurement_counts.get("01", 0) == 0
    assert result.measurement_counts.get("10", 0) == 0
    assert set(result.measurement_counts) == {"00", "11"}
    assert abs(result.empirical_probabilities["00"] - 0.5) <= 0.08
    assert result.pass_or_caution == "pass"


def test_result_schema_contains_required_fields() -> None:
    result = run_basics_experiment("zero", shots=32).to_dict()
    for key in (
        "experiment_name",
        "description",
        "qubit_count",
        "classical_bit_count",
        "shots",
        "seed_simulator",
        "seed_transpiler",
        "circuit_depth",
        "circuit_width",
        "operation_counts",
        "transpiled_depth",
        "transpiled_operation_counts",
        "measurement_counts",
        "empirical_probabilities",
        "expected_behaviour",
        "pass_or_caution",
        "limitations",
        "python_version",
        "qiskit_version",
        "aer_version",
        "elapsed_seconds",
    ):
        assert key in result


def test_circuit_metadata_reporting() -> None:
    bell = build_circuit("bell")
    assert bell.num_qubits == 2
    assert bell.num_clbits == 2
    assert bell.count_ops()["cx"] == 1


def test_run_all_basics() -> None:
    results = run_all_basics(shots=64)
    assert {result.experiment_name for result in results} >= {"zero", "x", "bell"}
