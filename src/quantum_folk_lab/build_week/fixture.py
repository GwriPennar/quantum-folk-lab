"""Public adapter for the registered deterministic tune-family fixture."""

from __future__ import annotations

from itertools import combinations

from quantum_folk_lab.domain.synthetic import generate_benchmark
from quantum_folk_lab.similarity.combined import (
    combined_similarity,
    contour_similarity,
    interval_similarity,
    rhythm_similarity,
)
from quantum_folk_lab.tune_family import EXPECTED_TUNE_ORDER, FIXTURE_ID, registered_fixture

from .models import EvidencePair


def fixture_summary() -> dict[str, object]:
    fixture = registered_fixture()
    melodies = generate_benchmark(seed=42, variants_per_family=4)
    if tuple(melody.tune_id for melody in melodies) != EXPECTED_TUNE_ORDER:
        raise AssertionError("registered tune ordering changed")
    return {
        "fixture_identifier": FIXTURE_ID,
        "description": (
            "Eight deterministic synthetic tune variants form a small two-family "
            "partitioning question. Evaluation labels are withheld from optimisation."
        ),
        "tunes": [
            {
                "tune_id": melody.tune_id,
                "event_count": len(melody.events),
                "pitch_offsets": list(melody.pitches),
                "durations": list(melody.durations),
                "transformations": list(melody.transformations),
            }
            for melody in melodies
        ],
        "tau": fixture.tau,
        "lambda": fixture.balance_lambda,
        "graph_threshold": fixture.graph_threshold,
    }


def musical_evidence() -> tuple[EvidencePair, ...]:
    melodies = generate_benchmark(seed=42, variants_per_family=4)
    fixture = registered_fixture()
    edge_pairs = {(edge.left, edge.right) for edge in fixture.graph.edges}
    rows: list[EvidencePair] = []
    for left, right in combinations(range(len(melodies)), 2):
        a, b = melodies[left], melodies[right]
        rows.append(
            EvidencePair(
                left_tune=a.tune_id,
                right_tune=b.tune_id,
                interval_similarity=round(interval_similarity(a, b), 6),
                contour_similarity=round(contour_similarity(a, b), 6),
                rhythm_similarity=round(rhythm_similarity(a, b), 6),
                combined_similarity=round(combined_similarity(a, b), 6),
                graph_edge=(left, right) in edge_pairs,
            )
        )
    return tuple(rows)
