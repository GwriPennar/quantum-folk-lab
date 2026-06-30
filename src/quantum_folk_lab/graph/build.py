from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from quantum_folk_lab.domain.models import Melody
from quantum_folk_lab.similarity.combined import combined_similarity


@dataclass(frozen=True)
class WeightedEdge:
    left: int
    right: int
    weight: float


@dataclass(frozen=True)
class SimilarityGraph:
    tune_ids: tuple[str, ...]
    labels: tuple[int, ...]
    edges: tuple[WeightedEdge, ...]


def build_similarity_graph(melodies: list[Melody], threshold: float = 0.45) -> SimilarityGraph:
    families = {family: index for index, family in enumerate(sorted({m.family for m in melodies}))}
    edges = []
    for i, j in combinations(range(len(melodies)), 2):
        weight = combined_similarity(melodies[i], melodies[j])
        if weight >= threshold or weight <= 0.25:
            edges.append(WeightedEdge(i, j, round(weight, 6)))
    return SimilarityGraph(
        tuple(m.tune_id for m in melodies),
        tuple(families[m.family] for m in melodies),
        tuple(edges),
    )
