from itertools import product

from quantum_folk_lab.domain.synthetic import generate_benchmark
from quantum_folk_lab.graph.build import build_similarity_graph
from quantum_folk_lab.qubo.two_family import build_two_family_qubo, direct_objective


def test_qubo_matches_direct_objective() -> None:
    graph = build_similarity_graph(generate_benchmark())
    model = build_two_family_qubo(graph)
    for bits in product((0, 1), repeat=len(model.variables)):
        assert abs(model.energy(bits) - direct_objective(bits, graph)) < 1e-9
