from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from quantum_folk_lab.maxcut import (
    Assignment,
    MaxCutGraph,
    all_assignments,
    assignment_to_bitstring,
    cut_value,
)


@dataclass(frozen=True)
class EquivalenceRow:
    bitstring: str
    direct_cut: float
    qubo_value: float
    pauli_cut_expectation: float
    minimization_energy: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def require_qiskit_ising() -> tuple[Any, Any]:
    try:
        from qiskit.circuit.library import QAOAAnsatz  # type: ignore[import-not-found]
        from qiskit.quantum_info import SparsePauliOp  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "EXP-002 requires optional local Qiskit dependencies. "
            'Install them with: python -m pip install -e ".[quantum]"'
        ) from exc
    return SparsePauliOp, QAOAAnsatz


def qubo_value(graph: MaxCutGraph, assignment: Assignment) -> float:
    value = 0.0
    for edge in graph.edges:
        i = graph.node_index(edge.u)
        j = graph.node_index(edge.v)
        value += edge.weight * (assignment[i] + assignment[j] - 2 * assignment[i] * assignment[j])
    return value


def z_eigenvalue(bit: int) -> int:
    if bit == 0:
        return 1
    if bit == 1:
        return -1
    raise ValueError("bit must be 0 or 1")


def pauli_cut_expectation(graph: MaxCutGraph, assignment: Assignment) -> float:
    value = 0.0
    for edge in graph.edges:
        i = graph.node_index(edge.u)
        j = graph.node_index(edge.v)
        value += edge.weight * 0.5 * (1 - z_eigenvalue(assignment[i]) * z_eigenvalue(assignment[j]))
    return value


def minimization_energy(graph: MaxCutGraph, assignment: Assignment) -> float:
    return -pauli_cut_expectation(graph, assignment)


def _pauli_label(node_count: int, left: int | None = None, right: int | None = None) -> str:
    label = ["I"] * node_count
    for qubit in (left, right):
        if qubit is not None:
            label[node_count - 1 - qubit] = "Z"
    return "".join(label)


def build_cut_operator(graph: MaxCutGraph) -> Any:
    SparsePauliOp, _ = require_qiskit_ising()
    terms: list[tuple[str, float]] = []
    for edge in graph.edges:
        i = graph.node_index(edge.u)
        j = graph.node_index(edge.v)
        terms.append((_pauli_label(graph.node_count), edge.weight * 0.5))
        terms.append((_pauli_label(graph.node_count, i, j), -edge.weight * 0.5))
    return SparsePauliOp.from_list(terms).simplify()


def build_minimization_operator(graph: MaxCutGraph) -> Any:
    return (-1.0 * build_cut_operator(graph)).simplify()


def verify_equivalence(graph: MaxCutGraph, tolerance: float = 1e-9) -> list[EquivalenceRow]:
    rows: list[EquivalenceRow] = []
    for assignment in all_assignments(graph):
        direct = cut_value(graph, assignment)
        qubo = qubo_value(graph, assignment)
        pauli = pauli_cut_expectation(graph, assignment)
        energy = minimization_energy(graph, assignment)
        if abs(direct - qubo) > tolerance:
            raise AssertionError(f"QUBO mismatch for {assignment_to_bitstring(assignment)}")
        if abs(direct - pauli) > tolerance:
            raise AssertionError(f"Pauli mismatch for {assignment_to_bitstring(assignment)}")
        if abs(energy + direct) > tolerance:
            bitstring = assignment_to_bitstring(assignment)
            raise AssertionError(f"minimization sign mismatch for {bitstring}")
        rows.append(
            EquivalenceRow(
                bitstring=assignment_to_bitstring(assignment),
                direct_cut=direct,
                qubo_value=qubo,
                pauli_cut_expectation=pauli,
                minimization_energy=energy,
            )
        )
    return rows
