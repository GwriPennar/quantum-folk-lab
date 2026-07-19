"""Run the frozen EXP-009A-R2 p=1 local QAOA protocol."""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path
from typing import Any

from quantum_folk_lab.simulation import package_version

INITIAL_POINTS = ((0.2, 0.2), (0.5, 0.5), (0.8, 0.3), (1.0, 0.7))
SHOTS = 4096
SEED = 42
MAX_ITERATIONS = 80


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _pauli_label(size: int, indexes: tuple[int, ...]) -> str:
    label = ["I"] * size
    for index in indexes:
        label[size - index - 1] = "Z"
    return "".join(label)


def _build_operator(ising: dict[str, Any]) -> Any:
    from qiskit.quantum_info import SparsePauliOp  # type: ignore[import-not-found]

    size = len(ising["h"])
    terms: list[tuple[str, float]] = [(_pauli_label(size, ()), ising["constant"])]
    terms.extend(
        (_pauli_label(size, (index,)), coefficient)
        for index, coefficient in enumerate(ising["h"])
        if coefficient
    )
    terms.extend(
        (_pauli_label(size, (left, right)), ising["j"][left][right])
        for left in range(size)
        for right in range(left + 1, size)
        if ising["j"][left][right]
    )
    return SparsePauliOp.from_list(terms)


def _estimate(estimator: Any, ansatz: Any, operator: Any, values: list[float]) -> float:
    result = estimator.run([(ansatz, operator, values)]).result()
    return float(result[0].data.evs)


def _variable_order_bitstring(qiskit_bitstring: str) -> str:
    return qiskit_bitstring[::-1]


def _qubo_energy(bitstring: str, qubo: dict[str, Any]) -> float:
    bits = [int(value) for value in bitstring]
    return float(qubo["offset"]) + sum(
        float(qubo["matrix"][left][right]) * bits[left] * bits[right]
        for left in range(8)
        for right in range(left, 8)
    )


def _is_feasible(bitstring: str) -> bool:
    return all(bitstring[index] != bitstring[index + 1] for index in range(0, 8, 2))


def _mass(distribution: dict[str, float], states: set[str]) -> float:
    return sum(probability for state, probability in distribution.items() if state in states)


def _wilson_interval(successes: int, total: int) -> list[float]:
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total**2))
    radius /= denominator
    return [round(max(0.0, centre - radius), 12), round(min(1.0, centre + radius), 12)]


