import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1] / "experiments" / "EXP-009A-R2-real-data-quantum"


def test_qaoa_result_obeys_frozen_protocol_and_probability_contracts() -> None:
    result = json.loads((ROOT / "qaoa-result.json").read_text(encoding="utf-8"))
    protocol = result["protocol"]
    assert protocol["depth"] == 1
    assert protocol["shots"] == 4096
    assert protocol["seed"] == 42
    assert protocol["optimizer"] == "COBYLA"
    assert protocol["optimizer_max_iterations"] == 80
    assert protocol["ibm_service_used"] is False
    assert sum(result["shot_counts"].values()) == 4096
    assert sum(result["ideal_distribution"].values()) == pytest.approx(1.0, abs=1e-12)
    assert result["shot_feasible_subspace_mass"] == 1.0
    assert result["logical_width"] == 8


def test_qaoa_result_uses_exact_optimum_and_is_non_sensitive() -> None:
    result = json.loads((ROOT / "qaoa-result.json").read_text(encoding="utf-8"))
    exact = json.loads((ROOT / "exact-result.json").read_text(encoding="utf-8"))
    assert result["optimum_bitstrings"] == exact["optimum_bitstrings"]
    assert result["optimum_class_size"] == exact["optimum_class_size"]
    text = json.dumps(result).lower()
    for forbidden in ("abc notation", "credential", "runtime service", "backend_name"):
        assert forbidden not in text
