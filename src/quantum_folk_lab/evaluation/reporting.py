from __future__ import annotations

from quantum_folk_lab.evaluation.metrics import family_recovery
from quantum_folk_lab.graph.build import SimilarityGraph


def summarize(bits: tuple[int, ...], graph: SimilarityGraph) -> dict[str, object]:
    return {"bits": bits, "family_recovery": family_recovery(bits, graph.labels)}
