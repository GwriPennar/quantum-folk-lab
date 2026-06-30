from __future__ import annotations

from quantum_folk_lab.domain.models import Melody

from .intervals import normalized_edit_similarity


def interval_similarity(left: Melody, right: Melody) -> float:
    return normalized_edit_similarity(left.intervals, right.intervals)


def contour_similarity(left: Melody, right: Melody) -> float:
    return normalized_edit_similarity(left.contour, right.contour)


def rhythm_similarity(left: Melody, right: Melody) -> float:
    return normalized_edit_similarity(left.durations, right.durations)


def combined_similarity(
    left: Melody, right: Melody, weights: tuple[float, float, float] = (0.5, 0.3, 0.2)
) -> float:
    total = sum(weights)
    if total <= 0:
        raise ValueError("weights must have positive sum")
    scores = (
        interval_similarity(left, right),
        contour_similarity(left, right),
        rhythm_similarity(left, right),
    )
    value = sum(weight * score for weight, score in zip(weights, scores, strict=True)) / total
    return max(0.0, min(1.0, value))
