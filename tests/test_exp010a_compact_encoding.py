import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from quantum_folk_lab.compact_family_encoding import compact_to_r2

ROOT = Path(__file__).parents[1] / "experiments" / "EXP-010A-compact-family-encoding"


def _load(name: str) -> Any:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def _hash(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_complete_bijection_and_exact_equivalence() -> None:
    exact = _load("compact-exact-result.json")
    assert exact["state_count"] == 16
    assert exact["all_states_valid"] is True
    assert len({item["r2_bitstring"] for item in exact["mapping"]}) == 16
    assert exact["maximum_representation_error"] <= 1e-12
    assert exact["maximum_r2_spectrum_error"] <= 1e-12
    for item in exact["mapping"]:
        assert item["r2_bitstring"] == compact_to_r2(item["compact_bitstring"])
        assert item["compact_qubo_energy"] == pytest.approx(item["r2_direct_energy"], abs=1e-12)
        assert item["compact_ising_energy"] == pytest.approx(item["r2_direct_energy"], abs=1e-12)


def test_compact_optimum_and_coefficient_hashes() -> None:
    exact = _load("compact-exact-result.json")
    qubo = _load("compact-qubo.json")
    ising = _load("compact-ising.json")
    assert exact["canonical_optimum"] == "1010"
    assert exact["mapped_r2_optimum_bitstrings"] == ["01100110"]
    assert qubo["penalty_term"] is False
    assert _hash({"offset": qubo["offset"], "matrix": qubo["matrix"]}) == qubo["coefficient_sha256"]
    assert (
        _hash({"constant": ising["constant"], "h": ising["h"], "j": ising["j"]})
        == ising["coefficient_sha256"]
    )
