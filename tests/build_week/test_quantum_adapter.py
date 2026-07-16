from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from quantum_folk_lab.build_week.quantum import (
    QUICK_QAOA_MAX_ITERATIONS,
    QUICK_QAOA_SHOTS,
    run_quick_qiskit,
)


def test_quick_adapter_uses_bounded_configuration() -> None:
    captured: dict[str, Any] = {}

    def fake_runner(**kwargs: Any) -> SimpleNamespace:
        captured.update(kwargs)
        return SimpleNamespace(
            to_dict=lambda: {
                "run_identifier": "quick",
                "expected_energy": 0.1,
                "expected_objective_gap": 0.1,
                "sampled": {
                    "best_sampled_human_bitstring": "00001111",
                    "optimal_complement_class_probability": 0.5,
                    "balanced_sample_probability": 0.75,
                },
                "circuit_metrics": {
                    "total_qiskit_circuit_width": 16,
                    "transpiled_depth": 20,
                    "two_qubit_gate_count": 8,
                },
                "qaoa_configuration": {
                    "shots": kwargs["shots"],
                    "depth": kwargs["depth"],
                    "sampler_seed": kwargs["sampler_seed"],
                    "estimator_seed": kwargs["estimator_seed"],
                    "optimiser_max_iterations": kwargs["optimiser_max_iterations"],
                },
                "elapsed_seconds": 1.0,
                "limitations": "local simulation only",
            }
        )

    result = run_quick_qiskit(fake_runner)
    assert captured["shots"] == QUICK_QAOA_SHOTS == 256
    assert captured["optimiser_max_iterations"] == QUICK_QAOA_MAX_ITERATIONS == 8
    assert captured["initial_points"] == ((0.0, 0.0),)
    assert result["execution_classification"] == "current-local-qiskit-quick-run"
