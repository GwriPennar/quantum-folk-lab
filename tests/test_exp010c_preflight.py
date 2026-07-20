from pathlib import Path


def test_preflight_has_no_submission_surface() -> None:
    source = Path("scripts/run_exp010c_preflight.py").read_text(encoding="utf-8")
    for forbidden in ("Sampler", "Estimator", "Session", "Batch", "save_account", "service.run("):
        assert forbidden not in source
    assert "service.backends(" in source
    assert "use_fractional_gates=False" in source


def test_manifest_is_fail_closed_after_generation() -> None:
    path = Path("experiments/EXP-010C-read-only-ibm-preflight/submission-manifest.json")
    if not path.exists():
        return
    import json

    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["authorization"] is False
    assert manifest["submitted"] is False
    assert manifest["job_id"] is None
    assert manifest["intent_created"] is False
    assert manifest["receipt_created"] is False
    assert manifest["shots_per_pub"] == 4096
    assert manifest["pub_count"] == 2
