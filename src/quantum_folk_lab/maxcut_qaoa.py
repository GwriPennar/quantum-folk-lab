from __future__ import annotations

import platform
import time
import warnings
from dataclasses import asdict, dataclass
from typing import Any

from quantum_folk_lab.circuit_reporting import operation_counts
from quantum_folk_lab.maxcut import (
    MaxCutGraph,
    bitstring_to_assignment,
    cut_value,
    decode_counts,
)
from quantum_folk_lab.maxcut_exact import solve_maxcut_exact
from quantum_folk_lab.maxcut_ising import (
    build_minimization_operator,
    require_qiskit_ising,
    verify_equivalence,
)
from quantum_folk_lab.simulation import package_version

DEFAULT_INITIAL_POINTS: tuple[tuple[float, float], ...] = (
    (0.2, 0.2),
    (0.5, 0.5),
    (0.8, 0.3),
    (1.0, 0.7),
)


@dataclass(frozen=True)
class OptimiserAttempt:
    initial_point: list[float]
    optimal_parameters: list[float]
    expected_energy: float
    expected_cut_value: float
    function_evaluations: int
    success: bool
    message: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MaxCutQAOAResult:
    experiment_id: str
    graph_name: str
    node_count: int
    edge_count: int
    total_edge_weight: float
    graph_edges: list[list[object]]
    execution_path: str
    genuine_qiskit_circuit: bool
    simulator_type: str
    python_version: str
    qiskit_version: str
    aer_version: str
    scipy_version: str
    seed: int
    shots: int
    qaoa_depth: int
    parameter_count: int
    optimiser_name: str
    optimiser_max_iterations: int
    optimiser_function_evaluations: int
    initial_points: list[list[float]]
    selected_initial_point: list[float]
    optimisation_attempts: list[dict[str, object]]
    optimal_parameters: list[float]
    exact_max_cut: float
    exact_optimal_bitstrings: list[str]
    exact_canonical_bitstring: str
    expected_cut_value: float
    expected_approximation_ratio: float
    sampled_best_bitstring: str
    sampled_best_cut: float
    sampled_best_approximation_ratio: float
    optimal_sample_count: int
    optimal_sample_probability: float
    measurement_counts: dict[str, int]
    circuit_width: int
    circuit_depth: int
    transpiled_depth: int
    operation_counts: dict[str, int]
    two_qubit_gate_count: int
    elapsed_seconds: float
    pass_or_caution: str
    limitations: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def require_qiskit_qaoa() -> tuple[Any, Any, Any, Any, Any, Any]:
    try:
        from qiskit import transpile  # type: ignore[import-not-found]
        from qiskit.primitives import (  # type: ignore[import-not-found]
            StatevectorEstimator,
            StatevectorSampler,
        )
        from scipy.optimize import minimize  # type: ignore[import-untyped]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "EXP-002 requires optional local Qiskit dependencies. "
            'Install them with: python -m pip install -e ".[quantum]"'
        ) from exc
    SparsePauliOp, QAOAAnsatz = require_qiskit_ising()
    return SparsePauliOp, QAOAAnsatz, StatevectorEstimator, StatevectorSampler, minimize, transpile


def _round_list(values: list[float] | tuple[float, ...]) -> list[float]:
    return [round(float(value), 10) for value in values]


def _estimate(estimator: Any, circuit: Any, operator: Any, values: list[float]) -> float:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = estimator.run([(circuit, operator, values)]).result()
    return float(result[0].data.evs)


def build_qaoa_ansatz(graph: MaxCutGraph, depth: int = 1) -> Any:
    if depth < 1:
        raise ValueError("depth must be positive")
    _, QAOAAnsatz = require_qiskit_ising()
    return QAOAAnsatz(build_minimization_operator(graph), reps=depth)


def build_measured_qaoa_circuit(graph: MaxCutGraph, parameters: list[float], depth: int = 1) -> Any:
    circuit = build_qaoa_ansatz(graph, depth).assign_parameters(parameters)
    measured = circuit.decompose(reps=10)
    measured.measure_all()
    return measured


def _two_qubit_gate_count(circuit: Any) -> int:
    return sum(1 for instruction in circuit.data if len(instruction.qubits) == 2)


def _select_best_count(graph: MaxCutGraph, counts: dict[str, int]) -> tuple[str, float]:
    best_bitstring = ""
    best_cut = float("-inf")
    for bitstring in sorted(counts):
        value = cut_value(graph, bitstring_to_assignment(bitstring))
        if value > best_cut:
            best_cut = value
            best_bitstring = bitstring
    return best_bitstring, best_cut


