from __future__ import annotations

import argparse
import json
import sys

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
