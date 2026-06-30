from __future__ import annotations

import argparse
import json

from quantum_folk_lab.classical.exact import solve_exact
from quantum_folk_lab.domain.models import Melody
from quantum_folk_lab.domain.synthetic import generate_benchmark, to_jsonable
from quantum_folk_lab.evaluation.metrics import approximation_ratio, family_recovery
from quantum_folk_lab.graph.build import SimilarityGraph, build_similarity_graph
from quantum_folk_lab.quantum.qaoa_local import run_local_qaoa
from quantum_folk_lab.qubo.model import QUBOModel
from quantum_folk_lab.qubo.two_family import build_two_family_qubo
from quantum_folk_lab.utils.reproducibility import environment_report


def _pipeline(seed: int) -> tuple[SimilarityGraph, QUBOModel, list[Melody]]:
    melodies = generate_benchmark(seed)
    graph = build_similarity_graph(melodies)
    model = build_two_family_qubo(graph)
    return graph, model, melodies


def main() -> None:
    parser = argparse.ArgumentParser(prog="qfl")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("generate-synthetic", "solve-exact", "solve-qaoa", "compare"):
        p = sub.add_parser(name)
        p.add_argument("--seed", type=int, default=42)
    sub.add_parser("doctor")
    args = parser.parse_args()
    if args.command == "doctor":
        print(json.dumps(environment_report(), indent=2))
        return
    graph, model, melodies = _pipeline(args.seed)
    if args.command == "generate-synthetic":
        print(json.dumps(to_jsonable(melodies), indent=2))
    elif args.command == "solve-exact":
        exact_result = solve_exact(model)
        print(
            json.dumps(
                {
                    "bits": exact_result.bits,
                    "energy": exact_result.energy,
                    "evaluated": exact_result.evaluated,
                    "family_recovery": family_recovery(exact_result.bits, graph.labels),
                },
                indent=2,
            )
        )
    elif args.command == "solve-qaoa":
        qaoa_result = run_local_qaoa(model, seed=args.seed)
        exact = solve_exact(model)
        print(
            json.dumps(
                {
                    "bits": qaoa_result.best_bits,
                    "energy": qaoa_result.best_energy,
                    "backend": qaoa_result.backend,
                    "optimal_probability": qaoa_result.optimal_probability,
                    "approximation_ratio": approximation_ratio(
                        qaoa_result.best_energy, exact.energy
                    ),
                },
                indent=2,
            )
        )
    elif args.command == "compare":
        exact = solve_exact(model)
        qaoa = run_local_qaoa(model, seed=args.seed)
        print(
            json.dumps(
                {
                    "exact": {
                        "bits": exact.bits,
                        "energy": exact.energy,
                        "family_recovery": family_recovery(exact.bits, graph.labels),
                    },
                    "qaoa": {
                        "backend": qaoa.backend,
                        "energy": qaoa.best_energy,
                        "optimal_probability": qaoa.optimal_probability,
                    },
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
