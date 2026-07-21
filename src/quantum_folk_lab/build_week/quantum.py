"""Bounded optional Qiskit adapter for the Guided Experiment."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any, cast

from quantum_folk_lab.tune_family import ESTIMATOR_SEED, SAMPLER_SEED, threshold_manifest

from .models import ExecutionClassification

QUICK_QAOA_DEPTH = 1
QUICK_QAOA_SHOTS = 256
QUICK_QAOA_MAX_ITERATIONS = 8
QUICK_QAOA_INITIAL_POINTS = ((0.0, 0.0),)


@dataclass(frozen=True)
class QuantumCapability:
    available: bool
    classification: ExecutionClassification
    message: str
    install_command: str = 'python -m pip install -e ".[quantum]"'

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["classification"] = self.classification.value
        return payload


def quantum_capability() -> QuantumCapability:
    try:
        import qiskit  # type: ignore[import-not-found,import-untyped,unused-ignore]  # noqa: F401
        import scipy  # type: ignore[import-untyped,unused-ignore]  # noqa: F401
    except ModuleNotFoundError:
        return QuantumCapability(
            available=False,
            classification=ExecutionClassification.UNAVAILABLE,
            message=(
                "Local Qiskit is not installed. The exact experiment remains complete and "
                "authoritative. Install the optional quantum extra to enable a quick run."
            ),
        )
    return QuantumCapability(
        available=True,
        classification=ExecutionClassification.CURRENT_QISKIT,
        message="A bounded local ideal-simulator Qiskit quick run is available.",
    )


def run_quick_qiskit(
    runner: Callable[..., Any] | None = None,
) -> dict[str, object]:
    if runner is None:
        from quantum_folk_lab.tune_family_qaoa import run_tune_family_qaoa

        runner = run_tune_family_qaoa
    result = runner(
        threshold_manifest=threshold_manifest(),
        depth=QUICK_QAOA_DEPTH,
        shots=QUICK_QAOA_SHOTS,
        sampler_seed=SAMPLER_SEED,
        estimator_seed=ESTIMATOR_SEED,
        optimiser_max_iterations=QUICK_QAOA_MAX_ITERATIONS,
        initial_points=QUICK_QAOA_INITIAL_POINTS,
    )
    payload = result.to_dict()
    sampled = cast(dict[str, object], payload["sampled"])
    circuit = cast(dict[str, object], payload["circuit_metrics"])
    config = cast(dict[str, object], payload["qaoa_configuration"])
    return {
        "execution_classification": ExecutionClassification.CURRENT_QISKIT.value,
        "run_identifier": payload["run_identifier"],
        "expected_energy": payload["expected_energy"],
        "expected_objective_gap": payload["expected_objective_gap"],
        "best_sampled_assignment": sampled["best_sampled_human_bitstring"],
        "measurement_counts": payload["measurement_counts"],
        "optimal_complement_class_probability": sampled["optimal_complement_class_probability"],
        "balanced_sample_probability": sampled["balanced_sample_probability"],
        "shots": config["shots"],
        "depth": config["depth"],
        "sampler_seed": config["sampler_seed"],
        "estimator_seed": config["estimator_seed"],
        "optimiser_max_iterations": config["optimiser_max_iterations"],
        "circuit_width": circuit["total_qiskit_circuit_width"],
        "circuit_depth": circuit["transpiled_depth"],
        "two_qubit_gate_count": circuit["two_qubit_gate_count"],
        "elapsed_seconds": payload["elapsed_seconds"],
        "limitations": payload["limitations"],
    }
