from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from itertools import combinations, product

from quantum_folk_lab.domain.synthetic import generate_benchmark
from quantum_folk_lab.evaluation.metrics import family_recovery
from quantum_folk_lab.graph.build import SimilarityGraph, build_similarity_graph
from quantum_folk_lab.qubo.model import QUBOModel
from quantum_folk_lab.qubo.two_family import build_two_family_qubo, direct_objective

FIXTURE_ID = "synthetic-two-family-v1-seed42"
EXPERIMENT_ID = "EXP-005A-tune-family-qaoa"
RESULT_SCHEMA_VERSION = "exp005a.tune_family_qaoa.v1"
PLAN_PATH = "docs/plans/EXP-005A-current-qiskit-local-plan.md"
PLAN_VERSION = "EXP-005A-current-qiskit-local-plan"
REVIEW_PATHS = (
    "docs/reviews/EXP-005A-tune-family-qubo-plan-review.md",
    "docs/reviews/EXP-005A-revised-plan-second-review.md",
)
EXPECTED_TUNE_ORDER = (
    "fam_a_base",
    "fam_a_transposed",
    "fam_a_substitution",
    "fam_a_rhythm",
    "fam_b_base",
    "fam_b_transposed",
    "fam_b_inserted",
    "fam_b_deleted",
)
EXPECTED_LABEL_BITSTRING = "00001111"
TAU = 0.25
LAMBDA_BALANCE = 0.1
GRAPH_THRESHOLD = 0.45
LOW_SIMILARITY_EDGE_THRESHOLD = 0.25
EXPECTED_OPTIMA = ("00001111", "11110000")
CANONICAL_OPTIMUM = "00001111"
RANDOM_SUCCESS_ALL = 2 / 256
RANDOM_SUCCESS_BALANCED = 2 / 70
OPTIMAL_PROBABILITY_THRESHOLD = 0.05
QAOA_DEPTH = 1
QAOA_SHOTS = 4096
ESTIMATOR_SEED = 42
SAMPLER_SEED = 42
TRANSPILE_SEED = 42
OPTIMISER_NAME = "COBYLA"
OPTIMISER_MAX_ITERATIONS = 80
INITIAL_POINTS = ((0.2, 0.2), (0.5, 0.5), (0.8, 0.3), (1.0, 0.7))


@dataclass(frozen=True)
class TuneFamilyFixture:
    fixture_id: str
    graph: SimilarityGraph
    model: QUBOModel
    evaluation_labels: tuple[int, ...]
    tau: float
    balance_lambda: float
    graph_threshold: float


@dataclass(frozen=True)
class TuneFamilyExactResult:
    fixture_id: str
    evaluated_assignments: int
    exact_minimum_energy: float
    exact_optimal_bitstrings: list[str]
    exact_complement_classes: list[str]
    canonical_optimum: str
    all_optima_balanced: bool
    family_recovery: float
    random_all_expected_energy: float
    random_balanced_expected_energy: float
    random_all_success_probability: float
    random_balanced_success_probability: float
    maximum_direct_qubo_disagreement: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class IsingModel:
    constant: float
    linear_z: dict[str, float]
    quadratic_zz: dict[str, float]
    scaling_factor: float = 1.0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationSummary:
    verified_assignments: int
    maximum_disagreement: float
    tolerance: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def registered_fixture() -> TuneFamilyFixture:
    melodies = generate_benchmark(seed=42, variants_per_family=4)
    tune_order = tuple(melody.tune_id for melody in melodies)
    if tune_order != EXPECTED_TUNE_ORDER:
        raise AssertionError(f"registered tune order changed: {tune_order}")
    graph = build_similarity_graph(melodies, threshold=GRAPH_THRESHOLD)
    model = build_two_family_qubo(graph, dissimilar_threshold=TAU, balance=LAMBDA_BALANCE)
    labels = tuple(graph.labels)
    if bitstring_from_bits(labels) != EXPECTED_LABEL_BITSTRING:
        raise AssertionError("registered evaluation labels changed")
    return TuneFamilyFixture(
        fixture_id=FIXTURE_ID,
        graph=graph,
        model=model,
        evaluation_labels=labels,
        tau=TAU,
        balance_lambda=LAMBDA_BALANCE,
        graph_threshold=GRAPH_THRESHOLD,
    )


