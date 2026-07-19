"""Exact four-bit encoding of the EXP-009A-R2 feasible family selections."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any

TOLERANCE = 1e-12


@dataclass(frozen=True)
class CompactModel:
    """Upper-triangular compact QUBO and equivalent Ising coefficients."""

    offset: float
    qubo: tuple[tuple[float, ...], ...]
    ising_constant: float
    h: tuple[float, ...]
    j: tuple[tuple[float, ...], ...]


def compact_to_r2(bitstring: str) -> str:
    """Map four compact bits to the frozen eight-bit R2 pair ordering."""

    if len(bitstring) != 4 or set(bitstring) - {"0", "1"}:
        raise ValueError("Compact state must contain exactly four binary digits.")
    return "".join("10" if bit == "0" else "01" for bit in bitstring)


def r2_direct_musical_energy(
    compact_bitstring: str,
    variable_order: list[str],
    pair_distances: dict[tuple[str, str], float],
) -> float:
    """Evaluate committed R2 cross-family distances for one compact selection."""

    r2_bits = compact_to_r2(compact_bitstring)
    selected = [variable_order[index] for index, bit in enumerate(r2_bits) if bit == "1"]
    return sum(
        pair_distances.get((left, right), pair_distances[(right, left)])
        if (left, right) not in pair_distances
        else pair_distances[(left, right)]
        for left, right in itertools.combinations(selected, 2)
    )


def derive_compact_model(energy_by_state: dict[str, float]) -> CompactModel:
    """Derive the unique quadratic polynomial from a quadratic four-bit spectrum."""

    expected_states = {f"{value:04b}" for value in range(16)}
    if set(energy_by_state) != expected_states:
        raise ValueError("Compact derivation requires all sixteen states.")
    offset = energy_by_state["0000"]
    linear = []
    for index in range(4):
        state = ["0"] * 4
        state[index] = "1"
        linear.append(energy_by_state["".join(state)] - offset)
    qubo = [[0.0] * 4 for _ in range(4)]
    for index, coefficient in enumerate(linear):
        qubo[index][index] = coefficient
    for left, right in itertools.combinations(range(4), 2):
        state = ["0"] * 4
        state[left] = state[right] = "1"
        qubo[left][right] = energy_by_state["".join(state)] - offset - linear[left] - linear[right]

    ising_constant = offset
    h = [0.0] * 4
    j = [[0.0] * 4 for _ in range(4)]
    for index in range(4):
        coefficient = qubo[index][index]
        ising_constant += coefficient / 2
        h[index] -= coefficient / 2
    for left, right in itertools.combinations(range(4), 2):
        coefficient = qubo[left][right]
        ising_constant += coefficient / 4
        h[left] -= coefficient / 4
        h[right] -= coefficient / 4
        j[left][right] = coefficient / 4
    return CompactModel(
        offset=offset,
        qubo=tuple(tuple(row) for row in qubo),
        ising_constant=ising_constant,
        h=tuple(h),
        j=tuple(tuple(row) for row in j),
    )


def qubo_energy(bitstring: str, model: CompactModel) -> float:
    bits = [int(value) for value in bitstring]
    return model.offset + sum(
        model.qubo[left][right] * bits[left] * bits[right]
        for left in range(4)
        for right in range(left, 4)
    )


def ising_energy(bitstring: str, model: CompactModel) -> float:
    z = [1 - 2 * int(value) for value in bitstring]
    return (
        model.ising_constant
        + sum(model.h[index] * z[index] for index in range(4))
        + sum(
            model.j[left][right] * z[left] * z[right]
            for left, right in itertools.combinations(range(4), 2)
        )
    )


def verify_compact_equivalence(
    variable_order: list[str], pair_distances: dict[tuple[str, str], float]
) -> dict[str, Any]:
    """Verify mapped direct, compact QUBO, and compact Ising energies for all states."""

    direct = {
        state: r2_direct_musical_energy(state, variable_order, pair_distances)
        for state in (f"{value:04b}" for value in range(16))
    }
    model = derive_compact_model(direct)
    mappings: list[dict[str, Any]] = []
    maximum_error = 0.0
    for state in sorted(direct):
        r2_state = compact_to_r2(state)
        mapped = r2_direct_musical_energy(state, variable_order, pair_distances)
        compact_direct = direct[state]
        qubo = qubo_energy(state, model)
        ising = ising_energy(state, model)
        maximum_error = max(
            maximum_error,
            abs(mapped - compact_direct),
            abs(mapped - qubo),
            abs(mapped - ising),
        )
        mappings.append(
            {
                "compact_bitstring": state,
                "r2_bitstring": r2_state,
                "one_hot_valid": all(
                    r2_state[index] != r2_state[index + 1] for index in range(0, 8, 2)
                ),
                "r2_direct_energy": mapped,
                "compact_direct_energy": compact_direct,
                "compact_qubo_energy": qubo,
                "compact_ising_energy": ising,
            }
        )
    if maximum_error > TOLERANCE or not all(item["one_hot_valid"] for item in mappings):
        raise AssertionError("Compact exact-equivalence gate failed.")
    return {"model": model, "mappings": mappings, "maximum_error": maximum_error}
