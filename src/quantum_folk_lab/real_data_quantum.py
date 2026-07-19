"""Exact EXP-009A feature, QUBO, and Ising helpers."""

from __future__ import annotations

import itertools
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

FEATURE_NAMES = (
    "event_count_scaled",
    "range_scaled",
    "ascending_proportion",
    "descending_proportion",
    "repeated_proportion",
    "step_proportion",
    "skip_proportion",
    "leap_proportion",
    "contour_change_rate",
)
ONE_HOT_PENALTY = 7.0
MUSICAL_WEIGHT = 1.0
AGREEMENT_TOLERANCE = 1e-10

_HEADER_RE = re.compile(r"^[A-Za-z]:")
_NOTE_RE = re.compile(
    r"(?:\^{1,2}|_{1,2}|=)?(?P<note>[A-Ga-g])(?P<oct>[,']*)"
    r"(?:\d+(?:/\d*)?|/+)?"
)


class FeatureParseError(ValueError):
    """A non-content-bearing rejection of an unsupported ABC structure."""


@dataclass(frozen=True)
class BinaryModel:
    """Upper-triangular QUBO plus equivalent Ising coefficients."""

    offset: float
    qubo: tuple[tuple[float, ...], ...]
    ising_constant: float
    h: tuple[float, ...]
    j: tuple[tuple[float, ...], ...]


def extract_coarse_features(abc: str) -> dict[str, float]:
    """Extract the frozen nine-feature representation without returning notes."""

    if not abc.strip():
        raise FeatureParseError("Selected record has an empty ABC body.")
    lines = abc.splitlines()
    if any(line.startswith(("W:", "w:")) for line in lines):
        raise FeatureParseError("Selected record contains lyrics.")
    if any(line.startswith("V:") for line in lines) or "[V:" in abc:
        raise FeatureParseError("Selected record contains multiple voices.")
    if abc.count('"') % 2:
        raise FeatureParseError("Selected record has unmatched quoted text.")
    if abc.count("{") != abc.count("}") or abc.count("!") % 2:
        raise FeatureParseError("Selected record has unmatched ornament markup.")

    music_lines = [line.split("%", 1)[0] for line in lines if not _HEADER_RE.match(line.strip())]
    music = "\n".join(music_lines)
    if re.search(r"\[K:[^]]+\]", music):
        raise FeatureParseError("Selected record contains an inline key change.")
    music = re.sub(
        r'"[^"]*"|![^!]*!|\{[^}]*\}|\[[A-JL-ZM-Z]:[^]]*\]',
        "",
        music,
    )

    pitches: list[int] = []
    for match in _NOTE_RE.finditer(music):
        letter = match.group("note")
        octave = int(letter.islower())
        octave += match.group("oct").count("'")
        octave -= match.group("oct").count(",")
        pitches.append("CDEFGAB".index(letter.upper()) + 7 * octave)
    if len(pitches) < 8:
        raise FeatureParseError("Selected record has fewer than eight parsed note events.")

    intervals = [b - a for a, b in zip(pitches, pitches[1:], strict=False)]
    count = len(intervals)
    ascending = sum(value > 0 for value in intervals) / count
    descending = sum(value < 0 for value in intervals) / count
    repeated = sum(value == 0 for value in intervals) / count
    step = sum(abs(value) == 1 for value in intervals) / count
    skip = sum(2 <= abs(value) <= 3 for value in intervals) / count
    leap = sum(abs(value) >= 4 for value in intervals) / count
    directions = [1 if value > 0 else -1 for value in intervals if value]
    changes = sum(a != b for a, b in zip(directions, directions[1:], strict=False))
    change_rate = changes / (len(directions) - 1) if len(directions) > 1 else 0.0

    values = {
        "event_count_scaled": min(len(pitches), 256) / 256,
        "range_scaled": min(max(pitches) - min(pitches), 28) / 28,
        "ascending_proportion": ascending,
        "descending_proportion": descending,
        "repeated_proportion": repeated,
        "step_proportion": step,
        "skip_proportion": skip,
        "leap_proportion": leap,
        "contour_change_rate": change_rate,
    }
    if tuple(values) != FEATURE_NAMES or not all(0 <= value <= 1 for value in values.values()):
        raise AssertionError("Feature contract invariant failed.")
    return values


