from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BasicsExperiment:
    name: str
    description: str
    expected_behaviour: str
    limitations: str


def require_qiskit() -> tuple[Any, Any]:
    try:
        from qiskit import QuantumCircuit  # type: ignore[import-not-found]
        from qiskit_aer import AerSimulator  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "EXP-001 requires optional local Qiskit dependencies. "
            'Install them with: python -m pip install -e ".[quantum]"'
        ) from exc
    return QuantumCircuit, AerSimulator


EXPERIMENTS: dict[str, BasicsExperiment] = {
    "zero": BasicsExperiment(
        "zero",
        "Prepare |0> and measure it in the computational basis.",
        "An ideal simulator should return only 0.",
        "This demonstrates ideal preparation and measurement, not hardware noise.",
    ),
    "x": BasicsExperiment(
        "x",
        "Apply an X gate to |0>, producing |1>, then measure.",
        "An ideal simulator should return only 1.",
        "The X gate is noise-free here; real hardware can flip or read out incorrectly.",
    ),
    "hadamard": BasicsExperiment(
        "hadamard",
        "Apply H to |0>, creating an equal superposition, then measure.",
        "Finite shots should show both 0 and 1 with probability near 0.5.",
        "Sampling varies with finite shots even in an ideal simulator.",
    ),
    "double-hadamard": BasicsExperiment(
        "double-hadamard",
        "Apply H twice. Since H is its own inverse, the state returns to |0>.",
        "An ideal simulator should return only 0.",
        "This is exact in the ideal circuit model, before hardware noise is considered.",
    ),
    "z-zero": BasicsExperiment(
        "z-zero",
        "Apply Z to |0>. The state is unchanged because |0> has positive phase.",
        "An ideal simulator should return only 0.",
        "Measurement in the computational basis cannot reveal a global phase.",
    ),
    "z-after-h": BasicsExperiment(
        "z-after-h",
        "Apply H then Z. The phase of the |1> amplitude changes before measurement.",
        "Measurement should still be near 50/50 in the computational basis.",
        "The phase effect is real but not directly visible without another interference step.",
    ),
    "bell": BasicsExperiment(
        "bell",
        "Create a Bell state with H on qubit 0 and CX from qubit 0 to qubit 1.",
        "Only 00 and 11 should appear, approximately balanced, in an ideal simulator.",
        "Ideal entanglement correlations are shown without decoherence or readout error.",
    ),
}


def list_experiments() -> tuple[BasicsExperiment, ...]:
    return tuple(EXPERIMENTS[name] for name in sorted(EXPERIMENTS))


def build_circuit(name: str) -> Any:
    QuantumCircuit, _ = require_qiskit()
    if name not in EXPERIMENTS:
        valid = ", ".join(sorted(EXPERIMENTS))
        raise ValueError(f"unknown basics experiment {name!r}; choose one of: {valid}")
    if name == "bell":
        circuit = QuantumCircuit(2, 2, name=name)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure([0, 1], [0, 1])
        return circuit
    circuit = QuantumCircuit(1, 1, name=name)
    if name == "x":
        circuit.x(0)
    elif name == "hadamard":
        circuit.h(0)
    elif name == "double-hadamard":
        circuit.h(0)
        circuit.h(0)
    elif name == "z-zero":
        circuit.z(0)
    elif name == "z-after-h":
        circuit.h(0)
        circuit.z(0)
    circuit.measure(0, 0)
    return circuit
