"""Generate EXP-009A-R1 exact evidence from the pinned external IrishMAN data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from quantum_folk_lab.real_data_quantum import (
    FEATURE_NAMES,
    ONE_HOT_PENALTY,
    build_binary_model,
    enumerate_exact,
    feature_distance,
)
from quantum_folk_lab.real_data_quantum_r1 import extract_coarse_features_r1
from quantum_folk_lab.research_selection import (
    canonical_record_sha256,
    normalized_melody_fingerprint,
    verify_external_files,
)

TRAIN_SHA256 = "5706880c0f935e69108244e010784935b7aba855f37ae2ce7f4e4d170851835c"
VALIDATION_SHA256 = "a33935f9047edc976e087b146737ed3737a9315c2bf52ff02d8873b057c575ae"
IRISHMAN_REVISION = "30902e69ca45266207f8466e0d04e4bc742c5604"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _coefficient_hash(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--irishman-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    verify_external_files(
        args.irishman_root,
        {"train.json": TRAIN_SHA256, "validation.json": VALIDATION_SHA256},
    )
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest["irishman_revision"] != IRISHMAN_REVISION:
        raise ValueError("Manifest revision does not match the frozen successor contract.")
    settings = manifest["settings"]
    if len(settings) != 8:
        raise ValueError("Manifest must contain exactly eight settings.")

    split_rows = {
        split: json.loads((args.irishman_root / f"{split}.json").read_text(encoding="utf-8"))
        for split in ("train", "validation")
    }
    selected_records: list[dict[str, Any]] = []
    for setting in settings:
        record = split_rows[setting["irishman_split"]][setting["irishman_row_index"]]
        if canonical_record_sha256(record) != setting["raw_record_sha256"]:
            raise ValueError(f"Raw-record hash mismatch for {setting['setting_id']}.")
        if (
            normalized_melody_fingerprint(record["abc notation"])
            != setting["normalized_melody_fingerprint"]
        ):
            raise ValueError(f"Fingerprint mismatch for {setting['setting_id']}.")
        selected_records.append(record)

    first_match: dict[str, tuple[str, int]] = {}
    targets = {setting["normalized_melody_fingerprint"] for setting in settings}
    for split in ("train", "validation"):
        for index, record in enumerate(split_rows[split]):
            fingerprint = normalized_melody_fingerprint(record["abc notation"])
            if fingerprint in targets and fingerprint not in first_match:
                first_match[fingerprint] = (split, index)
    for setting in settings:
        expected = (setting["irishman_split"], setting["irishman_row_index"])
        if first_match.get(setting["normalized_melody_fingerprint"]) != expected:
            raise ValueError(f"Tie-break verification failed for {setting['setting_id']}.")

    parsed = [extract_coarse_features_r1(record["abc notation"]) for record in selected_records]
    features = [result.features for result in parsed]
    family_names = list(dict.fromkeys(setting["family_id"] for setting in settings))
    family_indexes = [family_names.index(setting["family_id"]) for setting in settings]
    model = build_binary_model(features, family_indexes)
    exact = enumerate_exact(features, family_indexes)

    derived = {
        "experiment_id": "EXP-009A-R1",
        "feature_names": list(FEATURE_NAMES),
        "records": [
            {
                "setting_id": setting["setting_id"],
                "family_id": setting["family_id"],
                "alawarchwilio_stable_id": setting["alawarchwilio_stable_id"],
                "irishman_split": setting["irishman_split"],
                "irishman_row_index": setting["irishman_row_index"],
                "dataset_hash_verified": True,
                "source_record_hash_verified": True,
                "normalized_fingerprint_verified": True,
                "deterministic_tie_break_verified": True,
                "inline_key_field_count": result.inline_key_field_count,
                "features": {name: round(value, 12) for name, value in result.features.items()},
            }
            for setting, result in zip(settings, parsed, strict=True)
        ],
    }
    distances = {
        "metric": "uniform-weight squared Euclidean over nine frozen features",
        "pairs": [
            {
                "left": settings[left]["setting_id"],
                "right": settings[right]["setting_id"],
                "distance": round(feature_distance(features[left], features[right]), 12),
            }
            for left in range(8)
            for right in range(left + 1, 8)
            if family_indexes[left] != family_indexes[right]
        ],
    }
    qubo_coefficients = {
        "offset": model.offset,
        "matrix": [[round(value, 15) for value in row] for row in model.qubo],
    }
    qubo = {
        "convention": "offset + diagonal + upper-triangular pair terms",
        "variable_order": [setting["setting_id"] for setting in settings],
        "one_hot_penalty_A": ONE_HOT_PENALTY,
        "musical_weight_B": 1.0,
        **qubo_coefficients,
        "coefficient_sha256": _coefficient_hash(qubo_coefficients),
    }
    ising_coefficients = {
        "constant": round(model.ising_constant, 15),
        "h": [round(value, 15) for value in model.h],
        "j": [[round(value, 15) for value in row] for row in model.j],
    }
    ising = {
        "convention": "x=(1-z)/2; constant + sum(h_i z_i) + sum(J_ij z_i z_j)",
        "variable_order": [setting["setting_id"] for setting in settings],
        **ising_coefficients,
        "coefficient_sha256": _coefficient_hash(ising_coefficients),
    }
    exact_public = {key: value for key, value in exact.items() if key not in {"states", "model"}}
    for key in ("minimum_energy", "gap_to_next_non_optimal", "minimum_infeasible_energy"):
        exact_public[key] = round(float(exact_public[key]), 15)
    exact_public["qubo_coefficient_sha256"] = qubo["coefficient_sha256"]
    exact_public["ising_coefficient_sha256"] = ising["coefficient_sha256"]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.output_dir / "derived-features.json", derived)
    _write_json(args.output_dir / "pairwise-distances.json", distances)
    _write_json(args.output_dir / "qubo.json", qubo)
    _write_json(args.output_dir / "ising.json", ising)
    _write_json(args.output_dir / "exact-result.json", exact_public)

    optima = ", ".join(f"`{value}`" for value in exact_public["optimum_bitstrings"])
    report = f"""# EXP-009A-R1 exact report

