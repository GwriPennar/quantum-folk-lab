from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def operation_counts(circuit: Any) -> dict[str, int]:
    return {str(name): int(count) for name, count in circuit.count_ops().items()}


def empirical_probabilities(counts: Mapping[str, int], shots: int) -> dict[str, float]:
    if shots <= 0:
        raise ValueError("shots must be positive")
    return {state: count / shots for state, count in sorted(counts.items())}


def circuit_summary(circuit: Any) -> dict[str, object]:
    return {
        "qubit_count": int(circuit.num_qubits),
        "classical_bit_count": int(circuit.num_clbits),
        "circuit_depth": int(circuit.depth() or 0),
        "circuit_width": int(circuit.width()),
        "operation_counts": operation_counts(circuit),
    }