def run_maxcut_qaoa(
    graph: MaxCutGraph,
    depth: int = 1,
    shots: int = 4096,
    seed: int = 42,
    optimiser_max_iterations: int = 80,
    initial_points: tuple[tuple[float, ...], ...] | None = None,
) -> MaxCutQAOAResult:
    if shots <= 0:
        raise ValueError("shots must be positive")
    if depth < 1:
        raise ValueError("depth must be positive")
    verify_equivalence(graph)
    _, _, StatevectorEstimator, StatevectorSampler, minimize, transpile = require_qiskit_qaoa()

    start = time.perf_counter()
    exact = solve_maxcut_exact(graph)
    operator = build_minimization_operator(graph)
    ansatz = build_qaoa_ansatz(graph, depth)
    estimator = StatevectorEstimator()
    starts = initial_points or DEFAULT_INITIAL_POINTS
    expected_parameter_count = int(ansatz.num_parameters)
    attempts: list[OptimiserAttempt] = []

    for start_point in starts:
        if len(start_point) != expected_parameter_count:
            raise ValueError(f"initial point must contain {expected_parameter_count} parameters")

        def objective(values: list[float]) -> float:
            return _estimate(estimator, ansatz, operator, [float(value) for value in values])

        result = minimize(
            objective,
            list(start_point),
            method="COBYLA",
            options={"maxiter": optimiser_max_iterations, "rhobeg": 0.5},
        )
        energy = float(result.fun)
        attempts.append(
            OptimiserAttempt(
                initial_point=_round_list(start_point),
                optimal_parameters=_round_list(list(result.x)),
                expected_energy=round(energy, 10),
                expected_cut_value=round(-energy, 10),
                function_evaluations=int(result.nfev),
                success=bool(result.success),
                message=str(result.message),
            )
        )

    selected = min(attempts, key=lambda attempt: (attempt.expected_energy, attempt.initial_point))
    optimal_parameters = selected.optimal_parameters
    final_energy = _estimate(estimator, ansatz, operator, optimal_parameters)
    expected_cut = -final_energy
    measured = build_measured_qaoa_circuit(graph, optimal_parameters, depth)
    transpiled = transpile(measured, seed_transpiler=seed)
    sampler = StatevectorSampler(seed=seed)
    raw_counts = sampler.run([transpiled], shots=shots).result()[0].data.meas.get_counts()
    counts = decode_counts({str(key): int(value) for key, value in raw_counts.items()})
    sampled_best, sampled_best_cut = _select_best_count(graph, counts)
    optimal_set = set(exact.optimal_assignments)
    optimal_sample_count = sum(
        count for bitstring, count in counts.items() if bitstring in optimal_set
    )
    elapsed = time.perf_counter() - start
    expected_ratio = expected_cut / exact.maximum_cut if exact.maximum_cut else 0.0
    sampled_ratio = sampled_best_cut / exact.maximum_cut if exact.maximum_cut else 0.0
    status = (
        "pass" if sampled_best_cut == exact.maximum_cut and optimal_sample_count > 0 else "caution"
    )
    return MaxCutQAOAResult(
        experiment_id="EXP-002-maxcut-reference",
        graph_name=graph.name,
        node_count=graph.node_count,
        edge_count=graph.edge_count,
        total_edge_weight=graph.total_edge_weight,
        graph_edges=[[edge.u, edge.v, edge.weight] for edge in graph.edges],
        execution_path="local-qiskit-qaoa-statevector-estimator-and-sampler",
        genuine_qiskit_circuit=True,
        simulator_type="StatevectorEstimator optimisation; StatevectorSampler finite-shot sampling",
        python_version=platform.python_version(),
        qiskit_version=package_version("qiskit"),
        aer_version=package_version("qiskit-aer"),
        scipy_version=package_version("scipy"),
        seed=seed,
        shots=shots,
        qaoa_depth=depth,
        parameter_count=expected_parameter_count,
        optimiser_name="COBYLA",
        optimiser_max_iterations=optimiser_max_iterations,
        optimiser_function_evaluations=sum(attempt.function_evaluations for attempt in attempts),
        initial_points=[attempt.initial_point for attempt in attempts],
        selected_initial_point=selected.initial_point,
        optimisation_attempts=[attempt.to_dict() for attempt in attempts],
        optimal_parameters=optimal_parameters,
        exact_max_cut=exact.maximum_cut,
        exact_optimal_bitstrings=exact.optimal_assignments,
        exact_canonical_bitstring=exact.canonical_bitstring,
        expected_cut_value=round(expected_cut, 10),
        expected_approximation_ratio=round(expected_ratio, 10),
        sampled_best_bitstring=sampled_best,
        sampled_best_cut=sampled_best_cut,
        sampled_best_approximation_ratio=round(sampled_ratio, 10),
        optimal_sample_count=optimal_sample_count,
        optimal_sample_probability=round(optimal_sample_count / shots, 10),
        measurement_counts=counts,
        circuit_width=int(measured.width()),
        circuit_depth=int(measured.depth() or 0),
        transpiled_depth=int(transpiled.depth() or 0),
        operation_counts=operation_counts(transpiled),
        two_qubit_gate_count=_two_qubit_gate_count(transpiled),
        elapsed_seconds=round(elapsed, 6),
        pass_or_caution=status,
        limitations=(
            "Four-node ideal statevector simulation only; brute force is superior for this tiny "
            "instance and no quantum advantage or hardware behaviour is claimed."
        ),
    )


def compare_maxcut(
    graph: MaxCutGraph, depth: int = 1, shots: int = 4096, seed: int = 42
) -> dict[str, object]:
    exact = solve_maxcut_exact(graph)
    qaoa = run_maxcut_qaoa(graph, depth=depth, shots=shots, seed=seed)
    return {
        "experiment_id": "EXP-002-maxcut-reference",
        "graph_name": graph.name,
        "exact": exact.to_dict(),
        "qaoa": qaoa.to_dict(),
        "interpretation": {
            "exact_solver_is_ground_truth": True,
            "expected_and_sampled_metrics_are_distinct": True,
            "no_quantum_advantage_claimed": True,
        },
    }