Exact enumeration is authoritative. All 256 assignments were evaluated directly, as a QUBO, and
as an Ising Hamiltonian after the separately frozen successor parser proof.

- Global optimum bitstrings: {optima}
- Canonical optimum: `{exact_public["canonical_optimum"]}`
- Minimum energy: `{exact_public["minimum_energy"]:.15f}`
- Distinct rounded energy levels: `{exact_public["distinct_energy_levels"]}`
- Gap to next non-optimal level: `{exact_public["gap_to_next_non_optimal"]:.15f}`
- Maximum direct/QUBO/Ising disagreement: `{exact_public["maximum_agreement_error"]:.3e}`
- All optima satisfy one-hot: `{exact_public["all_optima_feasible"]}`
- Minimum infeasible energy: `{exact_public["minimum_infeasible_energy"]:.15f}`
- Uniform optimum-class baseline: `{exact_public["uniform_optimum_class_baseline"]:.8f}`
- QUBO coefficient SHA-256: `{qubo["coefficient_sha256"]}`
- Ising coefficient SHA-256: `{ising["coefficient_sha256"]}`

The inherited one-hot proof is data-independent: feasible energy is at most 6 and every infeasible
state costs at least 7. This optimum is a result of the frozen coarse objective, not musical truth
or authenticity. No QAOA or hardware result contributes to this exact evidence.
"""
    (args.output_dir / "EXACT-REPORT.md").write_text(report, encoding="utf-8")
    print("EXP-009A-R1 exact gate passed for 256 assignments; no notation emitted.")


if __name__ == "__main__":
    main()
