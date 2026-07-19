import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[1] / "experiments" / "EXP-009A-R2-real-data-quantum"


def _load(name: str) -> Any:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def _hash(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_exact_evidence_contract_and_coefficient_hashes() -> None:
    exact = _load("exact-result.json")
    qubo = _load("qubo.json")
    ising = _load("ising.json")
    assert exact["assignment_count"] == 256
    assert exact["all_optima_feasible"] is True
    assert exact["maximum_agreement_error"] <= 1e-10
    assert len(exact["feasible_state_energies"]) == 16
    assert exact["optimum_class_size"] == len(exact["optimum_bitstrings"])
    assert exact["uniform_feasible_subspace_baseline"] == 16 / 256
    qubo_coefficients = {"offset": qubo["offset"], "matrix": qubo["matrix"]}
    ising_coefficients = {"constant": ising["constant"], "h": ising["h"], "j": ising["j"]}
    assert _hash(qubo_coefficients) == exact["qubo_coefficient_sha256"]
    assert _hash(ising_coefficients) == exact["ising_coefficient_sha256"]


def test_derived_evidence_is_aggregate_only() -> None:
    derived = _load("derived-features.json")
    assert len(derived["records"]) == 8
    assert all(
        set(record["inline_field_counts"]) == {"K", "M", "Q"} for record in derived["records"]
    )
    text = json.dumps(derived).lower()
    for forbidden in ("abc notation", "ordered_notes", "ordered_intervals", "musicxml", "midi"):
        assert forbidden not in text
