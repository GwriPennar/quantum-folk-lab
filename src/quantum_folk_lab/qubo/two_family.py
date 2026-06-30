from __future__ import annotations

from quantum_folk_lab.graph.build import SimilarityGraph

from .model import QUBOModel


def direct_objective(
    bits: tuple[int, ...],
    graph: SimilarityGraph,
    dissimilar_threshold: float = 0.25,
    balance: float = 0.1,
) -> float:
    value = 0.0
    for edge in graph.edges:
        different = bits[edge.left] + bits[edge.right] - 2 * bits[edge.left] * bits[edge.right]
        same = 1 - different
        if edge.weight >= dissimilar_threshold:
            value += edge.weight * different
        else:
            value += (1.0 - edge.weight) * same
    target = len(bits) / 2
    value += balance * (sum(bits) - target) ** 2
    return value


def build_two_family_qubo(
    graph: SimilarityGraph, dissimilar_threshold: float = 0.25, balance: float = 0.1
) -> QUBOModel:
    variables = tuple(f"x_{i}_{name}" for i, name in enumerate(graph.tune_ids))
    linear = dict.fromkeys(variables, 0.0)
    quadratic: dict[tuple[str, str], float] = {}
    offset = balance * (len(variables) / 2) ** 2
    for edge in graph.edges:
        a, b = variables[edge.left], variables[edge.right]
        if edge.weight >= dissimilar_threshold:
            linear[a] += edge.weight
            linear[b] += edge.weight
            quadratic[(a, b)] = quadratic.get((a, b), 0.0) - 2 * edge.weight
        else:
            penalty = 1.0 - edge.weight
            offset += penalty
            linear[a] -= penalty
            linear[b] -= penalty
            quadratic[(a, b)] = quadratic.get((a, b), 0.0) + 2 * penalty
    for a in variables:
        linear[a] += balance * (1 - len(variables))
    for i, a in enumerate(variables):
        for b in variables[i + 1 :]:
            quadratic[(a, b)] = quadratic.get((a, b), 0.0) + 2 * balance
    return QUBOModel(
        variables,
        linear,
        quadratic,
        offset,
        {"balance": balance, "dissimilar_threshold": dissimilar_threshold},
    )
