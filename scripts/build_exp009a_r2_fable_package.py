"""Build the EXP-009A-R2 local detectability and Fable evidence package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr  # type: ignore[import-untyped]

RESAMPLES = 10_000
SHOTS = 4096
SEED = 42
POWER_THRESHOLD = 0.80


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _qubo_energy(bitstring: str, qubo: dict[str, Any]) -> float:
    bits = [int(value) for value in bitstring]
    return float(qubo["offset"]) + sum(
        float(qubo["matrix"][left][right]) * bits[left] * bits[right]
        for left in range(8)
        for right in range(left, 8)
    )


def _is_feasible(bitstring: str) -> bool:
    return all(bitstring[index] != bitstring[index + 1] for index in range(0, 8, 2))


def _summarize(values: np.ndarray) -> dict[str, float]:
    quantiles = np.quantile(values, [0.025, 0.5, 0.975])
    return {
        "q025": float(quantiles[0]),
        "median": float(quantiles[1]),
        "q975": float(quantiles[2]),
        "standard_deviation": float(np.std(values, ddof=1)),
    }


def _rank_correlations(
    counts: np.ndarray, feasible_indexes: np.ndarray, feasible_energies: np.ndarray
) -> np.ndarray:
    values = np.empty(len(counts), dtype=float)
    for index, row in enumerate(counts[:, feasible_indexes]):
        statistic = spearmanr(feasible_energies, row).statistic
        values[index] = 0.0 if np.isnan(statistic) else float(statistic)
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()

    exact = json.loads((args.evidence_dir / "exact-result.json").read_text(encoding="utf-8"))
    qubo = json.loads((args.evidence_dir / "qubo.json").read_text(encoding="utf-8"))
    qaoa = json.loads((args.evidence_dir / "qaoa-result.json").read_text(encoding="utf-8"))

    states = [f"{index:08b}" for index in range(256)]
    energies = np.array([_qubo_energy(state, qubo) for state in states])
    feasible_mask = np.array([_is_feasible(state) for state in states])
    optimum_mask = np.array([state in exact["optimum_bitstrings"] for state in states])
    four_lowest = set(qaoa["four_lowest_feasible_bitstrings"])
    low_mask = np.array([state in four_lowest for state in states])
    ideal_probabilities = np.array([qaoa["ideal_distribution"].get(state, 0.0) for state in states])
    ideal_probabilities /= ideal_probabilities.sum()
    uniform_probabilities = np.full(256, 1 / 256)

    rng = np.random.default_rng(SEED)
    alternative_counts = rng.multinomial(SHOTS, ideal_probabilities, size=RESAMPLES)
    null_counts = rng.multinomial(SHOTS, uniform_probabilities, size=RESAMPLES)
    alternative_probabilities = alternative_counts / SHOTS
    null_probabilities = null_counts / SHOTS
    feasible_indexes = np.flatnonzero(feasible_mask)
    feasible_energies = energies[feasible_indexes]

    metrics: dict[str, dict[str, Any]] = {}
    definitions = {
        "feasible_subspace_mass": (
            alternative_probabilities[:, feasible_mask].sum(axis=1),
            null_probabilities[:, feasible_mask].sum(axis=1),
            "higher",
        ),
        "optimum_class_mass": (
            alternative_probabilities[:, optimum_mask].sum(axis=1),
            null_probabilities[:, optimum_mask].sum(axis=1),
            "higher",
        ),
        "four_lowest_feasible_mass": (
            alternative_probabilities[:, low_mask].sum(axis=1),
            null_probabilities[:, low_mask].sum(axis=1),
            "higher",
        ),
        "expected_energy": (
            alternative_probabilities @ energies,
            null_probabilities @ energies,
            "lower",
        ),
        "feasible_energy_probability_spearman": (
            _rank_correlations(alternative_counts, feasible_indexes, feasible_energies),
            _rank_correlations(null_counts, feasible_indexes, feasible_energies),
            "lower",
        ),
    }
    for name, (alternative, null, direction) in definitions.items():
        quantile = 0.95 if direction == "higher" else 0.05
        critical = float(np.quantile(null, quantile))
        power = float(
            np.mean(alternative > critical if direction == "higher" else alternative < critical)
        )
        metrics[name] = {
            "favorable_direction": direction,
            "null_critical_value": critical,
            "alternative_uncertainty": _summarize(alternative),
            "estimated_power": power,
            "detectable_at_power_0_80": power >= POWER_THRESHOLD,
        }

    detectability = {
        "protocol": {
            "resamples": RESAMPLES,
            "shots_per_resample": SHOTS,
            "seed": SEED,
            "null": "uniform distribution over all 256 states",
            "alternative": "frozen ideal p=1 local-QAOA distribution",
            "significance_level": 0.05,
            "detectability_power_threshold": POWER_THRESHOLD,
        },
        "metrics": metrics,
        "primary_hardware_metric_selected": False,
    }
    _write_json(args.evidence_dir / "detectability-result.json", detectability)

    fable = {
        "experiment_id": "EXP-009A-R2",
        "purpose": "non-sensitive evidence for Fable hardware-design revision",
        "variable_order": qubo["variable_order"],
        "qubo_coefficient_sha256": exact["qubo_coefficient_sha256"],
        "ising_coefficient_sha256": exact["ising_coefficient_sha256"],
        "optimum_bitstrings": exact["optimum_bitstrings"],
        "canonical_optimum": exact["canonical_optimum"],
        "spectrum": {
            "distinct_energy_levels": exact["distinct_energy_levels"],
            "minimum_energy": exact["minimum_energy"],
            "gap_to_next_non_optimal": exact["gap_to_next_non_optimal"],
            "minimum_infeasible_energy": exact["minimum_infeasible_energy"],
        },
        "feasible_state_energies": exact["feasible_state_energies"],
        "ideal_p1_distribution": qaoa["ideal_distribution"],
        "shot_4096_distribution": qaoa["shot_distribution"],
        "gamma": qaoa["gamma"],
        "beta": qaoa["beta"],
        "metrics": {
            "ideal_optimum_class_mass": qaoa["ideal_optimum_class_mass"],
            "shot_optimum_class_mass": qaoa["shot_optimum_class_mass"],
            "ideal_feasible_subspace_mass": qaoa["ideal_feasible_subspace_mass"],
            "shot_feasible_subspace_mass": qaoa["shot_feasible_subspace_mass"],
            "ideal_expected_energy": qaoa["ideal_expected_energy"],
            "shot_expected_energy": qaoa["shot_expected_energy"],
            "ideal_four_lowest_feasible_mass": qaoa["ideal_four_lowest_feasible_mass"],
            "shot_four_lowest_feasible_mass": qaoa["shot_four_lowest_feasible_mass"],
            "ideal_feasible_energy_probability_spearman": qaoa[
                "ideal_feasible_energy_probability_spearman"
            ],
            "shot_feasible_energy_probability_spearman": qaoa[
                "shot_feasible_energy_probability_spearman"
            ],
        },
        "uniform_baselines": qaoa["uniform_baselines"],
        "spectrum_degeneracy_assessment": {
            "optimum_class_size": exact["optimum_class_size"],
            "optimum_mass_metric_degeneracy_weakened": qaoa[
                "optimum_mass_metric_is_degeneracy_weakened"
            ],
            "within_feasible_distribution_nearly_uniform": True,
        },
        "estimated_4096_shot_variability": {
            name: result["alternative_uncertainty"] for name, result in metrics.items()
        },
        "logical_width": qaoa["logical_width"],
        "untranspiled_p1_two_qubit_interaction_count": qaoa[
            "untranspiled_nonzero_two_qubit_interaction_count"
        ],
        "detectability": detectability,
        "hardware_contacted": False,
        "primary_hardware_metric_selected": False,
    }
    _write_json(args.evidence_dir / "fable-hardware-inputs.json", fable)

    detectable = [name for name, result in metrics.items() if result["detectable_at_power_0_80"]]
    not_detectable = [
        name for name, result in metrics.items() if not result["detectable_at_power_0_80"]
    ]
    interaction_count = fable["untranspiled_p1_two_qubit_interaction_count"]
    ideal_rank_statistic = qaoa["ideal_feasible_energy_probability_spearman"]["statistic"]
    detectable_text = ", ".join(detectable) if detectable else "none"
    not_detectable_text = ", ".join(not_detectable) if not_detectable else "none"
    report = f"""# Fable hardware-design inputs

