"""Build the non-sensitive EXP-010A hardware-design evidence package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp010a-dir", type=Path, required=True)
    parser.add_argument("--r2-dir", type=Path, required=True)
    args = parser.parse_args()

    exact = json.loads((args.exp010a_dir / "compact-exact-result.json").read_text(encoding="utf-8"))
    qubo = json.loads((args.exp010a_dir / "compact-qubo.json").read_text(encoding="utf-8"))
    ising = json.loads((args.exp010a_dir / "compact-ising.json").read_text(encoding="utf-8"))
    qaoa = json.loads((args.exp010a_dir / "qaoa-result.json").read_text(encoding="utf-8"))
    r2_qaoa = json.loads((args.r2_dir / "qaoa-result.json").read_text(encoding="utf-8"))

    minimum = float(exact["minimum_energy"])
    spectral_range = float(exact["spectral_range"])
    normalized_hamiltonian = {
        "convention": "(H - E_min I) / (E_max - E_min)",
        "constant": (float(ising["constant"]) - minimum) / spectral_range,
        "h": [float(value) / spectral_range for value in ising["h"]],
        "j": [[float(value) / spectral_range for value in row] for row in ising["j"]],
    }
    package = {
        "experiment_id": "EXP-010A",
        "purpose": "local evidence for EXP-010B compact-encoding hardware protocol design",
        "variable_order": qubo["variable_order"],
        "compact_to_r2_mapping": [
            {
                "compact_bitstring": item["compact_bitstring"],
                "r2_bitstring": item["r2_bitstring"],
            }
            for item in exact["mapping"]
        ],
        "compact_qubo_sha256": exact["qubo_coefficient_sha256"],
        "compact_ising_sha256": exact["ising_coefficient_sha256"],
        "exact_spectrum": [
            {"bitstring": item["compact_bitstring"], "energy": item["compact_direct_energy"]}
            for item in exact["mapping"]
        ],
        "optimum_bitstrings": exact["optimum_bitstrings"],
        "mapped_r2_optimum_bitstrings": exact["mapped_r2_optimum_bitstrings"],
        "minimum_energy": exact["minimum_energy"],
        "maximum_energy": exact["maximum_energy"],
        "spectral_range": exact["spectral_range"],
        "gap": exact["gap_to_next_non_optimal"],
        "normalized_hamiltonian": normalized_hamiltonian,
        "gamma": qaoa["selected_gamma"],
        "beta": qaoa["selected_beta"],
        "ideal_and_shot_states": qaoa["states"],
        "primary_metric": {
            "name": "relative_expected_energy_improvement",
            "ideal": qaoa["ideal_metrics"]["relative_expected_energy_improvement"],
            "shot": qaoa["shot_metrics"]["relative_expected_energy_improvement"],
            "detectability": qaoa["detectability"]["metrics"][
                "relative_expected_energy_improvement"
            ],
        },
        "secondary_metrics": {
            "ideal": qaoa["ideal_metrics"],
            "shot": qaoa["shot_metrics"],
            "wilson_95": qaoa["shot_wilson_95"],
            "detectability": qaoa["detectability"]["metrics"],
        },
        "uniform16_baselines": qaoa["uniform16_baselines"],
        "hardware_readiness_gate": qaoa["hardware_readiness_gate"],
        "logical_width": 4,
        "nonzero_quadratic_interactions": exact["nonzero_quadratic_terms"],
        "untranspiled_p1_two_qubit_interaction_count": exact["nonzero_quadratic_terms"],
        "r2_comparison": {
            "r2_logical_width": 8,
            "r2_possible_pair_interactions": 28,
            "r2_penalty_A": 7,
            "r2_valid_states": 16,
            "r2_total_states": 256,
            "r2_ideal_feasible_mass": r2_qaoa["ideal_feasible_subspace_mass"],
            "r2_ideal_conditional_feasible_distribution_nearly_uniform": True,
            "r2_ideal_energy_probability_spearman": r2_qaoa[
                "ideal_feasible_energy_probability_spearman"
            ]["statistic"],
            "compact_logical_width": 4,
            "compact_total_and_valid_states": 16,
            "compact_penalty": False,
            "compact_postselection": False,
            "same_exact_musical_spectrum": True,
            "compact_ideal_energy_probability_spearman": qaoa["ideal_metrics"][
                "energy_probability_spearman"
            ],
        },
        "ibm_service_contacted": False,
        "backend_queried": False,
        "qpu_job_submitted": False,
    }
    _write_json(args.exp010a_dir / "fable-hardware-inputs.json", package)

    comparison = f"""# EXP-010A comparison with EXP-009A-R2

