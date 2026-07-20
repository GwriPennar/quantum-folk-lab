from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from quantum_folk_lab.hardware_replication_evidence import load_hardware_replication_evidence


def test_governed_hardware_evidence_loads_exact_headline_values() -> None:
    evidence = load_hardware_replication_evidence(Path.cwd())
    exp010d = evidence.exp010d
    exp011 = evidence.exp011
    assert (exp010d.backend, exp010d.unique_cells, exp010d.pub_count, exp010d.shots_per_pub) == (
        "ibm_fez",
        25,
        32,
        4096,
    )
    assert exp010d.spearman_rho == 0.96
    assert exp010d.classification == "LANDSCAPE SUPPORTED"
    assert (exp010d.centre_rank, exp010d.centre_most_likely_state) == (1, "1010")
    assert (exp011.backend, exp011.unique_cells, exp011.pub_count, exp011.shots_per_pub) == (
        "ibm_fez",
        81,
        88,
        4096,
    )
    assert exp011.spearman_rho == 0.9046747967479675
    assert exp011.embedded_25_rho == 0.9315384615384615
    assert exp011.cross_run_rho == 0.9776923076923076
    assert exp011.cross_run_mean_absolute_difference == 0.01871101322274423
    assert exp011.classification == "STRONGLY REPLICATED"
    assert (exp011.centre_rank, exp011.centre_most_likely_state) == (4, "1010")


def test_missing_or_malformed_governed_evidence_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="could not be loaded"):
        load_hardware_replication_evidence(tmp_path)

    source = Path("experiments/EXP-010D-hardware-parameter-landscape-run")
    target = tmp_path / "experiments" / source.name
    target.mkdir(parents=True)
    for name in ("hardware-analysis.json", "execution-manifest.json"):
        shutil.copyfile(source / name, target / name)
    payload = json.loads((target / "hardware-analysis.json").read_text(encoding="utf-8"))
    payload["primary"]["classification"] = "CHANGED"
    (target / "hardware-analysis.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="classification"):
        load_hardware_replication_evidence(tmp_path)


def test_learning_console_renders_replication_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_" + "API" + "_KEY", raising=False)
    monkeypatch.delenv("IBM_" + "QUANTUM_TOKEN", raising=False)
    app = AppTest.from_file("apps/learning_console/app.py")
    app.run(timeout=30)
    assert not app.exception
    rendered = "\n".join(
        str(element.value)
        for collection in (
            app.header,
            app.subheader,
            app.markdown,
            app.caption,
            app.success,
            app.warning,
            app.metric,
        )
        for element in collection
    )
    for expected in (
        "IBM Hardware Replication",
        "EXP-010D — Controlled hardware landscape",
        "EXP-011 — Dense independent replication",
        "LANDSCAPE SUPPORTED",
        "STRONGLY REPLICATED",
        "Control warning retained",
        "Exact classical enumeration remains authoritative",
        "do not demonstrate quantum advantage or speedup",
        "No IBM access is needed",
    ):
        assert expected in rendered
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Ideal/hardware rho"] == "0.9600"
    assert metrics["Full-grid ideal/hardware rho"] == "0.9047"
    assert metrics["Embedded 25-cell rho"] == "0.9315"
    assert metrics["Cross-run rho"] == "0.9777"
    assert metrics["Repeated-cell mean absolute difference"] == "0.0187"


def test_renderer_contains_no_unsupported_claim_or_service_access() -> None:
    renderer = Path("apps/learning_console/renderers/hardware_replication.py").read_text(
        encoding="utf-8"
    )
    assert "do not demonstrate quantum advantage" in renderer
    for forbidden in (
        "qiskitruntimeservice",
        "samplerv2",
        "save_account",
        "quantum advantage achieved",
        "proves musical quality",
    ):
        assert forbidden not in renderer.lower()
