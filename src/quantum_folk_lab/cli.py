from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quantum_folk_lab.build_week import LearnerLevel, export_json, export_markdown, run_guided_exact
from quantum_folk_lab.classical.exact import solve_exact
from quantum_folk_lab.domain.models import Melody
from quantum_folk_lab.domain.synthetic import generate_benchmark, to_jsonable
from quantum_folk_lab.evaluation.metrics import approximation_ratio, family_recovery
from quantum_folk_lab.graph.build import SimilarityGraph, build_similarity_graph
from quantum_folk_lab.maxcut import get_graph, list_graphs
from quantum_folk_lab.maxcut_exact import solve_maxcut_exact
from quantum_folk_lab.maxcut_ising import verify_equivalence
from quantum_folk_lab.maxcut_qaoa import compare_maxcut, run_maxcut_qaoa
from quantum_folk_lab.quantum.qaoa_local import run_local_qaoa
from quantum_folk_lab.quantum_basics import list_experiments
from quantum_folk_lab.qubo.model import QUBOModel
from quantum_folk_lab.qubo.two_family import build_two_family_qubo
from quantum_folk_lab.simulation import run_all_basics, run_basics_experiment
from quantum_folk_lab.tune_family import (
    EXECUTABLE_SOURCE_COMMIT,
    FIXTURE_ID,
    GOVERNING_PLAN_COMMIT,
    GOVERNING_REVIEW_COMMITS,
    IMPLEMENTATION_BASE_COMMIT,
    QAOA_DEPTH,
    QAOA_SHOTS,
    THRESHOLD_CHECKPOINT_COMMIT,
    THRESHOLD_MANIFEST_PATH,
    build_ising_model,
    coefficient_summary,
    registered_fixture,
    serialise_qubo,
    solve_registered_exact,
    threshold_manifest,
    verify_direct_qubo,
    verify_qubo_ising,
)
from quantum_folk_lab.tune_family_qaoa import run_tune_family_qaoa
from quantum_folk_lab.utils.reproducibility import environment_report


def _pipeline(seed: int) -> tuple[SimilarityGraph, QUBOModel, list[Melody]]:
    melodies = generate_benchmark(seed)
    graph = build_similarity_graph(melodies)
    model = build_two_family_qubo(graph)
    return graph, model, melodies


def _add_basics_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--seed-simulator", type=int, default=42)
    parser.add_argument("--seed-transpiler", type=int, default=42)


def _add_maxcut_graph(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--graph", default="cycle4", help="registered graph name, default: cycle4")


def _add_maxcut_qaoa_options(parser: argparse.ArgumentParser) -> None:
    _add_maxcut_graph(parser)
    parser.add_argument("--depth", type=int, default=1, help="QAOA reps/depth, default: 1")
    parser.add_argument(
        "--shots", type=int, default=4096, help="finite sampling shots, default: 4096"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="deterministic sampler/transpiler seed"
    )


def _add_tune_family_qaoa_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--depth", type=int, default=QAOA_DEPTH, help="QAOA reps/depth, default: 1")
    parser.add_argument(
        "--shots", type=int, default=QAOA_SHOTS, help="finite sampling shots, default: 4096"
    )
    parser.add_argument("--seed", type=int, default=42, help="deterministic sampler seed")
    parser.add_argument("--source-commit", default=EXECUTABLE_SOURCE_COMMIT)
    parser.add_argument("--governing-plan-commit", default=GOVERNING_PLAN_COMMIT)
    parser.add_argument("--threshold-manifest", default="")


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2))


def _handle_qiskit_error(exc: RuntimeError) -> None:
    print(str(exc), file=sys.stderr)
    raise SystemExit(2) from exc


