from quantum_folk_lab.classical.exact import solve_exact
from quantum_folk_lab.domain.synthetic import generate_benchmark
from quantum_folk_lab.evaluation.metrics import family_recovery
from quantum_folk_lab.graph.build import build_similarity_graph
from quantum_folk_lab.qubo.two_family import build_two_family_qubo


def test_exact_solver_recovers_families() -> None:
    graph = build_similarity_graph(generate_benchmark())
    result = solve_exact(build_two_family_qubo(graph))
    assert result.energy >= -1e-9
    assert family_recovery(result.bits, graph.labels) >= 0.75