def feature_distance(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    """Return the frozen uniform-weight squared distance."""

    return sum((left[name] - right[name]) ** 2 for name in FEATURE_NAMES) / len(FEATURE_NAMES)


def build_binary_model(
    features: Sequence[Mapping[str, float]], family_indexes: Sequence[int]
) -> BinaryModel:
    """Construct the frozen upper-triangular QUBO and equivalent Ising model."""

    size = len(features)
    if size != 8 or len(family_indexes) != size:
        raise ValueError("EXP-009A requires exactly eight variables.")
    if sorted(family_indexes).count(0) != 2 or any(
        family_indexes.count(family) != 2 for family in range(4)
    ):
        raise ValueError("EXP-009A requires four families with two settings each.")

    qubo = [[0.0] * size for _ in range(size)]
    for index in range(size):
        qubo[index][index] = -ONE_HOT_PENALTY
    for left, right in itertools.combinations(range(size), 2):
        if family_indexes[left] == family_indexes[right]:
            qubo[left][right] = 2 * ONE_HOT_PENALTY
        else:
            qubo[left][right] = MUSICAL_WEIGHT * feature_distance(features[left], features[right])

    offset = 4 * ONE_HOT_PENALTY
    ising_constant = offset
    h = [0.0] * size
    j = [[0.0] * size for _ in range(size)]
    for index in range(size):
        diagonal = qubo[index][index]
        ising_constant += diagonal / 2
        h[index] -= diagonal / 2
    for left, right in itertools.combinations(range(size), 2):
        coefficient = qubo[left][right]
        ising_constant += coefficient / 4
        h[left] -= coefficient / 4
        h[right] -= coefficient / 4
        j[left][right] = coefficient / 4
    return BinaryModel(
        offset=offset,
        qubo=tuple(tuple(row) for row in qubo),
        ising_constant=ising_constant,
        h=tuple(h),
        j=tuple(tuple(row) for row in j),
    )


def direct_energy(
    bits: Sequence[int],
    features: Sequence[Mapping[str, float]],
    family_indexes: Sequence[int],
) -> float:
    """Evaluate the unexpanded frozen objective."""

    penalty = sum(
        (sum(bits[index] for index, value in enumerate(family_indexes) if value == family) - 1) ** 2
        for family in range(4)
    )
    musical = sum(
        feature_distance(features[left], features[right]) * bits[left] * bits[right]
        for left, right in itertools.combinations(range(8), 2)
        if family_indexes[left] != family_indexes[right]
    )
    return ONE_HOT_PENALTY * penalty + MUSICAL_WEIGHT * musical


def qubo_energy(bits: Sequence[int], model: BinaryModel) -> float:
    """Evaluate the expanded upper-triangular QUBO."""

    return model.offset + sum(
        model.qubo[left][right] * bits[left] * bits[right]
        for left in range(8)
        for right in range(left, 8)
    )


def ising_energy(bits: Sequence[int], model: BinaryModel) -> float:
    """Evaluate the Ising form with z=1-2x."""

    z = [1 - 2 * bit for bit in bits]
    return (
        model.ising_constant
        + sum(model.h[index] * z[index] for index in range(8))
        + sum(
            model.j[left][right] * z[left] * z[right]
            for left, right in itertools.combinations(range(8), 2)
        )
    )


def enumerate_exact(
    features: Sequence[Mapping[str, float]], family_indexes: Sequence[int]
) -> dict[str, Any]:
    """Enumerate all 256 assignments and verify three energy representations."""

    model = build_binary_model(features, family_indexes)
    states: list[tuple[str, float, bool]] = []
    maximum_error = 0.0
    for bits in itertools.product((0, 1), repeat=8):
        direct = direct_energy(bits, features, family_indexes)
        qubo = qubo_energy(bits, model)
        ising = ising_energy(bits, model)
        maximum_error = max(maximum_error, abs(direct - qubo), abs(direct - ising))
        feasible = all(
            sum(bits[index] for index, value in enumerate(family_indexes) if value == family) == 1
            for family in range(4)
        )
        states.append(("".join(map(str, bits)), direct, feasible))
    if maximum_error > AGREEMENT_TOLERANCE:
        raise AssertionError("Direct/QUBO/Ising agreement gate failed.")

    minimum = min(energy for _, energy, _ in states)
    optima = sorted(
        bitstring for bitstring, energy, _ in states if math.isclose(energy, minimum, abs_tol=1e-12)
    )
    non_optimal = sorted(
        {energy for _, energy, _ in states if not math.isclose(energy, minimum, abs_tol=1e-12)}
    )
    levels = sorted({round(energy, 12) for _, energy, _ in states})
    return {
        "assignment_count": 256,
        "agreement_tolerance": AGREEMENT_TOLERANCE,
        "maximum_agreement_error": maximum_error,
        "optimum_bitstrings": optima,
        "canonical_optimum": optima[0],
        "minimum_energy": minimum,
        "displayed_minimum_energy": round(minimum, 12),
        "distinct_energy_levels": len(levels),
        "gap_to_next_non_optimal": non_optimal[0] - minimum,
        "all_optima_feasible": all(
            feasible for bitstring, _, feasible in states if bitstring in optima
        ),
        "minimum_infeasible_energy": min(energy for _, energy, feasible in states if not feasible),
        "uniform_optimum_class_baseline": len(optima) / 256,
        "states": states,
        "model": model,
    }
