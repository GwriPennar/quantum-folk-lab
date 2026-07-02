from __future__ import annotations

import time
from dataclasses import asdict, dataclass

from quantum_folk_lab.maxcut import (
    Assignment,
    MaxCutGraph,
    all_assignments,
    assignment_to_bitstring,
    canonical_pair,
    complement_assignment,
    cut_value,
)


@dataclass(frozen=True)
class MaxCutExactResult:
    graph_name: str
    node_count: int
    edge_count: int
    total_edge_weight: float
    graph_edges: list[list[float]]
    maximum_cut: float
    optimal_assignments: list[str]
    assignments_enumerated: int
    canonical_bitstring: str
    complementary_bitstring: str
    elapsed_seconds: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def solve_maxcut_exact(graph: MaxCutGraph) -> MaxCutExactResult:
    start = time.perf_counter()
    best_value = float("-inf")
    best_assignments: list[Assignment] = []
    assignments = all_assignments(graph)
    for assignment in assignments:
        value = cut_value(graph, assignment)
        if value > best_value:
            best_value = value
            best_assignments = [assignment]
        elif value == best_value:
            best_assignments.append(assignment)
    bitstrings = sorted(assignment_to_bitstring(assignment) for assignment in best_assignments)
    canonical = bitstrings[0]
    canonical_assignment = tuple(int(bit) for bit in canonical)
    complement = assignment_to_bitstring(complement_assignment(canonical_assignment))
    if complement not in bitstrings:
        pair = canonical_pair(best_assignments[0])
        canonical, complement = pair
    elapsed = time.perf_counter() - start
    return MaxCutExactResult(
        graph_name=graph.name,
        node_count=graph.node_count,
        edge_count=graph.edge_count,
        total_edge_weight=graph.total_edge_weight,
        graph_edges=[[edge.u, edge.v, edge.weight] for edge in graph.edges],
        maximum_cut=best_value,
        optimal_assignments=bitstrings,
        assignments_enumerated=len(assignments),
        canonical_bitstring=min(canonical, complement),
        complementary_bitstring=max(canonical, complement),
        elapsed_seconds=round(elapsed, 6),
    )
