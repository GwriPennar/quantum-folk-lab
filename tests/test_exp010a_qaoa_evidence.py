import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1] / "experiments" / "EXP-010A-compact-family-encoding"


def test_qaoa_protocol_and_probability_contracts() -> None:
    result = json.loads((ROOT / "qaoa-result.json").read_text(encoding="utf-8"))
    protocol = result["protocol"]
    assert protocol["logical_width"] == 4
    assert protocol["depth"] == 1
    assert protocol["gamma_grid_points"] == 257
    assert protocol["beta_grid_points"] == 129
    assert protocol["grid_evaluations"] == 33_153
    assert protocol["refinement_starts"] == 16
    assert protocol["postselection"] is False
    assert protocol["ibm_service_used"] is False
    assert all(item["within_bounds"] for item in result["refinements"])
    assert sum(item["ideal_probability"] for item in result["states"]) == pytest.approx(
        1.0, abs=1e-12
    )
    assert sum(item["shot_count"] for item in result["states"]) == 4096
    assert result["maximum_analytic_qiskit_probability_error"] <= 1e-12


def test_primary_metric_and_readiness_gate_are_predeclared_and_pass() -> None:
    result = json.loads((ROOT / "qaoa-result.json").read_text(encoding="utf-8"))
    assert result["uniform16_baselines"]["optimum_mass"] == 1 / 16
    assert result["uniform16_baselines"]["four_lowest_mass"] == 4 / 16
    assert result["ideal_metrics"]["relative_expected_energy_improvement"] >= 0.10
    assert (
        result["detectability"]["metrics"]["relative_expected_energy_improvement"][
            "estimated_power"
        ]
        >= 0.80
    )
    assert (
        result["ideal_metrics"]["expected_raw_energy"]
        < result["uniform16_baselines"]["expected_raw_energy"]
    )
    assert result["hardware_readiness_gate"]["passed"] is True
