from __future__ import annotations

import platform
import time
from dataclasses import asdict, dataclass
from importlib import metadata

from quantum_folk_lab.circuit_reporting import (
    empirical_probabilities,
    operation_counts,
)
from quantum_folk_lab.quantum_basics import EXPERIMENTS, build_circuit, require_qiskit


@dataclass(frozen=True)
class BasicsResult:
    experiment_name: str
    description: str
    qubit_count: int
    classical_bit_count: int
    shots: int
    seed_simulator: int
    seed_transpiler: int
    circuit_depth: int
    circuit_width: int
    operation_counts: dict[str, int]
    transpiled_depth: int
    transpiled_operation_counts: dict[str, int]
    measurement_counts: dict[str, int]
    empirical_probabilities: dict[str, float]
    expected_behaviour: str
    pass_or_caution: str
    limitations: str
    python_version: str
    qiskit_version: str
    aer_version: str
    elapsed_seconds: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not installed"


def _status(
    name: str, counts: dict[str, int], probabilities: dict[str, float], tolerance: float
) -> str:
    invalid_bell = counts.get("01", 0) + counts.get("10", 0)
    if name == "zero" and counts.get("0", 0) == sum(counts.values()):
        return "pass"
    if name == "x" and counts.get("1", 0) == sum(counts.values()):
        return "pass"
    if (
        name == "hadamard"
        and {"0", "1"}.issubset(counts)
        and abs(probabilities.get("0", 0.0) - 0.5) <= tolerance
    ):
        return "pass"
    if name == "double-hadamard" and counts.get("0", 0) == sum(counts.values()):
        return "pass"
    if name == "z-zero" and counts.get("0", 0) == sum(counts.values()):
        return "pass"
    if (
        name == "z-after-h"
        and {"0", "1"}.issubset(counts)
        and abs(probabilities.get("0", 0.0) - 0.5) <= tolerance
    ):
        return "pass"
    if (
        name == "bell"
        and invalid_bell == 0
        and abs(probabilities.get("00", 0.0) - 0.5) <= tolerance
    ):
        return "pass"
    return "caution"


def run_basics_experiment(
    name: str,
    shots: int = 4096,
    seed_simulator: int = 42,
    seed_transpiler: int = 42,
    balance_tolerance: float = 0.08,
) -> BasicsResult:
    if shots <= 0:
        raise ValueError("shots must be positive")
    _, AerSimulator = require_qiskit()
    try:
        from qiskit import transpile  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError("Qiskit is required for EXP-001 local simulation.") from exc
    experiment = EXPERIMENTS[name]
    circuit = build_circuit(name)
    start = time.perf_counter()
    simulator = AerSimulator(seed_simulator=seed_simulator)
    transpiled = transpile(circuit, simulator, seed_transpiler=seed_transpiler)
    raw_counts: dict[str, int] = simulator.run(transpiled, shots=shots).result().get_counts()
    elapsed = time.perf_counter() - start
    counts = {str(state): int(count) for state, count in sorted(raw_counts.items())}
    probabilities = empirical_probabilities(counts, shots)
    status = _status(name, counts, probabilities, balance_tolerance)
    return BasicsResult(
        experiment_name=name,
        description=experiment.description,
        qubit_count=int(circuit.num_qubits),
        classical_bit_count=int(circuit.num_clbits),
        shots=shots,
        seed_simulator=seed_simulator,
        seed_transpiler=seed_transpiler,
        circuit_depth=int(circuit.depth() or 0),
        circuit_width=int(circuit.width()),
        operation_counts=operation_counts(circuit),
        transpiled_depth=int(transpiled.depth() or 0),
        transpiled_operation_counts=operation_counts(transpiled),
        measurement_counts=counts,
        empirical_probabilities=probabilities,
        expected_behaviour=experiment.expected_behaviour,
        pass_or_caution=status,
        limitations=experiment.limitations,
        python_version=platform.python_version(),
        qiskit_version=package_version("qiskit"),
        aer_version=package_version("qiskit-aer"),
        elapsed_seconds=round(elapsed, 6),
    )


def run_all_basics(
    shots: int = 4096, seed_simulator: int = 42, seed_transpiler: int = 42
) -> list[BasicsResult]:
    return [
        run_basics_experiment(name, shots, seed_simulator, seed_transpiler)
        for name in sorted(EXPERIMENTS)
    ]
