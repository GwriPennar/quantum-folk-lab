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
    assert len(evidence.ideal_hardware_points) == 25
    assert len(evidence.cross_run_points) == 25
    assert {point.cell_id for point in evidence.ideal_hardware_points} == {
        point.cell_id for point in evidence.cross_run_points
    }
    centre = next(point for point in evidence.ideal_hardware_points if point.cell_id == "g+0_b+0")
    assert centre.ideal_r == 0.5999118429921135
    assert centre.hardware_r == 0.5184178203750598
    repeated_centre = next(
        point for point in evidence.cross_run_points if point.cell_id == "g+0_b+0"
    )
    assert repeated_centre.exp010d_r == 0.5184178203750598
    assert repeated_centre.exp011_r == 0.4962957979192144

    d_payload = json.loads(
        Path(
            "experiments/EXP-010D-hardware-parameter-landscape-run/hardware-analysis.json"
        ).read_text(encoding="utf-8")
    )
    e_payload = json.loads(
        Path("experiments/EXP-011-dense-hardware-landscape-run/hardware-analysis.json").read_text(
            encoding="utf-8"
        )
    )
    d_cells = {cell["point_id"]: cell for cell in d_payload["cells"]}
    e_cells = {cell["point_id"]: cell for cell in e_payload["cells"]}
    assert {
        (point.cell_id, point.ideal_r, point.hardware_r) for point in evidence.ideal_hardware_points
    } == {(cell_id, cell["ideal_r"], cell["r"]) for cell_id, cell in d_cells.items()}
    for point in evidence.cross_run_points:
        gamma, beta = point.cell_id.removeprefix("g").split("_b")
        exp011_id = f"g{2 * (int(gamma) + 2)}_b{2 * (int(beta) + 2)}"
        assert point.exp010d_r == d_cells[point.cell_id]["r"]
        assert point.exp011_r == e_cells[exp011_id]["r"]


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


def test_malformed_chart_cell_fails_closed_and_sources_are_governed(tmp_path: Path) -> None:
    experiments = tmp_path / "experiments"
    for directory in (
        "EXP-010D-hardware-parameter-landscape-run",
        "EXP-011-dense-hardware-landscape-run",
    ):
        source = Path("experiments") / directory
        target = experiments / directory
        target.mkdir(parents=True)
        for name in ("hardware-analysis.json", "execution-manifest.json"):
            shutil.copyfile(source / name, target / name)

    analysis_path = (
        experiments / "EXP-010D-hardware-parameter-landscape-run" / "hardware-analysis.json"
    )
    payload = json.loads(analysis_path.read_text(encoding="utf-8"))
    del payload["cells"][0]["ideal_r"]
    analysis_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="ideal_r"):
        load_hardware_replication_evidence(tmp_path)

    loader = Path("src/quantum_folk_lab/hardware_replication_evidence.py").read_text(
        encoding="utf-8"
    )
    assert "EXP-010D-hardware-parameter-landscape-run" in loader
    assert "EXP-011-dense-hardware-landscape-run" in loader


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
        "Replicated IBM hardware landscape",
        "First landscape test",
        "Governed experiment EXP-010D",
        "Independent denser replication",
        "Governed experiment EXP-011",
        "LANDSCAPE SUPPORTED",
        "STRONGLY REPLICATED",
        "Control warning retained",
        "Exact classical enumeration remains authoritative",
        "do not demonstrate quantum advantage or speedup",
        "No IBM access is needed",
        "Did real hardware preserve the predicted landscape?",
        "Did the hardware pattern reproduce?",
        "A parameter landscape is a map of how well different circuit settings perform",
        "submitted circuits (PUBs)",
        "measured 4,096 times (shots)",
    ):
        assert expected in rendered
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Ordering agreement (rho)"] == "0.9600"
    assert metrics["Full-grid ordering agreement (rho)"] == "0.9047"
    assert metrics["Embedded 25-cell rho"] == "0.9315"
    assert metrics["Cross-run agreement (rho)"] == "0.9777"
    assert metrics["Repeated-cell mean absolute difference"] == "0.0187"
    renderer = Path("apps/learning_console/renderers/hardware_replication.py").read_text(
        encoding="utf-8"
    )
    assert renderer.count("st.vega_lite_chart(") == 2


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
