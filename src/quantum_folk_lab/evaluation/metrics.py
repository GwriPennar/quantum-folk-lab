from __future__ import annotations


def family_recovery(
    predicted: tuple[int, ...] | list[int], expected: tuple[int, ...] | list[int]
) -> float:
    if len(predicted) != len(expected):
        raise ValueError("label lengths differ")
    same = sum(int(a == b) for a, b in zip(predicted, expected, strict=True)) / len(expected)
    flipped = sum(int((1 - a) == b) for a, b in zip(predicted, expected, strict=True)) / len(
        expected
    )
    return max(same, flipped)


def approximation_ratio(value: float, optimum: float) -> float:
    if optimum == 0:
        return 1.0 if value == 0 else 0.0
    return optimum / value