def all_assignments(variable_count: int = 8) -> list[tuple[int, ...]]:
    return list(product((0, 1), repeat=variable_count))


def bitstring_from_bits(bits: tuple[int, ...] | list[int]) -> str:
    return "".join(str(bit) for bit in bits)


def bits_from_bitstring(bitstring: str) -> tuple[int, ...]:
    if any(char not in {"0", "1"} for char in bitstring):
        raise ValueError("bitstring must contain only 0 and 1")
    return tuple(int(char) for char in bitstring)


def complement_bits(bits: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    return tuple(1 - bit for bit in bits)


def canonical_bitstring(bits: tuple[int, ...] | list[int] | str) -> str:
    bitstring = bits if isinstance(bits, str) else bitstring_from_bits(bits)
    complement = bitstring_from_bits(complement_bits(bits_from_bitstring(bitstring)))
    return min(bitstring, complement)


def qiskit_key_to_human_bitstring(key: str) -> str:
    return key[::-1]


def human_bitstring_to_qiskit_key(bitstring: str) -> str:
    return bitstring[::-1]


def decode_qiskit_counts(counts: dict[str, int]) -> dict[str, int]:
    decoded: dict[str, int] = {}
    for key, count in counts.items():
        bitstring = qiskit_key_to_human_bitstring(str(key))
        decoded[bitstring] = decoded.get(bitstring, 0) + int(count)
    return dict(sorted(decoded.items()))


def balance_violation(bits: tuple[int, ...] | list[int]) -> int:
    return abs(sum(bits) - len(bits) // 2)


def is_balanced(bits: tuple[int, ...] | list[int]) -> bool:
    return balance_violation(bits) == 0


def serialise_qubo(model: QUBOModel) -> dict[str, object]:
    return {
        "variables": list(model.variables),
        "offset": model.offset,
        "linear": dict(sorted(model.linear.items())),
        "quadratic": {
            f"{left}|{right}": value for (left, right), value in sorted(model.quadratic.items())
        },
        "metadata": model.metadata,
    }


def direct_energy(bits: tuple[int, ...], fixture: TuneFamilyFixture | None = None) -> float:
    current = fixture or registered_fixture()
    return direct_objective(
        bits,
        current.graph,
        dissimilar_threshold=current.tau,
        balance=current.balance_lambda,
    )


def _same_family_pairs(labels: tuple[int, ...]) -> set[tuple[int, int]]:
    return {
        pair for pair in combinations(range(len(labels)), 2) if labels[pair[0]] == labels[pair[1]]
    }


def pairwise_partition_metrics(
    bits: tuple[int, ...] | list[int], labels: tuple[int, ...] | list[int]
) -> dict[str, float]:
    same_truth = _same_family_pairs(tuple(labels))
    same_pred = {
        pair for pair in combinations(range(len(bits)), 2) if bits[pair[0]] == bits[pair[1]]
    }
    true_positive = len(same_truth & same_pred)
    false_positive = len(same_pred - same_truth)
    false_negative = len(same_truth - same_pred)
    precision = true_positive / (true_positive + false_positive) if same_pred else 0.0
    recall = true_positive / (true_positive + false_negative) if same_truth else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    return {
        "pairwise_precision": precision,
        "pairwise_recall": recall,
        "pairwise_f1": f1,
    }


def adjusted_rand_index(
    bits: tuple[int, ...] | list[int], labels: tuple[int, ...] | list[int]
) -> float:
    predicted_clusters: dict[int, list[int]] = {}
    true_clusters: dict[int, list[int]] = {}
    for index, (bit, label) in enumerate(zip(bits, labels, strict=True)):
        predicted_clusters.setdefault(bit, []).append(index)
        true_clusters.setdefault(label, []).append(index)

    def choose2(count: int) -> float:
        return count * (count - 1) / 2

    contingency_sum = 0.0
    for pred_members in predicted_clusters.values():
        pred_set = set(pred_members)
        for true_members in true_clusters.values():
            contingency_sum += choose2(len(pred_set & set(true_members)))
    pred_sum = sum(choose2(len(members)) for members in predicted_clusters.values())
    true_sum = sum(choose2(len(members)) for members in true_clusters.values())
    total_pairs = choose2(len(bits))
    expected = pred_sum * true_sum / total_pairs if total_pairs else 0.0
    maximum = 0.5 * (pred_sum + true_sum)
    denominator = maximum - expected
    return (contingency_sum - expected) / denominator if denominator else 1.0


def assignment_metrics(
    bits: tuple[int, ...] | list[int], labels: tuple[int, ...] | list[int]
) -> dict[str, float]:
    metrics = {
        "family_recovery": family_recovery(bits, labels),
        "partition_accuracy": family_recovery(bits, labels),
        "adjusted_rand_index": adjusted_rand_index(bits, labels),
    }
    metrics.update(pairwise_partition_metrics(bits, labels))
    return metrics


def solve_registered_exact(fixture: TuneFamilyFixture | None = None) -> TuneFamilyExactResult:
    current = fixture or registered_fixture()
    rows = []
    max_disagreement = 0.0
    for bits in all_assignments(len(current.model.variables)):
        direct = direct_energy(bits, current)
        qubo = current.model.energy(bits)
        max_disagreement = max(max_disagreement, abs(direct - qubo))
        rows.append((bits, direct, qubo))
    best = min(qubo for _, _, qubo in rows)
    optima = [bitstring_from_bits(bits) for bits, _, qubo in rows if abs(qubo - best) <= 1e-9]
    balanced = [qubo for bits, _, qubo in rows if is_balanced(bits)]
    return TuneFamilyExactResult(
        fixture_id=current.fixture_id,
        evaluated_assignments=len(rows),
        exact_minimum_energy=best,
        exact_optimal_bitstrings=optima,
        exact_complement_classes=sorted({canonical_bitstring(bitstring) for bitstring in optima}),
        canonical_optimum=CANONICAL_OPTIMUM,
        all_optima_balanced=all(
            is_balanced(bits_from_bitstring(bitstring)) for bitstring in optima
        ),
        family_recovery=max(
            family_recovery(bits_from_bitstring(bitstring), current.evaluation_labels)
            for bitstring in optima
        ),
        random_all_expected_energy=sum(qubo for _, _, qubo in rows) / len(rows),
        random_balanced_expected_energy=sum(balanced) / len(balanced),
        random_all_success_probability=RANDOM_SUCCESS_ALL,
        random_balanced_success_probability=RANDOM_SUCCESS_BALANCED,
        maximum_direct_qubo_disagreement=max_disagreement,
    )


def verify_direct_qubo(tolerance: float = 1e-9) -> VerificationSummary:
    fixture = registered_fixture()
    max_disagreement = 0.0
    for bits in all_assignments(len(fixture.model.variables)):
        direct = direct_energy(bits, fixture)
        qubo = fixture.model.energy(bits)
        disagreement = abs(direct - qubo)
        max_disagreement = max(max_disagreement, disagreement)
        if disagreement > tolerance:
            raise AssertionError(f"direct/QUBO mismatch for {bitstring_from_bits(bits)}")
    exact = solve_registered_exact(fixture)
    if exact.exact_optimal_bitstrings != list(EXPECTED_OPTIMA):
        raise AssertionError("registered argmin set changed")
    if not exact.all_optima_balanced:
        raise AssertionError("unbalanced optimum found")
    return VerificationSummary(256, max_disagreement, tolerance)


def build_ising_model(model: QUBOModel) -> IsingModel:
    linear_z = dict.fromkeys(model.variables, 0.0)
    quadratic_zz: dict[str, float] = {}
    constant = model.offset
    for variable, coeff in model.linear.items():
        constant += coeff / 2
        linear_z[variable] -= coeff / 2
    for (left, right), coeff in model.quadratic.items():
        constant += coeff / 4
        linear_z[left] -= coeff / 4
        linear_z[right] -= coeff / 4
        quadratic_zz[f"{left}|{right}"] = coeff / 4
    return IsingModel(
        constant=constant,
        linear_z={key: value for key, value in linear_z.items() if abs(value) > 1e-12},
        quadratic_zz={key: value for key, value in quadratic_zz.items() if abs(value) > 1e-12},
    )


def z_eigenvalue(bit: int) -> int:
    if bit == 0:
        return 1
    if bit == 1:
        return -1
    raise ValueError("bit must be 0 or 1")


def ising_energy(bits: tuple[int, ...], model: QUBOModel, ising: IsingModel | None = None) -> float:
    current = ising or build_ising_model(model)
    values = dict(zip(model.variables, bits, strict=True))
    energy = current.constant
    for variable, coeff in current.linear_z.items():
        energy += coeff * z_eigenvalue(values[variable])
    for key, coeff in current.quadratic_zz.items():
        left, right = key.split("|")
        energy += coeff * z_eigenvalue(values[left]) * z_eigenvalue(values[right])
    return energy / current.scaling_factor


def verify_qubo_ising(tolerance: float = 1e-8) -> VerificationSummary:
    fixture = registered_fixture()
    ising = build_ising_model(fixture.model)
    max_disagreement = 0.0
    for bits in all_assignments(len(fixture.model.variables)):
        qubo = fixture.model.energy(bits)
        energy = ising_energy(bits, fixture.model, ising)
        disagreement = abs(qubo - energy)
        max_disagreement = max(max_disagreement, disagreement)
        if disagreement > tolerance:
            raise AssertionError(f"QUBO/Ising mismatch for {bitstring_from_bits(bits)}")
    return VerificationSummary(256, max_disagreement, tolerance)


def _pauli_label(qubit_count: int, *qubits: int) -> str:
    label = ["I"] * qubit_count
    for qubit in qubits:
        label[qubit_count - 1 - qubit] = "Z"
    return "".join(label)


def sparse_pauli_terms(model: QUBOModel, include_constant: bool = False) -> list[tuple[str, float]]:
    ising = build_ising_model(model)
    variable_index = {variable: index for index, variable in enumerate(model.variables)}
    terms: list[tuple[str, float]] = []
    if include_constant and abs(ising.constant) > 1e-12:
        terms.append(("I" * len(model.variables), ising.constant))
    for variable, coeff in ising.linear_z.items():
        terms.append((_pauli_label(len(model.variables), variable_index[variable]), coeff))
    for key, coeff in ising.quadratic_zz.items():
        left, right = key.split("|")
        terms.append(
            (_pauli_label(len(model.variables), variable_index[left], variable_index[right]), coeff)
        )
    return terms


def threshold_manifest(governing_plan_commit: str, source_base_commit: str) -> dict[str, object]:
    fixture = registered_fixture()
    exact = solve_registered_exact(fixture)
    return {
        "manifest_schema_version": "exp005a.threshold-manifest.v1",
        "experiment_id": EXPERIMENT_ID,
        "governing_plan_path": PLAN_PATH,
        "governing_plan_commit": governing_plan_commit,
        "governing_plan_version": PLAN_VERSION,
        "governing_review_paths": list(REVIEW_PATHS),
        "governing_review_commits": [governing_plan_commit, governing_plan_commit],
        "source_base_commit": source_base_commit,
        "fixture_identifier": FIXTURE_ID,
        "tune_ordering": list(fixture.graph.tune_ids),
        "variable_ordering": list(fixture.model.variables),
        "tau": TAU,
        "dissimilar_threshold_internal_name": (
            "tau maps to build_two_family_qubo.dissimilar_threshold"
        ),
        "lambda": LAMBDA_BALANCE,
        "graph_threshold": GRAPH_THRESHOLD,
        "low_similarity_edge_threshold": LOW_SIMILARITY_EDGE_THRESHOLD,
        "exact_optimum_energy": exact.exact_minimum_energy,
        "exact_optimal_bitstrings": exact.exact_optimal_bitstrings,
        "canonical_complement_class": exact.canonical_optimum,
        "random_expected_energies": {
            "all_assignments": exact.random_all_expected_energy,
            "balanced_assignments": exact.random_balanced_expected_energy,
        },
        "random_exact_success_probabilities": {
            "all_assignments": RANDOM_SUCCESS_ALL,
            "balanced_assignments": RANDOM_SUCCESS_BALANCED,
        },
        "qaoa_depth": QAOA_DEPTH,
        "optimiser": OPTIMISER_NAME,
        "optimiser_evaluation_budget": OPTIMISER_MAX_ITERATIONS,
        "fixed_initial_points": [list(point) for point in INITIAL_POINTS],
        "estimator_seed": ESTIMATOR_SEED,
        "sampler_seed": SAMPLER_SEED,
        "transpile_seed": TRANSPILE_SEED,
        "shot_count": QAOA_SHOTS,
        "optimal_probability_success_threshold": OPTIMAL_PROBABILITY_THRESHOLD,
        "threshold_rationale": (
            "The threshold is fixed before any EXP-005A QAOA output is generated. "
            "It is 6.4x the uniform all-assignment optimum-class probability "
            f"({RANDOM_SUCCESS_ALL:.8f}) and 1.75x the uniform balanced optimum-class "
            f"probability ({RANDOM_SUCCESS_BALANCED:.8f}). The value remains cautious "
            "for a dense eight-variable p=1 local ideal-simulation benchmark while requiring "
            "measurable concentration beyond random sampling."
        ),
        "qaoa_output_generated_before_manifest": False,
    }


def sample_summary(
    counts: dict[str, int], fixture: TuneFamilyFixture | None = None
) -> dict[str, object]:
    current = fixture or registered_fixture()
    shots = sum(counts.values())
    if shots <= 0:
        raise ValueError("counts must contain at least one shot")
    energies = {
        bitstring: current.model.energy(bits_from_bitstring(bitstring)) for bitstring in counts
    }
    best_bitstring = min(energies, key=lambda bitstring: (energies[bitstring], bitstring))
    optimal_count = sum(
        count for bitstring, count in counts.items() if bitstring in EXPECTED_OPTIMA
    )
    intended_count = sum(
        count
        for bitstring, count in counts.items()
        if canonical_bitstring(bitstring) == CANONICAL_OPTIMUM
    )
    balanced_count = sum(
        count for bitstring, count in counts.items() if is_balanced(bits_from_bitstring(bitstring))
    )
    metrics = assignment_metrics(bits_from_bitstring(best_bitstring), current.evaluation_labels)
    return {
        "shots": shots,
        "best_sampled_human_bitstring": best_bitstring,
        "canonical_sampled_partition": canonical_bitstring(best_bitstring),
        "best_sampled_energy": energies[best_bitstring],
        "probability_00001111": counts.get("00001111", 0) / shots,
        "probability_11110000": counts.get("11110000", 0) / shots,
        "optimal_complement_class_probability": optimal_count / shots,
        "intended_family_partition_probability": intended_count / shots,
        "balanced_sample_probability": balanced_count / shots,
        **metrics,
    }


def classical_fallback_summary(shots: int = QAOA_SHOTS) -> dict[str, object]:
    exact = solve_registered_exact()
    return {
        "execution_classification": "classical-fallback",
        "description": "Existing deterministic non-Qiskit softmax sampler, not genuine QAOA.",
        "shots": shots,
        "reference_best_bitstring": exact.canonical_optimum,
        "reference_energy": exact.exact_minimum_energy,
    }


def coefficient_summary(model: QUBOModel) -> dict[str, object]:
    values = [abs(model.offset), *(abs(value) for value in model.linear.values())]
    values.extend(abs(value) for value in model.quadratic.values())
    nonzero = [value for value in values if value > 0]
    return {
        "offset": model.offset,
        "linear_count": len(model.linear),
        "quadratic_count": len(model.quadratic),
        "nonzero_abs_min": min(nonzero),
        "nonzero_abs_max": max(nonzero),
    }


def count_histogram_by_energy(counts: dict[str, int], model: QUBOModel) -> dict[str, int]:
    histogram: Counter[str] = Counter()
    for bitstring, count in counts.items():
        histogram[f"{model.energy(bits_from_bitstring(bitstring)):.6f}"] += count
    return dict(sorted(histogram.items()))