def main() -> None:
    parser = argparse.ArgumentParser(prog="qfl")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("generate-synthetic", "solve-exact", "solve-qaoa", "compare"):
        p = sub.add_parser(name)
        p.add_argument("--seed", type=int, default=42)
    sub.add_parser("doctor")
    sub.add_parser("basics-list")
    basics_run = sub.add_parser("basics-run")
    basics_run.add_argument("--experiment", required=True)
    _add_basics_options(basics_run)
    basics_all = sub.add_parser("basics-run-all")
    _add_basics_options(basics_all)
    sub.add_parser("maxcut-list")
    maxcut_exact = sub.add_parser("maxcut-exact")
    _add_maxcut_graph(maxcut_exact)
    maxcut_qaoa = sub.add_parser("maxcut-qaoa")
    _add_maxcut_qaoa_options(maxcut_qaoa)
    maxcut_compare = sub.add_parser("maxcut-compare")
    _add_maxcut_qaoa_options(maxcut_compare)
    sub.add_parser("tune-family-list")
    sub.add_parser("tune-family-exact")
    sub.add_parser("tune-family-qubo")
    tune_family_qaoa = sub.add_parser("tune-family-qaoa")
    _add_tune_family_qaoa_options(tune_family_qaoa)
    tune_family_compare = sub.add_parser("tune-family-compare")
    _add_tune_family_qaoa_options(tune_family_compare)
    build_week_exact = sub.add_parser("build-week-exact")
    build_week_exact.add_argument(
        "--format", choices=("summary", "json", "markdown"), default="summary"
    )
    build_week_exact.add_argument("--output", type=Path)
    build_week_exact.add_argument(
        "--level", choices=tuple(level.value for level in LearnerLevel), default="first_encounter"
    )
    args = parser.parse_args()

    if args.command == "doctor":
        _print_json(environment_report())
        return
    if args.command == "basics-list":
        _print_json([experiment.__dict__ for experiment in list_experiments()])
        return
    if args.command == "basics-run":
        try:
            result = run_basics_experiment(
                args.experiment,
                shots=args.shots,
                seed_simulator=args.seed_simulator,
                seed_transpiler=args.seed_transpiler,
            )
        except RuntimeError as exc:
            _handle_qiskit_error(exc)
        _print_json(result.to_dict())
        return
    if args.command == "basics-run-all":
        try:
            results = run_all_basics(
                shots=args.shots,
                seed_simulator=args.seed_simulator,
                seed_transpiler=args.seed_transpiler,
            )
        except RuntimeError as exc:
            _handle_qiskit_error(exc)
        _print_json([result.to_dict() for result in results])
        return
    if args.command == "maxcut-list":
        _print_json([maxcut_graph.metadata() for maxcut_graph in list_graphs()])
        return
    if args.command == "maxcut-exact":
        maxcut_graph = get_graph(args.graph)
        maxcut_exact_result = solve_maxcut_exact(maxcut_graph)
        equivalence = verify_equivalence(maxcut_graph)
        _print_json(
            {
                **maxcut_exact_result.to_dict(),
                "qubo_ising_verified_assignments": len(equivalence),
                "convention": "direct cut and QUBO are maximized; QAOA minimises -H_cut",
            }
        )
        return
    if args.command == "maxcut-qaoa":
        try:
            maxcut_qaoa_result = run_maxcut_qaoa(
                get_graph(args.graph), depth=args.depth, shots=args.shots, seed=args.seed
            )
        except RuntimeError as exc:
            _handle_qiskit_error(exc)
        _print_json(maxcut_qaoa_result.to_dict())
        return
    if args.command == "maxcut-compare":
        try:
            maxcut_comparison = compare_maxcut(
                get_graph(args.graph), depth=args.depth, shots=args.shots, seed=args.seed
            )
        except RuntimeError as exc:
            _handle_qiskit_error(exc)
        _print_json(maxcut_comparison)
        return
    if args.command == "tune-family-list":
        fixture = registered_fixture()
        _print_json(
            {
                "fixture_identifier": FIXTURE_ID,
                "tune_ordering": list(fixture.graph.tune_ids),
                "evaluation_labels": list(fixture.evaluation_labels),
                "tau": fixture.tau,
                "lambda": fixture.balance_lambda,
                "graph_threshold": fixture.graph_threshold,
                "edge_count": len(fixture.graph.edges),
                "execution_classification": "fixture-registration",
            }
        )
        return
    if args.command == "tune-family-exact":
        direct_qubo = verify_direct_qubo()
        ising = verify_qubo_ising()
        exact = solve_registered_exact()
        _print_json(
            {
                **exact.to_dict(),
                "direct_qubo_verification": direct_qubo.to_dict(),
                "qubo_ising_verification": ising.to_dict(),
                "execution_classification": "exact-classical-enumeration",
            }
        )
        return
    if args.command == "tune-family-qubo":
        fixture = registered_fixture()
        direct_qubo = verify_direct_qubo()
        ising_summary = verify_qubo_ising()
        _print_json(
            {
                "fixture_identifier": fixture.fixture_id,
                "tau": fixture.tau,
                "lambda": fixture.balance_lambda,
                "qubo": serialise_qubo(fixture.model),
                "coefficient_summary": coefficient_summary(fixture.model),
                "ising": build_ising_model(fixture.model).to_dict(),
                "direct_qubo_verification": direct_qubo.to_dict(),
                "qubo_ising_verification": ising_summary.to_dict(),
                "execution_classification": "classical-verification",
            }
        )
        return
    if args.command == "build-week-exact":
        try:
            envelope = run_guided_exact()
            if args.format == "json":
                output = export_json(envelope)
            elif args.format == "markdown":
                output = export_markdown(envelope, LearnerLevel(args.level))
            else:
                output = (
                    f"Fixture: {envelope.fixture_identifier}\n"
                    f"Exact minimum: {envelope.exact_result['minimum_energy']:.6f}\n"
                    "Canonical complement class: "
                    f"{envelope.exact_result['canonical_complement_class']}\n"
                    "Authority: exact enumeration of 256 assignments\n"
                )
        except (AssertionError, ValueError) as exc:
            print(f"Build Week exact validation failed: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return
    if args.command in {"tune-family-qaoa", "tune-family-compare"}:
        manifest = threshold_manifest(
            governing_plan_commit=args.governing_plan_commit,
            implementation_base_commit=IMPLEMENTATION_BASE_COMMIT,
            governing_review_commits=GOVERNING_REVIEW_COMMITS,
            threshold_checkpoint_commit=THRESHOLD_CHECKPOINT_COMMIT,
        )
        if args.threshold_manifest:
            manifest = json.loads(Path(args.threshold_manifest).read_text(encoding="utf-8"))
        try:
            tune_family_result = run_tune_family_qaoa(
                threshold_manifest=manifest,
                source_commit=args.source_commit,
                governing_plan_commit=args.governing_plan_commit,
                depth=args.depth,
                shots=args.shots,
                sampler_seed=args.seed,
                base_commit=IMPLEMENTATION_BASE_COMMIT,
                checkpoint_commit=THRESHOLD_CHECKPOINT_COMMIT,
                executable_source_commit=EXECUTABLE_SOURCE_COMMIT,
                threshold_manifest_path=THRESHOLD_MANIFEST_PATH,
                governing_review_commits=GOVERNING_REVIEW_COMMITS,
            )
        except RuntimeError as exc:
            _handle_qiskit_error(exc)
        payload: object = tune_family_result.to_dict()
        if args.command == "tune-family-compare":
            payload = {
                "exact": tune_family_result.exact,
                "classical_baselines": tune_family_result.classical_baselines,
                "qaoa": tune_family_result.to_dict(),
                "interpretation": {
                    "exact_solver_is_ground_truth": True,
                    "expected_and_sampled_metrics_are_distinct": True,
                    "no_maxcut_approximation_ratio_used": True,
                    "no_quantum_advantage_claimed": True,
                },
            }
        _print_json(payload)
        return

    similarity_graph, model, melodies = _pipeline(args.seed)
    if args.command == "generate-synthetic":
        _print_json(to_jsonable(melodies))
    elif args.command == "solve-exact":
        exact_result = solve_exact(model)
        _print_json(
            {
                "bits": exact_result.bits,
                "energy": exact_result.energy,
                "evaluated": exact_result.evaluated,
                "family_recovery": family_recovery(exact_result.bits, similarity_graph.labels),
            }
        )
    elif args.command == "solve-qaoa":
        qaoa_result = run_local_qaoa(model, seed=args.seed)
        exact_result = solve_exact(model)
        _print_json(
            {
                "bits": qaoa_result.best_bits,
                "energy": qaoa_result.best_energy,
                "backend": qaoa_result.backend,
                "optimal_probability": qaoa_result.optimal_probability,
                "approximation_ratio": approximation_ratio(
                    qaoa_result.best_energy, exact_result.energy
                ),
            }
        )
    elif args.command == "compare":
        exact_result = solve_exact(model)
        qaoa_result = run_local_qaoa(model, seed=args.seed)
        _print_json(
            {
                "exact": {
                    "bits": exact_result.bits,
                    "energy": exact_result.energy,
                    "family_recovery": family_recovery(exact_result.bits, similarity_graph.labels),
                },
                "qaoa": {
                    "backend": qaoa_result.backend,
                    "energy": qaoa_result.best_energy,
                    "optimal_probability": qaoa_result.optimal_probability,
                },
            }
        )


if __name__ == "__main__":
    main()