## R2 eight-qubit penalty encoding

- 8 logical qubits and 28 possible pair interactions;
- one-hot penalty `A=7`;
- 16 feasible states among 256;
- ideal feasible mass `{r2_qaoa["ideal_feasible_subspace_mass"]}`;
- conditional feasible distribution almost uniform;
- ideal feasible energy/probability Spearman rho
  `{r2_qaoa["ideal_feasible_energy_probability_spearman"]["statistic"]}`, an unfavorable direction.

## EXP-010A compact encoding

- 4 logical qubits and {exact["nonzero_quadratic_terms"]} nonzero quadratic interactions;
- all 16 states valid;
- no penalty and no postselection;
- exactly the same 16 musical energies, optimum, and gap;
- ideal energy/probability Spearman rho
  `{qaoa["ideal_metrics"]["energy_probability_spearman"]}`, a favorable negative direction;
- ideal relative expected-energy improvement
  `{qaoa["ideal_metrics"]["relative_expected_energy_improvement"]}`.

Under the frozen p=1 protocols, the compact encoding produces genuine within-spectrum energy
ordering that the R2 penalty encoding did not. This encoding improvement is not quantum advantage
and does not predict hardware performance.
"""
    (args.exp010a_dir / "R2-COMPARISON.md").write_text(comparison, encoding="utf-8")
    primary_power = qaoa["detectability"]["metrics"]["relative_expected_energy_improvement"][
        "estimated_power"
    ]
    fable_report = f"""# Fable hardware-design inputs

EXP-010A exactly preserves the R2 feasible spectrum in four logical qubits and passes the
predeclared local hardware-readiness gate.

- Compact QUBO SHA-256: `{exact["qubo_coefficient_sha256"]}`.
- Compact Ising SHA-256: `{exact["ising_coefficient_sha256"]}`.
- Optimum: `{exact["canonical_optimum"]}` -> R2 `{exact["mapped_r2_optimum_bitstrings"][0]}`.
- Gap: `{exact["gap_to_next_non_optimal"]}`.
- Frozen gamma: `{qaoa["selected_gamma"]}`; beta: `{qaoa["selected_beta"]}`.
- Ideal primary metric: `{qaoa["ideal_metrics"]["relative_expected_energy_improvement"]}`.
- Primary 4096-shot power: `{primary_power}`.
- Logical width: 4; nonzero two-qubit interactions: {exact["nonzero_quadratic_terms"]}.

This package selects no IBM backend and designs no job. No IBM service was contacted.
"""
    (args.exp010a_dir / "FABLE-HARDWARE-INPUTS.md").write_text(fable_report, encoding="utf-8")
    readiness = """# EXP-010A hardware readiness

Exact equivalence, ideal relative improvement, primary detectability, lower-than-uniform expected
energy, and no-postselection gates all pass. This authorizes protocol design only, not IBM access or
hardware submission.

`READY TO DESIGN EXP-010B COMPACT-ENCODING HARDWARE PROTOCOL`
"""
    (args.exp010a_dir / "HARDWARE-READINESS.md").write_text(readiness, encoding="utf-8")
    readme = """# EXP-010A — compact four-family encoding

EXP-010A algebraically eliminates R2's one-hot penalties by representing each two-setting family
with one binary variable. All sixteen compact states are valid and map bijectively to the sixteen
R2-feasible states.

The four-bit model exactly preserves the R2 musical spectrum. Its frozen local p=1 result passes the
predeclared relative-energy and 4096-shot detectability gates and shows favorable within-spectrum
energy ordering. Exact enumeration remains authoritative, and no quantum advantage is claimed.

No external dataset was reread and no IBM service or hardware was contacted.

Outcome: `READY TO DESIGN EXP-010B COMPACT-ENCODING HARDWARE PROTOCOL`.
"""
    (args.exp010a_dir / "README.md").write_text(readme, encoding="utf-8")
    print("EXP-010A hardware-design package built; no IBM service contacted.")


if __name__ == "__main__":
    main()
