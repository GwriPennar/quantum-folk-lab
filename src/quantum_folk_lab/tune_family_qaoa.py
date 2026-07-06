from __future__ import annotations

import platform
import time
import warnings
from dataclasses import asdict, dataclass
from typing import Any

from quantum_folk_lab.circuit_reporting import operation_counts
from quantum_folk_lab.simulation import package_version
from quantum_folk_lab.tune_family import (
    ESTIMATOR_SEED,
    EXECUTABLE_SOURCE_COMMIT,
    EXPERIMENT_ID,
    FIXTURE_ID,
    GOVERNING_PLAN_COMMIT,
    GOVERNING_REVIEW_COMMITS,
    IMPLEMENTATION_BASE_COMMIT,
    INITIAL_POINTS,
    OPTIMISER_MAX_ITERATIONS,
    OPTIMISER_NAME,
    PLAN_PATH,
    PLAN_VERSION,
    QAOA_DEPTH,
    QAOA_SHOTS,
    RESULT_SCHEMA_VERSION,
    REVIEW_PATHS,
    SAMPLER_SEED,
    THRESHOLD_CHECKPOINT_COMMIT,
    THRESHOLD_MANIFEST_PATH,
    TRANSPILE_SEED,
    assignment_metrics,
    build_ising_model,
    classical_fallback_summary,
    coefficient_summary,
    count_histogram_by_energy,
    decode_qiskit_counts,
    registered_fixture,
    sample_summary,
    serialise_qubo,
    solve_registered_exact,
    sparse_pauli_terms,
    verify_direct_qubo,
    verify_qubo_ising,
)


@dataclass(frozen=True)
class OptimiserAttempt:
    initial_point: list[float]
    optimal_parameters: list[float]
    expected_energy: float
    function_evaluations: int
    success: bool
    message: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TuneFamilyQAOAResult:
    result_schema_version: str
    experiment_id: str
    run_identifier: str
    base_commit: str
    implementation_base_commit: str
    checkpoint_commit: str
    executable_source_commit: str
    source_commit: str
    threshold_manifest_path: str
    governing_plan_path: str
    governing_plan_commit: str
    governing_plan_version: str
    governing_review_paths: list[str]
    governing_review_commits: list[str]
    fixture_identifier: str
    deterministic_seed: int
    tune_ordering: list[str]
    tune_identifiers: list[str]
    hidden_labels_for_evaluation: list[int]
    similarity_weights: list[dict[str, object]]
    graph_threshold: float
    low_similarity_edge_threshold: float
    tau: float
    lambda_balance: float
    qubo: dict[str, object]
    qubo_coefficient_summary: dict[str, object]
    ising: dict[str, object]
    threshold_manifest: dict[str, object]
    exact: dict[str, object]
    classical_baselines: dict[str, object]
    qaoa_configuration: dict[str, object]
    optimisation_attempts: list[dict[str, object]]
    expected_energy: float
    expected_objective_gap: float
    optimal_parameters: list[float]
    sampled: dict[str, object]
    measurement_counts: dict[str, int]
    qiskit_raw_counts: dict[str, int]
    energy_histogram: dict[str, int]
    circuit_metrics: dict[str, object]
    package_versions: dict[str, str]
    execution_classification: str
    limitations: str
    elapsed_seconds: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def require_qiskit_qaoa() -> tuple[Any, Any, Any, Any, Any, Any]:
    try:
        from qiskit import transpile  # type: ignore[import-not-found,import-untyped,unused-ignore]
        from qiskit.circuit.library import (  # type: ignore[import-not-found,import-untyped,unused-ignore]
            QAOAAnsatz,
        )
        from qiskit.primitives import (  # type: ignore[import-not-found,import-untyped,unused-ignore]
            StatevectorEstimator,
            StatevectorSampler,
        )
        from qiskit.quantum_info import (  # type: ignore[import-not-found,import-untyped,unused-ignore]
            SparsePauliOp,
        )
        from scipy.optimize import minimize  # type: ignore[import-untyped]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "EXP-005A genuine local Qiskit QAOA requires optional local quantum "
            'dependencies. Install them with: python -m pip install -e ".[quantum]"'
        ) from exc
    return QAOAAnsatz, SparsePauliOp, StatevectorEstimator, StatevectorSampler, minimize, transpile


def build_sparse_pauli_operator(include_constant: bool = False) -> Any:
    _, SparsePauliOp, _, _, _, _ = require_qiskit_qaoa()
    fixture = registered_fixture()
    return SparsePauliOp.from_list(sparse_pauli_terms(fixture.model, include_constant)).simplify()


