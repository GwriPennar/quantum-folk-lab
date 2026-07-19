import json
from pathlib import Path

ROOT = Path(__file__).parents[1] / "experiments" / "EXP-009A-R2-real-data-quantum"


def test_detectability_protocol_and_metrics_are_complete() -> None:
    result = json.loads((ROOT / "detectability-result.json").read_text(encoding="utf-8"))
    protocol = result["protocol"]
    assert protocol["resamples"] == 10_000
    assert protocol["shots_per_resample"] == 4096
    assert protocol["seed"] == 42
    assert result["primary_hardware_metric_selected"] is False
    assert set(result["metrics"]) == {
        "feasible_subspace_mass",
        "optimum_class_mass",
        "four_lowest_feasible_mass",
        "expected_energy",
        "feasible_energy_probability_spearman",
    }
    for metric in result["metrics"].values():
        assert 0 <= metric["estimated_power"] <= 1
        assert (
            metric["alternative_uncertainty"]["q025"] <= metric["alternative_uncertainty"]["q975"]
        )


def test_fable_package_is_non_sensitive_and_does_not_authorize_hardware() -> None:
    package = json.loads((ROOT / "fable-hardware-inputs.json").read_text(encoding="utf-8"))
    assert package["hardware_contacted"] is False
    assert package["primary_hardware_metric_selected"] is False
    assert package["logical_width"] == 8
    assert package["untranspiled_p1_two_qubit_interaction_count"] == 28
    assert len(package["feasible_state_energies"]) == 16
    text = json.dumps(package).lower()
    for forbidden in (
        "abc notation",
        "credential",
        "api key",
        "instance crn",
        "ordered_notes",
        "ordered_intervals",
    ):
        assert forbidden not in text
