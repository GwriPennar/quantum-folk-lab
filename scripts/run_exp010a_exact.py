"""Generate EXP-010A compact algebraic-equivalence evidence from committed R2 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from quantum_folk_lab.compact_family_encoding import TOLERANCE, verify_compact_equivalence


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _hash(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r2-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    r2_qubo = json.loads((args.r2_dir / "qubo.json").read_text(encoding="utf-8"))
    r2_exact = json.loads((args.r2_dir / "exact-result.json").read_text(encoding="utf-8"))
    pair_distances = {
        (r2_qubo["variable_order"][left], r2_qubo["variable_order"][right]): float(
            r2_qubo["matrix"][left][right]
        )
        for left in range(8)
        for right in range(left + 1, 8)
        if left // 2 != right // 2
    }
    result = verify_compact_equivalence(r2_qubo["variable_order"], pair_distances)
    model = result["model"]
    mappings = result["mappings"]
    energies = [float(item["compact_direct_energy"]) for item in mappings]
    minimum = min(energies)
    maximum = max(energies)
    optima = sorted(
        item["compact_bitstring"]
        for item in mappings
        if math.isclose(float(item["compact_direct_energy"]), minimum, abs_tol=TOLERANCE)
    )
    levels = sorted(set(energies))
    gap = (
        min(value for value in levels if not math.isclose(value, minimum, abs_tol=TOLERANCE))
        - minimum
    )
    r2_spectrum = sorted(float(item["energy"]) for item in r2_exact["feasible_state_energies"])
    maximum_spectrum_error = max(
        abs(left - right) for left, right in zip(sorted(energies), r2_spectrum, strict=True)
    )
    mapped_optima = sorted(
        item["r2_bitstring"] for item in mappings if item["compact_bitstring"] in optima
    )
    if maximum_spectrum_error > TOLERANCE:
        raise AssertionError("Compact and R2 feasible spectra differ.")
    if mapped_optima != sorted(r2_exact["optimum_bitstrings"]):
        raise AssertionError("Compact and R2 optimum classes differ.")
    if abs(gap - float(r2_exact["gap_to_next_non_optimal"])) > TOLERANCE:
        raise AssertionError("Compact and R2 gaps differ.")

    qubo_coefficients = {
        "offset": model.offset,
        "matrix": [list(row) for row in model.qubo],
    }
    ising_coefficients = {
        "constant": model.ising_constant,
        "h": list(model.h),
        "j": [list(row) for row in model.j],
    }
    qubo_hash = _hash(qubo_coefficients)
    ising_hash = _hash(ising_coefficients)
    variable_order = ["blackbird", "bold-deserter", "catherine-tyrrell", "merry-old-woman"]
    compact_qubo = {
        "convention": "offset + diagonal + upper-triangular pair terms",
        "source": "algebraic substitution using committed R2 15-decimal cross-family terms",
        "variable_order": variable_order,
        "penalty_term": False,
        **qubo_coefficients,
        "coefficient_sha256": qubo_hash,
    }
    compact_ising = {
        "convention": "y=(1-z)/2; constant + sum(h_i z_i) + sum(J_ij z_i z_j)",
        "variable_order": variable_order,
        **ising_coefficients,
        "coefficient_sha256": ising_hash,
    }
    exact = {
        "experiment_id": "EXP-010A",
        "comparison_tolerance": TOLERANCE,
        "state_count": 16,
        "all_states_valid": True,
        "mapping": mappings,
        "maximum_representation_error": result["maximum_error"],
        "maximum_r2_spectrum_error": maximum_spectrum_error,
        "optimum_bitstrings": optima,
        "canonical_optimum": optima[0],
        "mapped_r2_optimum_bitstrings": mapped_optima,
        "minimum_energy": minimum,
        "maximum_energy": maximum,
        "spectral_range": maximum - minimum,
        "gap_to_next_non_optimal": gap,
        "distinct_energy_levels": len(levels),
        "qubo_coefficient_sha256": qubo_hash,
        "ising_coefficient_sha256": ising_hash,
        "nonzero_linear_terms": sum(
            abs(model.qubo[index][index]) > TOLERANCE for index in range(4)
        ),
        "nonzero_quadratic_terms": sum(
            abs(model.qubo[left][right]) > TOLERANCE
            for left in range(4)
            for right in range(left + 1, 4)
        ),
        "normalization": {
            "formula": "(E - E_min) / (E_max - E_min)",
            "minimum": minimum,
            "range": maximum - minimum,
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.output_dir / "compact-qubo.json", compact_qubo)
    _write_json(args.output_dir / "compact-ising.json", compact_ising)
    _write_json(args.output_dir / "compact-exact-result.json", exact)
    report = f"""# EXP-010A encoding-equivalence report

All sixteen compact states map bijectively to the sixteen R2-feasible states. Exact enumeration is
authoritative and no penalty, postselection, or repair is used.

- Compact optimum: `{optima[0]}`.
- Mapped R2 optimum: `{mapped_optima[0]}`.
- Minimum energy: `{minimum!r}`.
- Maximum energy: `{maximum!r}`.
- Spectral range: `{maximum - minimum!r}`.
- Exact gap: `{gap!r}`.
- Distinct energy levels: `{len(levels)}`.
- Maximum mapped/direct/QUBO/Ising disagreement: `{result["maximum_error"]:.3e}`.
- Maximum compact/R2 spectrum disagreement: `{maximum_spectrum_error:.3e}`.
- Nonzero compact linear terms: `{exact["nonzero_linear_terms"]}`.
- Nonzero compact quadratic terms: `{exact["nonzero_quadratic_terms"]}`.
- Compact QUBO SHA-256: `{qubo_hash}`.
- Compact Ising SHA-256: `{ising_hash}`.

The compact encoding exactly preserves the committed R2 feasible musical spectrum. It makes no
claim about musical truth, authenticity, hardware behavior, or quantum advantage.
"""
    (args.output_dir / "ENCODING-EQUIVALENCE-REPORT.md").write_text(report, encoding="utf-8")
    print("EXP-010A exact compact equivalence passed for all 16 states.")


if __name__ == "__main__":
    main()
