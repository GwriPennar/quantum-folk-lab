"""Run the frozen EXP-010A compact p=1 QAOA and detectability protocol."""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize  # type: ignore[import-untyped]
from scipy.stats import spearmanr  # type: ignore[import-untyped]

from quantum_folk_lab.simulation import package_version

GAMMA_POINTS = 257
BETA_POINTS = 129
REFINEMENT_STARTS = 16
SHOTS = 4096
SEED = 42
RESAMPLES = 10_000
GAMMA_BOUNDS = (0.0, 16 * math.pi)
BETA_BOUNDS = (0.0, math.pi)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _mixer(beta: float) -> np.ndarray:
    single = np.array(
        [[math.cos(beta), -1j * math.sin(beta)], [-1j * math.sin(beta), math.cos(beta)]],
        dtype=complex,
    )
    result = np.array([[1.0 + 0.0j]])
    for _ in range(4):
        result = np.kron(result, single)
    return result


def _distribution(gamma: float, beta: float, normalized_energies: np.ndarray) -> np.ndarray:
    phased = np.exp(-1j * gamma * normalized_energies) / 4
    amplitudes = _mixer(beta) @ phased
    return np.abs(amplitudes) ** 2


def _expectation(gamma: float, beta: float, normalized_energies: np.ndarray) -> float:
    return float(_distribution(gamma, beta, normalized_energies) @ normalized_energies)


def _wilson(successes: int, total: int) -> list[float]:
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total**2))
    radius /= denominator
    return [max(0.0, centre - radius), min(1.0, centre + radius)]


def _metrics(
    probabilities: np.ndarray,
    energies: np.ndarray,
    normalized_energies: np.ndarray,
    optimum_indexes: np.ndarray,
    low_indexes: np.ndarray,
) -> dict[str, float]:
    uniform_energy = float(np.mean(energies))
    minimum = float(np.min(energies))
    expected = float(probabilities @ energies)
    statistic = float(spearmanr(energies, probabilities).statistic)
    return {
        "relative_expected_energy_improvement": (uniform_energy - expected)
        / (uniform_energy - minimum),
        "optimum_mass": float(np.sum(probabilities[optimum_indexes])),
        "four_lowest_mass": float(np.sum(probabilities[low_indexes])),
        "expected_raw_energy": expected,
        "expected_normalized_energy": float(probabilities @ normalized_energies),
        "energy_probability_spearman": statistic,
        "total_variation_from_uniform16": float(0.5 * np.sum(np.abs(probabilities - 1 / 16))),
    }


def _qiskit_distribution(
    gamma: float, beta: float, normalized_by_state: dict[str, float]
) -> tuple[dict[str, float], Any]:
    from qiskit import QuantumCircuit  # type: ignore[import-not-found]
    from qiskit.circuit.library import DiagonalGate  # type: ignore[import-not-found]
    from qiskit.quantum_info import Statevector  # type: ignore[import-not-found]

    circuit = QuantumCircuit(4)
    circuit.h(range(4))
    qiskit_diagonal = [
        np.exp(-1j * gamma * normalized_by_state[f"{index:04b}"[::-1]]) for index in range(16)
    ]
    circuit.append(DiagonalGate(qiskit_diagonal), range(4))
    circuit.rx(2 * beta, range(4))
    raw = Statevector.from_instruction(circuit).probabilities_dict()
    distribution = {
        str(bitstring)[::-1]: float(probability) for bitstring, probability in raw.items()
    }
    return distribution, circuit


def _shot_distribution(circuit: Any) -> tuple[dict[str, int], dict[str, float]]:
    from qiskit import transpile  # type: ignore[import-not-found]
    from qiskit.primitives import StatevectorSampler  # type: ignore[import-not-found]

    measured = circuit.copy()
    measured.measure_all()
    transpiled = transpile(measured, seed_transpiler=SEED)
    raw = (
        StatevectorSampler(seed=SEED)
        .run([transpiled], shots=SHOTS)
        .result()[0]
        .data.meas.get_counts()
    )
    counts = {str(bitstring)[::-1]: int(count) for bitstring, count in raw.items()}
    return counts, {state: count / SHOTS for state, count in counts.items()}


