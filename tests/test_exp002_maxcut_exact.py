from __future__ import annotations

import pytest

from quantum_folk_lab.maxcut import (
    CYCLE4,
    MaxCutGraph,
    WeightedEdge,
    assignment_to_bitstring,
    bitstring_to_assignment,
    canonical_pair,
    complement_assignment,
    cut_value,
    get_graph,
    list_graphs,
    qiskit_key_to_assignment,
)
from quantum_folk_lab.maxcut_exact import solve_maxcut_exact
from quantum_folk_lab.maxcut_ising import qubo_value, verify_equivalence


def test_cycle4_graph_registry() -> None:
    assert get_graph("cycle4") == CYCLE4
    assert [graph.name for graph in list_graphs()] == ["cycle4"]
    assert CYCLE4.nodes == (0, 1, 2, 3)
    assert CYCLE4.edge_count == 4
    assert CYCLE4.total_edge_weight == 4.0


def test_graph_validation_rejects_bad_edges() -> None:
    with pytest.raises(ValueError, match="self-loops"):
        WeightedEdge(0, 0)
    with pytest.raises(ValueError, match="duplicate"):
        MaxCutGraph("bad", (0, 1), (WeightedEdge(0, 1), WeightedEdge(1, 0)))
    with pytest.raises(ValueError, match="existing nodes"):
        MaxCutGraph("bad", (0, 1), (WeightedEdge(0, 2),))


def test_cut_value_and_assignment_validation() -> None:
    assert cut_value(CYCLE4, (0, 1, 0, 1)) == 4.0
    assert cut_value(CYCLE4, (1, 0, 1, 0)) == 4.0
    assert cut_value(CYCLE4, (0, 0, 0, 0)) == 0.0
    assert cut_value(CYCLE4, (0, 0, 1, 1)) == 2.0
    with pytest.raises(ValueError, match="assignment length"):
        cut_value(CYCLE4, (0, 1))
    with pytest.raises(ValueError, match="0 or 1"):
        cut_value(CYCLE4, (0, 1, 0, 2))


def test_exact_cycle4_optimum_and_complements() -> None:
    result = solve_maxcut_exact(CYCLE4)
    assert result.maximum_cut == 4.0
    assert result.assignments_enumerated == 16
    assert result.optimal_assignments == ["0101", "1010"]
    assert result.canonical_bitstring == "0101"
    assert result.complementary_bitstring == "1010"
    assert complement_assignment((0, 1, 0, 1)) == (1, 0, 1, 0)
    assert canonical_pair((1, 0, 1, 0)) == ("0101", "1010")


def test_bitstring_and_qiskit_key_conventions() -> None:
    assert assignment_to_bitstring((0, 1, 0, 1)) == "0101"
    assert bitstring_to_assignment("0101") == (0, 1, 0, 1)
    assert qiskit_key_to_assignment("1010") == (0, 1, 0, 1)
    assert qiskit_key_to_assignment("0101") == (1, 0, 1, 0)


def test_qubo_equivalence_does_not_require_qiskit_imports() -> None:
    rows = verify_equivalence(CYCLE4)
    assert len(rows) == 16
    for row in rows:
        assert row.direct_cut == row.qubo_value
        assert row.minimization_energy == -row.direct_cut
    assert qubo_value(CYCLE4, (0, 1, 0, 1)) == 4.0