def main() -> None:
    from qiskit import transpile  # type: ignore[import-not-found]
    from qiskit.circuit.library import QAOAAnsatz  # type: ignore[import-not-found]
    from qiskit.primitives import (  # type: ignore[import-not-found]
        StatevectorEstimator,
        StatevectorSampler,
    )
    from qiskit.quantum_info import Statevector  # type: ignore[import-not-found]
    from scipy.optimize import minimize  # type: ignore[import-untyped]
    from scipy.stats import spearmanr  # type: ignore[import-untyped]

    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()

    exact = json.loads((args.evidence_dir / "exact-result.json").read_text(encoding="utf-8"))
    qubo = json.loads((args.evidence_dir / "qubo.json").read_text(encoding="utf-8"))
    ising = json.loads((args.evidence_dir / "ising.json").read_text(encoding="utf-8"))
    if exact["maximum_agreement_error"] > 1e-10 or not exact["all_optima_feasible"]:
        raise ValueError("Authoritative exact gate is not valid.")

    operator = _build_operator(ising)
    ansatz = QAOAAnsatz(operator, reps=1)
    parameter_names = [str(parameter) for parameter in ansatz.parameters]
    if len(parameter_names) != 2:
        raise ValueError("Frozen p=1 protocol requires exactly two parameters.")
    estimator = StatevectorEstimator()
    attempts: list[dict[str, Any]] = []
    for initial_point in INITIAL_POINTS:

        def objective(values: list[float]) -> float:
            return _estimate(estimator, ansatz, operator, [float(value) for value in values])

        optimized = minimize(
            objective,
            list(initial_point),
            method="COBYLA",
            options={"maxiter": MAX_ITERATIONS, "rhobeg": 0.5},
        )
        attempts.append(
            {
                "initial_point": list(initial_point),
                "parameters": [float(value) for value in optimized.x],
                "expected_energy": float(optimized.fun),
                "function_evaluations": int(optimized.nfev),
                "success": bool(optimized.success),
                "message": str(optimized.message),
            }
        )
    selected = min(attempts, key=lambda item: (item["expected_energy"], item["initial_point"]))
    values = selected["parameters"]
    parameter_map = dict(zip(parameter_names, values, strict=True))
    gamma = next(value for name, value in parameter_map.items() if "γ" in name or "gamma" in name)
    beta = next(value for name, value in parameter_map.items() if "β" in name or "beta" in name)

    bound = ansatz.assign_parameters(values)
    decomposed = bound.decompose(reps=10)
    ideal_raw = Statevector.from_instruction(decomposed).probabilities_dict()
    ideal = {
        _variable_order_bitstring(str(bitstring)): float(probability)
        for bitstring, probability in ideal_raw.items()
        if probability > 1e-15
    }

    measured = decomposed.copy()
    measured.measure_all()
    transpiled = transpile(measured, seed_transpiler=SEED)
    sampled_raw = (
        StatevectorSampler(seed=SEED)
        .run([transpiled], shots=SHOTS)
        .result()[0]
        .data.meas.get_counts()
    )
    counts = {
        _variable_order_bitstring(str(bitstring)): int(count)
        for bitstring, count in sampled_raw.items()
    }
    sampled = {bitstring: count / SHOTS for bitstring, count in counts.items()}

    optima = set(exact["optimum_bitstrings"])
    feasible = {f"{state:08b}" for state in range(256) if _is_feasible(f"{state:08b}")}
    feasible_energies = {
        item["bitstring"]: float(item["energy"]) for item in exact["feasible_state_energies"]
    }
    four_lowest = set(
        sorted(feasible_energies, key=lambda state: (feasible_energies[state], state))[:4]
    )
    ideal_expected = sum(
        _qubo_energy(state, qubo) * probability for state, probability in ideal.items()
    )
    sampled_expected = sum(
        _qubo_energy(state, qubo) * probability for state, probability in sampled.items()
    )
    feasible_order = sorted(feasible_energies)
    ideal_spearman = spearmanr(
        [feasible_energies[state] for state in feasible_order],
        [ideal.get(state, 0.0) for state in feasible_order],
    )
    sampled_spearman = spearmanr(
        [feasible_energies[state] for state in feasible_order],
        [sampled.get(state, 0.0) for state in feasible_order],
    )
    optimum_count = sum(counts.get(state, 0) for state in optima)
    feasible_count = sum(counts.get(state, 0) for state in feasible)
    low_count = sum(counts.get(state, 0) for state in four_lowest)
    most_frequent = min(counts, key=lambda state: (-counts[state], state))
    nonzero_interactions = sum(
        bool(ising["j"][left][right]) for left in range(8) for right in range(left + 1, 8)
    )
    result = {
        "experiment_id": "EXP-009A-R2",
        "protocol": {
            "depth": 1,
            "shots": SHOTS,
            "seed": SEED,
            "optimizer": "COBYLA",
            "optimizer_max_iterations": MAX_ITERATIONS,
            "rhobeg": 0.5,
            "initial_points": [list(point) for point in INITIAL_POINTS],
            "execution": "local Qiskit statevector estimator and sampler",
            "ibm_service_used": False,
        },
        "versions": {
            "python": platform.python_version(),
            "qiskit": package_version("qiskit"),
            "scipy": package_version("scipy"),
        },
        "parameter_order": parameter_names,
        "selected_initial_point": selected["initial_point"],
        "selected_parameters": values,
        "gamma": float(gamma),
        "beta": float(beta),
        "optimizer_attempts": attempts,
        "optimizer_total_function_evaluations": sum(
            attempt["function_evaluations"] for attempt in attempts
        ),
        "ideal_distribution": {state: ideal[state] for state in sorted(ideal)},
        "shot_counts": {state: counts[state] for state in sorted(counts)},
        "shot_distribution": {state: sampled[state] for state in sorted(sampled)},
        "optimum_bitstrings": sorted(optima),
        "four_lowest_feasible_bitstrings": sorted(four_lowest),
        "ideal_optimum_class_mass": _mass(ideal, optima),
        "shot_optimum_class_mass": optimum_count / SHOTS,
        "ideal_feasible_subspace_mass": _mass(ideal, feasible),
        "shot_feasible_subspace_mass": feasible_count / SHOTS,
        "ideal_expected_energy": ideal_expected,
        "shot_expected_energy": sampled_expected,
        "ideal_four_lowest_feasible_mass": _mass(ideal, four_lowest),
        "shot_four_lowest_feasible_mass": low_count / SHOTS,
        "ideal_feasible_energy_probability_spearman": {
            "statistic": float(ideal_spearman.statistic),
            "pvalue": float(ideal_spearman.pvalue),
        },
        "shot_feasible_energy_probability_spearman": {
            "statistic": float(sampled_spearman.statistic),
            "pvalue": float(sampled_spearman.pvalue),
        },
        "most_frequent_bitstring": most_frequent,
        "most_frequent_count": counts[most_frequent],
        "shot_wilson_95": {
            "optimum_class_mass": _wilson_interval(optimum_count, SHOTS),
            "feasible_subspace_mass": _wilson_interval(feasible_count, SHOTS),
            "four_lowest_feasible_mass": _wilson_interval(low_count, SHOTS),
        },
        "uniform_baselines": {
            "optimum_class_mass": exact["uniform_optimum_class_baseline"],
            "feasible_subspace_mass": exact["uniform_feasible_subspace_baseline"],
            "four_lowest_feasible_mass": 4 / 256,
        },
        "optimum_class_size": exact["optimum_class_size"],
        "optimum_mass_metric_is_degeneracy_weakened": exact["optimum_class_size"] > 1,
        "logical_width": 8,
        "untranspiled_nonzero_two_qubit_interaction_count": nonzero_interactions,
        "untranspiled_decomposed_two_qubit_instruction_count": sum(
            len(instruction.qubits) == 2 for instruction in decomposed.data
        ),
    }
    _write_json(args.evidence_dir / "qaoa-result.json", result)
    print("EXP-009A-R2 local QAOA completed; no IBM service used.")


if __name__ == "__main__":
    main()
