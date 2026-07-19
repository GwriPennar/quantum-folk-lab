"""Pure read models for the exact landscape and registered QAOA evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from quantum_folk_lab.tune_family import (
    CANONICAL_OPTIMUM,
    EXPECTED_OPTIMA,
    FIXTURE_ID,
    all_assignments,
    bitstring_from_bits,
    complement_bits,
    registered_fixture,
    solve_registered_exact,
    verify_direct_qubo,
    verify_qubo_ising,
)

DISPLAY_ZERO_TOLERANCE = 1e-12
ENERGY_COMPARISON_TOLERANCE = 1e-9


@dataclass(frozen=True)
class LandscapeEntry:
    assignment: str
    integer_index: int
    row_bits: str
    column_bits: str
    energy: float
    display_energy: float
    energy_rank: int
    is_global_optimum: bool
    is_canonical_representative: bool
    complement: str
    hamming_weight: int
    marker: str

    def to_dict(self) -> dict[str, object]:
        return {
            "assignment": self.assignment,
            "integer_index": self.integer_index,
            "row_bits": self.row_bits,
            "column_bits": self.column_bits,
            "energy": self.energy,
            "display_energy": self.display_energy,
            "energy_rank": self.energy_rank,
            "is_global_optimum": self.is_global_optimum,
            "is_canonical_representative": self.is_canonical_representative,
            "complement": self.complement,
            "hamming_weight": self.hamming_weight,
            "marker": self.marker,
        }


@dataclass(frozen=True)
class ExactLandscape:
    fixture_identifier: str
    variable_count: int
    entries: tuple[LandscapeEntry, ...]
    global_optima: tuple[str, ...]
    canonical_representative: str
    raw_minimum_energy: float
    display_minimum_energy: float
    distinct_energy_levels: int
    next_best_energy: float
    optimum_to_next_gap: float
    complement_symmetry_verified: bool
    direct_qubo_verified_assignments: int
    qubo_ising_verified_assignments: int

    def chart_rows(self) -> list[dict[str, object]]:
        return [entry.to_dict() for entry in self.entries]


@dataclass(frozen=True)
class RegisteredQAOAEvidence:
    experiment_identifier: str
    fixture_identifier: str
    depth: int
    shots: int
    optimiser: str
    optimiser_max_iterations: int
    initial_point_count: int
    sampler_seed: int
    estimator_seed: int
    transpile_seed: int
    canonical_count: int
    complement_count: int
    optimum_class_count: int
    canonical_probability: float
    complement_probability: float
    optimum_class_probability: float
    uniform_optimum_class_probability: float


def _display_energy(energy: float) -> float:
    return 0.0 if abs(energy) < DISPLAY_ZERO_TOLERANCE else energy


def build_exact_landscape() -> ExactLandscape:
    """Build all 256 states through the registered, validated project objective."""

    fixture = registered_fixture()
    direct_qubo = verify_direct_qubo()
    qubo_ising = verify_qubo_ising()
    exact = solve_registered_exact(fixture)
    raw_rows = [
        (bits, fixture.model.energy(bits)) for bits in all_assignments(len(fixture.model.variables))
    ]
    energy_levels = sorted({round(energy, 9) for _, energy in raw_rows})
    ranks = {energy: rank for rank, energy in enumerate(energy_levels, start=1)}
    optimum_set = set(exact.exact_optimal_bitstrings)
    entries: list[LandscapeEntry] = []
    complement_symmetry_verified = True
    energy_by_assignment = {bitstring_from_bits(bits): energy for bits, energy in raw_rows}
    for bits, energy in raw_rows:
        assignment = bitstring_from_bits(bits)
        complement = bitstring_from_bits(complement_bits(bits))
        if abs(energy - energy_by_assignment[complement]) > ENERGY_COMPARISON_TOLERANCE:
            complement_symmetry_verified = False
        is_optimum = assignment in optimum_set
        is_canonical = assignment == exact.canonical_optimum
        entries.append(
            LandscapeEntry(
                assignment=assignment,
                integer_index=int(assignment, 2),
                row_bits=assignment[:4],
                column_bits=assignment[4:],
                energy=energy,
                display_energy=_display_energy(energy),
                energy_rank=ranks[round(energy, 9)],
                is_global_optimum=is_optimum,
                is_canonical_representative=is_canonical,
                complement=complement,
                hamming_weight=sum(bits),
                marker="C" if is_canonical else "E" if is_optimum else "",
            )
        )
    next_best = next(
        level
        for level in energy_levels
        if level > exact.exact_minimum_energy + ENERGY_COMPARISON_TOLERANCE
    )
    display_minimum = _display_energy(exact.exact_minimum_energy)
    if not complement_symmetry_verified:
        raise AssertionError("registered landscape lost complement symmetry")
    if tuple(exact.exact_optimal_bitstrings) != EXPECTED_OPTIMA:
        raise AssertionError("registered optimum set changed")
    return ExactLandscape(
        fixture_identifier=fixture.fixture_id,
        variable_count=len(fixture.model.variables),
        entries=tuple(entries),
        global_optima=tuple(exact.exact_optimal_bitstrings),
        canonical_representative=exact.canonical_optimum,
        raw_minimum_energy=exact.exact_minimum_energy,
        display_minimum_energy=display_minimum,
        distinct_energy_levels=len(energy_levels),
        next_best_energy=next_best,
        optimum_to_next_gap=next_best - display_minimum,
        complement_symmetry_verified=True,
        direct_qubo_verified_assignments=direct_qubo.verified_assignments,
        qubo_ising_verified_assignments=qubo_ising.verified_assignments,
    )


def parse_registered_qaoa_evidence(
    payload: Mapping[str, Any],
) -> RegisteredQAOAEvidence:
    """Validate and reduce the tracked EXP-005A result for presentation."""

    exact = dict(payload["exact"])
    sampled = dict(payload["sampled"])
    config = dict(payload["qaoa_configuration"])
    counts = {str(key): int(value) for key, value in dict(payload["measurement_counts"]).items()}
    fixture_identifier = str(payload["fixture_identifier"])
    if fixture_identifier != FIXTURE_ID:
        raise ValueError("registered QAOA fixture changed")
    if tuple(str(value) for value in exact["exact_optimal_bitstrings"]) != EXPECTED_OPTIMA:
        raise ValueError("registered QAOA optimum set changed")
    shots = int(config["shots"])
    canonical_count = counts.get(CANONICAL_OPTIMUM, 0)
    complement = EXPECTED_OPTIMA[1]
    complement_count = counts.get(complement, 0)
    optimum_class_count = canonical_count + complement_count
    optimum_probability = optimum_class_count / shots
    recorded_probability = float(sampled["optimal_complement_class_probability"])
    if abs(recorded_probability - optimum_probability) > 1e-12:
        raise ValueError("registered optimum-class probability is inconsistent")
    uniform_probability = len(EXPECTED_OPTIMA) / (2 ** len(CANONICAL_OPTIMUM))
    return RegisteredQAOAEvidence(
        experiment_identifier=str(payload["experiment_id"]),
        fixture_identifier=fixture_identifier,
        depth=int(config["depth"]),
        shots=shots,
        optimiser=str(config["optimiser"]),
        optimiser_max_iterations=int(config["optimiser_max_iterations"]),
        initial_point_count=len(list(config["initial_points"])),
        sampler_seed=int(config["sampler_seed"]),
        estimator_seed=int(config["estimator_seed"]),
        transpile_seed=int(config["transpile_seed"]),
        canonical_count=canonical_count,
        complement_count=complement_count,
        optimum_class_count=optimum_class_count,
        canonical_probability=canonical_count / shots,
        complement_probability=complement_count / shots,
        optimum_class_probability=optimum_probability,
        uniform_optimum_class_probability=uniform_probability,
    )
