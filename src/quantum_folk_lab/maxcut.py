from __future__ import annotations

from dataclasses import dataclass
from itertools import product

Assignment = tuple[int, ...]


@dataclass(frozen=True)
class WeightedEdge:
    u: int
    v: int
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.u == self.v:
            raise ValueError("self-loops are not supported")
        if self.weight <= 0:
            raise ValueError("edge weights must be positive")


@dataclass(frozen=True)
class MaxCutGraph:
    name: str
    nodes: tuple[int, ...]
    edges: tuple[WeightedEdge, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("graph name must not be empty")
        if len(set(self.nodes)) != len(self.nodes):
            raise ValueError("nodes must be unique")
        node_set = set(self.nodes)
        seen: set[tuple[int, int]] = set()
        for edge in self.edges:
            if edge.u not in node_set or edge.v not in node_set:
                raise ValueError("edges must reference existing nodes")
            key = (min(edge.u, edge.v), max(edge.u, edge.v))
            if key in seen:
                raise ValueError("duplicate undirected edges are not supported")
            seen.add(key)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def total_edge_weight(self) -> float:
        return sum(edge.weight for edge in self.edges)

    def node_index(self, node: int) -> int:
        try:
            return self.nodes.index(node)
        except ValueError as exc:
            raise ValueError(f"unknown node {node!r}") from exc

    def metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "nodes": list(self.nodes),
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "total_edge_weight": self.total_edge_weight,
            "edges": [[edge.u, edge.v, edge.weight] for edge in self.edges],
        }


CYCLE4 = MaxCutGraph(
    name="cycle4",
    nodes=(0, 1, 2, 3),
    edges=(
        WeightedEdge(0, 1, 1.0),
        WeightedEdge(1, 2, 1.0),
        WeightedEdge(2, 3, 1.0),
        WeightedEdge(3, 0, 1.0),
    ),
)

GRAPHS: dict[str, MaxCutGraph] = {CYCLE4.name: CYCLE4}


def list_graphs() -> tuple[MaxCutGraph, ...]:
    return tuple(GRAPHS[name] for name in sorted(GRAPHS))


def get_graph(name: str) -> MaxCutGraph:
    try:
        return GRAPHS[name]
    except KeyError as exc:
        valid = ", ".join(sorted(GRAPHS))
        raise ValueError(f"unknown Max-Cut graph {name!r}; choose one of: {valid}") from exc


def validate_assignment(graph: MaxCutGraph, assignment: Assignment) -> Assignment:
    if len(assignment) != graph.node_count:
        raise ValueError(f"assignment length must be {graph.node_count}")
    if any(bit not in (0, 1) for bit in assignment):
        raise ValueError("assignment bits must be 0 or 1")
    return assignment


def assignment_to_bitstring(assignment: Assignment) -> str:
    if any(bit not in (0, 1) for bit in assignment):
        raise ValueError("assignment bits must be 0 or 1")
    return "".join(str(bit) for bit in assignment)


def bitstring_to_assignment(bitstring: str) -> Assignment:
    if not bitstring or any(bit not in "01" for bit in bitstring):
        raise ValueError("bitstring must contain only 0 and 1")
    return tuple(int(bit) for bit in bitstring)


def qiskit_key_to_assignment(key: str) -> Assignment:
    compact = key.replace(" ", "")
    return bitstring_to_assignment(compact[::-1])


def assignment_to_qiskit_key(assignment: Assignment) -> str:
    return assignment_to_bitstring(assignment[::-1])


def complement_assignment(assignment: Assignment) -> Assignment:
    return tuple(1 - bit for bit in assignment)


def canonical_pair(assignment: Assignment) -> tuple[str, str]:
    bitstring = assignment_to_bitstring(assignment)
    complement = assignment_to_bitstring(complement_assignment(assignment))
    return (bitstring, complement) if bitstring <= complement else (complement, bitstring)


def all_assignments(graph: MaxCutGraph) -> tuple[Assignment, ...]:
    return tuple(product((0, 1), repeat=graph.node_count))


def cut_value(graph: MaxCutGraph, assignment: Assignment) -> float:
    validate_assignment(graph, assignment)
    value = 0.0
    for edge in graph.edges:
        u_index = graph.node_index(edge.u)
        v_index = graph.node_index(edge.v)
        if assignment[u_index] != assignment[v_index]:
            value += edge.weight
    return value


def decode_counts(counts: dict[str, int]) -> dict[str, int]:
    decoded: dict[str, int] = {}
    for key, count in counts.items():
        bitstring = assignment_to_bitstring(qiskit_key_to_assignment(key))
        decoded[bitstring] = decoded.get(bitstring, 0) + int(count)
    return dict(sorted(decoded.items()))