This package contains validated local evidence for revising the proposed “Four Families, One
Quantum Job” design. It does not choose a primary hardware metric and does not authorize IBM access.

## Exact and local summary

- Logical width: 8 qubits.
- Untranspiled p=1 nonzero two-qubit interactions: {interaction_count}.
- Exact optimum: `{exact["canonical_optimum"]}`; class size {exact["optimum_class_size"]}.
- Exact gap: `{exact["gap_to_next_non_optimal"]}`.
- Frozen β: `{qaoa["beta"]}`; frozen γ: `{qaoa["gamma"]}`.
- Ideal feasible mass: `{qaoa["ideal_feasible_subspace_mass"]}`.
- Ideal optimum mass: `{qaoa["ideal_optimum_class_mass"]}`.
- Ideal four-lowest-feasible mass: `{qaoa["ideal_four_lowest_feasible_mass"]}`.
- Ideal feasible energy/probability Spearman ρ: `{ideal_rank_statistic}`.

The ideal distribution is nearly uniform within the feasible subspace. Feasibility concentration is
strong, while within-feasible energy ordering is not favorable.

## Preregistered 4096-shot detectability

- Detectable at estimated power ≥ 0.80: {detectable_text}.
- Not detectable at estimated power ≥ 0.80: {not_detectable_text}.

Mass metrics may be detectable primarily because the circuit concentrates on the constrained
subspace; detectability alone does not make them scientifically primary. Fable should use these
results to revise the protocol before any separately authorized hardware activity.

No IBM Runtime client, backend, credential, session, simulator service, or QPU was contacted.
"""
    (args.evidence_dir / "FABLE-HARDWARE-INPUTS.md").write_text(report, encoding="utf-8")
    readiness = """# EXP-009A-R2 hardware readiness

The parser, exact, local-QAOA, and preregistered detectability evidence are complete. The local
distribution is nearly uniform inside the feasible subspace, so Fable must revise metric selection
and interpretation before proposing any hardware protocol.

This readiness state authorizes neither IBM access nor hardware submission. No hardware was
contacted in EXP-009A-R2.

`READY TO RETURN TO FABLE FOR EXP-009B DESIGN REVISION`
"""
    (args.evidence_dir / "HARDWARE-READINESS.md").write_text(readiness, encoding="utf-8")
    print("EXP-009A-R2 Fable package built; no hardware contacted.")


if __name__ == "__main__":
    main()