def build_qaoa_ansatz(depth: int = QAOA_DEPTH) -> Any:
    if depth < 1:
        raise ValueError("depth must be positive")
    QAOAAnsatz, _, _, _, _, _ = require_qiskit_qaoa()
    return QAOAAnsatz(build_sparse_pauli_operator(include_constant=False), reps=depth)


def build_measured_qaoa_circuit(parameters: list[float], depth: int = QAOA_DEPTH) -> Any:
    circuit = build_qaoa_ansatz(depth).assign_parameters(parameters)
    measured = circuit.decompose(reps=10)
    measured.measure_all()
    return measured


def _round_list(values: list[float] | tuple[float, ...]) -> list[float]:
    return [round(float(value), 10) for value in values]


def _estimate(
    estimator: Any, circuit: Any, operator: Any, constant: float, values: list[float]
) -> float:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = estimator.run([(circuit, operator, values)]).result()
    return float(result[0].data.evs) + constant


def _two_qubit_gate_count(circuit: Any) -> int:
    return sum(1 for instruction in circuit.data if len(instruction.qubits) == 2)


def run_tune_family_qaoa(
    threshold_manifest: dict[str, object],
    source_commit: str = EXECUTABLE_SOURCE_COMMIT,
    governing_plan_commit: str = GOVERNING_PLAN_COMMIT,
    depth: int = QAOA_DEPTH,
    shots: int = QAOA_SHOTS,
    sampler_seed: int = SAMPLER_SEED,
    estimator_seed: int = ESTIMATOR_SEED,
    optimiser_max_iterations: int = OPTIMISER_MAX_ITERATIONS,
    initial_points: tuple[tuple[float, ...], ...] = INITIAL_POINTS,
    base_commit: str = IMPLEMENTATION_BASE_COMMIT,
    checkpoint_commit: str = THRESHOLD_CHECKPOINT_COMMIT,
    executable_source_commit: str = EXECUTABLE_SOURCE_COMMIT,
    threshold_manifest_path: str = THRESHOLD_MANIFEST_PATH,
    governing_review_commits: tuple[str, str] = GOVERNING_REVIEW_COMMITS,
) -> TuneFamilyQAOAResult:
    if shots <= 0:
        raise ValueError("shots must be positive")
    if depth < 1:
        raise ValueError("depth must be positive")
    verify_direct_qubo()
    verify_qubo_ising()
    _, _, StatevectorEstimator, StatevectorSampler, minimize, transpile = require_qiskit_qaoa()
    fixture = registered_fixture()
    exact = solve_registered_exact(fixture)
    ising = build_ising_model(fixture.model)
    operator = build_sparse_pauli_operator(include_constant=False)
    ansatz = build_qaoa_ansatz(depth)
    estimator = StatevectorEstimator(seed=estimator_seed)
    expected_parameter_count = int(ansatz.num_parameters)
    attempts: list[OptimiserAttempt] = []
    start_time = time.perf_counter()

    for start_point in initial_points:
        if len(start_point) != expected_parameter_count:
            raise ValueError(f"initial point must contain {expected_parameter_count} parameters")

        def objective(values: list[float]) -> float:
            return _estimate(
                estimator,
                ansatz,
                operator,
                ising.constant,
                [float(value) for value in values],
            )

        result = minimize(
            objective,
            list(start_point),
            method=OPTIMISER_NAME,
            options={"maxiter": optimiser_max_iterations, "rhobeg": 0.5},
        )
        attempts.append(
            OptimiserAttempt(
                initial_point=_round_list(start_point),
                optimal_parameters=_round_list(list(result.x)),
                expected_energy=round(float(result.fun), 10),
                function_evaluations=int(result.nfev),
                success=bool(result.success),
                message=str(result.message),
            )
        )

    selected = min(attempts, key=lambda attempt: (attempt.expected_energy, attempt.initial_point))
    optimal_parameters = selected.optimal_parameters
    expected_energy = _estimate(estimator, ansatz, operator, ising.constant, optimal_parameters)
    measured = build_measured_qaoa_circuit(optimal_parameters, depth)
    transpiled = transpile(measured, seed_transpiler=TRANSPILE_SEED)
    sampler = StatevectorSampler(seed=sampler_seed)
    raw_counts = sampler.run([transpiled], shots=shots).result()[0].data.meas.get_counts()
    qiskit_counts = {str(key): int(value) for key, value in raw_counts.items()}
    counts = decode_qiskit_counts(qiskit_counts)
    sampled = sample_summary(counts, fixture)
    elapsed = time.perf_counter() - start_time
    exact_dict = exact.to_dict()
    expected_gap = expected_energy - exact.exact_minimum_energy
    graph = fixture.graph
    similarity_weights: list[dict[str, object]] = [
        {"left": edge.left, "right": edge.right, "weight": edge.weight} for edge in graph.edges
    ]
    sampled_best = sampled["best_sampled_human_bitstring"]
    best_metrics = assignment_metrics(
        tuple(int(char) for char in str(sampled_best)),
        fixture.evaluation_labels,
    )
    sampled.update(best_metrics)
    return TuneFamilyQAOAResult(
        result_schema_version=RESULT_SCHEMA_VERSION,
        experiment_id=EXPERIMENT_ID,
        run_identifier=f"{FIXTURE_ID}-p{depth}-shots{shots}-seed{sampler_seed}",
        base_commit=base_commit,
        implementation_base_commit=base_commit,
        checkpoint_commit=checkpoint_commit,
        executable_source_commit=executable_source_commit,
        source_commit=source_commit,
        threshold_manifest_path=threshold_manifest_path,
        governing_plan_path=PLAN_PATH,
        governing_plan_commit=governing_plan_commit,
        governing_plan_version=PLAN_VERSION,
        governing_review_paths=list(REVIEW_PATHS),
        governing_review_commits=list(governing_review_commits),
        fixture_identifier=FIXTURE_ID,
        deterministic_seed=42,
        tune_ordering=list(graph.tune_ids),
        tune_identifiers=list(graph.tune_ids),
        hidden_labels_for_evaluation=list(fixture.evaluation_labels),
        similarity_weights=similarity_weights,
        graph_threshold=fixture.graph_threshold,
        low_similarity_edge_threshold=0.25,
        tau=fixture.tau,
        lambda_balance=fixture.balance_lambda,
        qubo=serialise_qubo(fixture.model),
        qubo_coefficient_summary=coefficient_summary(fixture.model),
        ising=ising.to_dict(),
        threshold_manifest=threshold_manifest,
        exact=exact_dict,
        classical_baselines={
            "uniform_all_assignments": {
                "expected_energy": exact.random_all_expected_energy,
                "exact_success_probability": exact.random_all_success_probability,
            },
            "uniform_balanced_assignments": {
                "expected_energy": exact.random_balanced_expected_energy,
                "exact_success_probability": exact.random_balanced_success_probability,
            },
            "classical_fallback": classical_fallback_summary(shots),
        },
        qaoa_configuration={
            "depth": depth,
            "mixer": "standard X mixer",
            "optimiser": OPTIMISER_NAME,
            "optimiser_max_iterations": optimiser_max_iterations,
            "initial_points": [list(point) for point in initial_points],
            "estimator_seed": estimator_seed,
            "sampler_seed": sampler_seed,
            "transpile_seed": TRANSPILE_SEED,
            "shots": shots,
            "execution_path": "QAOAAnsatz + local StatevectorEstimator + local StatevectorSampler",
        },
        optimisation_attempts=[attempt.to_dict() for attempt in attempts],
        expected_energy=round(expected_energy, 10),
        expected_objective_gap=round(expected_gap, 10),
        optimal_parameters=optimal_parameters,
        sampled=sampled,
        measurement_counts=counts,
        qiskit_raw_counts=qiskit_counts,
        energy_histogram=count_histogram_by_energy(counts, fixture.model),
        circuit_metrics={
            "logical_problem_qubits": len(fixture.model.variables),
            "classical_bit_count": int(measured.num_clbits),
            "total_qiskit_circuit_width": int(measured.width()),
            "circuit_width_definition": (
                "Qiskit total width: logical problem qubits plus classical bits after measurement"
            ),
            "qaoa_depth": depth,
            "raw_circuit_depth": int(measured.depth() or 0),
            "transpiled_depth": int(transpiled.depth() or 0),
            "operation_counts": operation_counts(transpiled),
            "two_qubit_gate_count": _two_qubit_gate_count(transpiled),
            "parameter_count": expected_parameter_count,
            "hamiltonian_term_count": len(
                sparse_pauli_terms(fixture.model, include_constant=False)
            ),
            "interaction_graph_density": 1.0,
        },
        package_versions={
            "python": platform.python_version(),
            "qiskit": package_version("qiskit"),
            "qiskit_aer": package_version("qiskit-aer"),
            "scipy": package_version("scipy"),
        },
        execution_classification="genuine-local-qiskit",
        limitations=(
            "Eight-variable deterministic synthetic fixture only; exact brute-force enumeration "
            "is superior and remains ground truth. Local ideal statevector simulation is not "
            "hardware evidence and no quantum advantage, production readiness, real-corpus "
            "family discovery, IBM Runtime use, cloud backend use, or QPU execution is claimed."
        ),
        elapsed_seconds=round(elapsed, 6),
    )