def _detectability(
    ideal: np.ndarray,
    energies: np.ndarray,
    optimum_indexes: np.ndarray,
    low_indexes: np.ndarray,
) -> dict[str, Any]:
    rng = np.random.default_rng(SEED)
    alternative = rng.multinomial(SHOTS, ideal, size=RESAMPLES) / SHOTS
    null = rng.multinomial(SHOTS, np.full(16, 1 / 16), size=RESAMPLES) / SHOTS
    uniform_energy = float(np.mean(energies))
    minimum = float(np.min(energies))

    def relative(values: np.ndarray) -> np.ndarray:
        expected = values @ energies
        return (uniform_energy - expected) / (uniform_energy - minimum)

    def correlations(values: np.ndarray) -> np.ndarray:
        return np.array([float(spearmanr(energies, row).statistic) for row in values])

    definitions = {
        "relative_expected_energy_improvement": (relative(alternative), relative(null), "higher"),
        "optimum_mass": (
            alternative[:, optimum_indexes].sum(axis=1),
            null[:, optimum_indexes].sum(axis=1),
            "higher",
        ),
        "four_lowest_mass": (
            alternative[:, low_indexes].sum(axis=1),
            null[:, low_indexes].sum(axis=1),
            "higher",
        ),
        "negative_energy_probability_spearman": (
            correlations(alternative),
            correlations(null),
            "lower",
        ),
    }
    results: dict[str, Any] = {}
    for name, (alternative_values, null_values, direction) in definitions.items():
        critical = float(np.quantile(null_values, 0.95 if direction == "higher" else 0.05))
        crosses = (
            alternative_values > critical
            if direction == "higher"
            else alternative_values < critical
        )
        quantiles = np.quantile(alternative_values, [0.025, 0.5, 0.975])
        results[name] = {
            "favorable_direction": direction,
            "null_critical_value": critical,
            "estimated_power": float(np.mean(crosses)),
            "alternative_q025": float(quantiles[0]),
            "alternative_median": float(quantiles[1]),
            "alternative_q975": float(quantiles[2]),
            "alternative_standard_deviation": float(np.std(alternative_values, ddof=1)),
        }
    return {
        "protocol": {
            "resamples": RESAMPLES,
            "shots": SHOTS,
            "seed": SEED,
            "null": "uniform over sixteen compact states",
            "alternative": "frozen compact p=1 ideal distribution",
            "one_sided_alpha": 0.05,
        },
        "metrics": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()

    exact = json.loads(
        (args.evidence_dir / "compact-exact-result.json").read_text(encoding="utf-8")
    )
    states = [f"{value:04b}" for value in range(16)]
    energy_by_state = {
        item["compact_bitstring"]: float(item["compact_direct_energy"]) for item in exact["mapping"]
    }
    energies = np.array([energy_by_state[state] for state in states])
    minimum = float(exact["minimum_energy"])
    spectral_range = float(exact["spectral_range"])
    normalized = (energies - minimum) / spectral_range
    normalized_by_state = dict(zip(states, normalized.tolist(), strict=True))

    gamma_grid = np.linspace(*GAMMA_BOUNDS, GAMMA_POINTS)
    beta_grid = np.linspace(*BETA_BOUNDS, BETA_POINTS)
    mixer_matrices = np.stack([_mixer(beta) for beta in beta_grid])
    grid_results: list[tuple[float, float, float]] = []
    for gamma in gamma_grid:
        phased = np.exp(-1j * gamma * normalized) / 4
        amplitudes = np.einsum("bij,j->bi", mixer_matrices, phased)
        expectations = np.abs(amplitudes) ** 2 @ normalized
        grid_results.extend(
            (float(expectation), float(gamma), float(beta))
            for expectation, beta in zip(expectations, beta_grid, strict=True)
        )
    grid_results.sort(key=lambda item: (item[0], item[1], item[2]))
    starts = grid_results[:REFINEMENT_STARTS]

    refinements: list[dict[str, Any]] = []
    for grid_energy, gamma, beta in starts:

        def objective(values: np.ndarray) -> float:
            return _expectation(float(values[0]), float(values[1]), normalized)

        optimized = minimize(
            objective,
            np.array([gamma, beta]),
            method="L-BFGS-B",
            bounds=[GAMMA_BOUNDS, BETA_BOUNDS],
            options={"maxiter": 500, "ftol": 1e-15, "gtol": 1e-12, "maxls": 20},
        )
        refinements.append(
            {
                "grid_gamma": gamma,
                "grid_beta": beta,
                "grid_expected_normalized_energy": grid_energy,
                "gamma": float(optimized.x[0]),
                "beta": float(optimized.x[1]),
                "expected_normalized_energy": float(optimized.fun),
                "function_evaluations": int(optimized.nfev),
                "iterations": int(optimized.nit),
                "success": bool(optimized.success),
                "message": str(optimized.message),
                "within_bounds": bool(
                    GAMMA_BOUNDS[0] <= optimized.x[0] <= GAMMA_BOUNDS[1]
                    and BETA_BOUNDS[0] <= optimized.x[1] <= BETA_BOUNDS[1]
                ),
            }
        )
    refinements.sort(
        key=lambda item: (item["expected_normalized_energy"], item["gamma"], item["beta"])
    )
    selected = refinements[0]
    gamma = float(selected["gamma"])
    beta = float(selected["beta"])
    ideal = _distribution(gamma, beta, normalized)
    qiskit_dict, circuit = _qiskit_distribution(gamma, beta, normalized_by_state)
    qiskit = np.array([qiskit_dict.get(state, 0.0) for state in states])
    maximum_qiskit_error = float(np.max(np.abs(ideal - qiskit)))
    if maximum_qiskit_error > 1e-12:
        raise AssertionError("Analytic and Qiskit statevector distributions disagree.")
    counts_dict, shot_dict = _shot_distribution(circuit)
    shot = np.array([shot_dict.get(state, 0.0) for state in states])

    optimum_indexes = np.array([states.index(state) for state in exact["optimum_bitstrings"]])
    low_indexes = np.argsort(energies)[:4]
    ideal_metrics = _metrics(ideal, energies, normalized, optimum_indexes, low_indexes)
    shot_metrics = _metrics(shot, energies, normalized, optimum_indexes, low_indexes)
    optimum_count = sum(counts_dict.get(states[index], 0) for index in optimum_indexes)
    low_count = sum(counts_dict.get(states[index], 0) for index in low_indexes)
    most_frequent = min(counts_dict, key=lambda state: (-counts_dict[state], state))
    detectability = _detectability(ideal, energies, optimum_indexes, low_indexes)

    gate = {
        "exact_equivalence_passed": bool(
            exact["maximum_representation_error"] <= 1e-12
            and exact["maximum_r2_spectrum_error"] <= 1e-12
        ),
        "ideal_relative_improvement_at_least_0_10": ideal_metrics[
            "relative_expected_energy_improvement"
        ]
        >= 0.10,
        "primary_power_at_least_0_80": detectability["metrics"][
            "relative_expected_energy_improvement"
        ]["estimated_power"]
        >= 0.80,
        "ideal_energy_below_uniform16": ideal_metrics["expected_raw_energy"]
        < float(np.mean(energies)),
        "postselection_required": False,
    }
    gate["passed"] = all(value for key, value in gate.items() if key != "postselection_required")

    result = {
        "experiment_id": "EXP-010A",
        "versions": {
            "python": platform.python_version(),
            "numpy": package_version("numpy"),
            "scipy": package_version("scipy"),
            "qiskit": package_version("qiskit"),
        },
        "protocol": {
            "logical_width": 4,
            "depth": 1,
            "gamma_bounds": list(GAMMA_BOUNDS),
            "beta_bounds": list(BETA_BOUNDS),
            "gamma_grid_points": GAMMA_POINTS,
            "beta_grid_points": BETA_POINTS,
            "grid_evaluations": GAMMA_POINTS * BETA_POINTS,
            "refinement_starts": REFINEMENT_STARTS,
            "optimizer": "L-BFGS-B",
            "shots": SHOTS,
            "seed": SEED,
            "postselection": False,
            "ibm_service_used": False,
        },
        "normalization": exact["normalization"],
        "uniform16_baselines": {
            "expected_raw_energy": float(np.mean(energies)),
            "expected_normalized_energy": float(np.mean(normalized)),
            "relative_expected_energy_improvement": 0.0,
            "optimum_mass": len(optimum_indexes) / 16,
            "four_lowest_mass": 4 / 16,
        },
        "selected_gamma": gamma,
        "selected_beta": beta,
        "refinements": refinements,
        "maximum_analytic_qiskit_probability_error": maximum_qiskit_error,
        "states": [
            {
                "compact_bitstring": state,
                "raw_energy": energy_by_state[state],
                "normalized_energy": normalized_by_state[state],
                "ideal_probability": float(ideal[index]),
                "shot_count": counts_dict.get(state, 0),
                "shot_probability": float(shot[index]),
            }
            for index, state in enumerate(states)
        ],
        "ideal_metrics": ideal_metrics,
        "shot_metrics": shot_metrics,
        "shot_wilson_95": {
            "optimum_mass": _wilson(optimum_count, SHOTS),
            "four_lowest_mass": _wilson(low_count, SHOTS),
        },
        "most_frequent_state": most_frequent,
        "most_frequent_count": counts_dict[most_frequent],
        "detectability": detectability,
        "hardware_readiness_gate": gate,
        "nonzero_quadratic_interactions": exact["nonzero_quadratic_terms"],
    }
    _write_json(args.evidence_dir / "qaoa-result.json", result)
    print("EXP-010A compact QAOA and detectability completed; no IBM service used.")


if __name__ == "__main__":
    main()
