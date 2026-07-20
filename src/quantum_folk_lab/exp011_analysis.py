"""Frozen EXP-011 analysis; independent of IBM Runtime and submission code."""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from statistics import fmean

SEED = 20260720


def average_ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + 1 + end) / 2
        for position in range(start, end):
            ranks[order[position]] = rank
        start = end
    return ranks


def pearson(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("paired vectors must have equal length >= 2")
    left_mean, right_mean = fmean(left), fmean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right, strict=True))
    left_ss = sum((a - left_mean) ** 2 for a in left)
    right_ss = sum((b - right_mean) ** 2 for b in right)
    if left_ss == 0 or right_ss == 0:
        raise ValueError("Spearman correlation undefined for constant ranks")
    return numerator / (left_ss * right_ss) ** 0.5


def spearman(left: Sequence[float], right: Sequence[float]) -> float:
    return pearson(average_ranks(left), average_ranks(right))


def classify(rho: float, p_value: float) -> str:
    if rho >= 0.80 and p_value < 0.01:
        return "STRONGLY REPLICATED"
    if rho >= 0.50 and p_value < 0.05:
        return "REPLICATED"
    if rho > 0:
        return "WEAK OR INCONCLUSIVE"
    return "NOT REPLICATED"


def permutation_p_value(
    ideal: Sequence[float],
    hardware: Sequence[float],
    permutations: int = 100_000,
) -> tuple[float, float]:
    observed = spearman(ideal, hardware)
    shuffled = list(hardware)
    rng = random.Random(SEED)
    exceedances = 0
    for _ in range(permutations):
        rng.shuffle(shuffled)
        if spearman(ideal, shuffled) >= observed:
            exceedances += 1
    return observed, (1 + exceedances) / (permutations + 1)


def aggregate_centres(rows: Sequence[Mapping[str, object]]) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for row in rows:
        grouped.setdefault(str(row["point_id"]), []).append(float(row["r"]))
    return {point_id: fmean(values) for point_id, values in grouped.items()}
