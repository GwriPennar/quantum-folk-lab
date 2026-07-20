import json
from pathlib import Path

ROOT = Path(__file__).parents[1] / "experiments" / "EXP-010A-compact-family-encoding"


def test_fable_package_contains_complete_compact_evidence() -> None:
    package = json.loads((ROOT / "fable-hardware-inputs.json").read_text(encoding="utf-8"))
    assert package["variable_order"] == [
        "blackbird",
        "bold-deserter",
        "catherine-tyrrell",
        "merry-old-woman",
    ]
    assert len(package["compact_to_r2_mapping"]) == 16
    assert len(package["exact_spectrum"]) == 16
    assert package["logical_width"] == 4
    assert package["nonzero_quadratic_interactions"] == 6
    assert package["untranspiled_p1_two_qubit_interaction_count"] == 6
    assert package["hardware_readiness_gate"]["passed"] is True
    assert package["r2_comparison"]["same_exact_musical_spectrum"] is True


def test_hardware_package_is_non_sensitive_and_local_only() -> None:
    package = json.loads((ROOT / "fable-hardware-inputs.json").read_text(encoding="utf-8"))
    assert package["ibm_service_contacted"] is False
    assert package["backend_queried"] is False
    assert package["qpu_job_submitted"] is False
    text = json.dumps(package).lower()
    for forbidden in (
        "abc notation",
        "credential",
        "api key",
        "instance crn",
        "ordered_notes",
        "metadata contents",
    ):
        assert forbidden not in text
