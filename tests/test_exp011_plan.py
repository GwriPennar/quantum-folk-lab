from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from quantum_folk_lab.exp011_submission import AUTHORIZATION, IDENTITY

ROOT = Path("experiments/EXP-011-dense-hardware-landscape")
OLD = Path("experiments/EXP-010D-hardware-parameter-landscape/grid-manifest.json")


def load(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((ROOT / name).read_text(encoding="utf-8")))


def test_exact_dense_grid_and_embedded_original() -> None:
    grid = load("grid-manifest.json")
    assert grid["point_count"] == 81 and len(grid["points"]) == 81
    assert len({row["point_id"] for row in grid["points"]}) == 81
    assert grid["gamma_values"] == [
        "2.517797519192915",
        "2.71779751919291525",
        "2.9177975191929155",
        "3.11779751919291545",
        "3.3177975191929154",
        "3.51779751919291535",
        "3.7177975191929153",
        "3.91779751919291565",
        "4.117797519192916",
    ]
    assert grid["beta_values"] == [
        "2.0765052999860263",
        "2.17650529998602615",
        "2.276505299986026",
        "2.376505299986026",
        "2.476505299986026",
        "2.5765052999860262",
        "2.6765052999860264",
        "2.7765052999860262",
        "2.876505299986026",
    ]
    old = json.loads(OLD.read_text(encoding="utf-8"))
    expected = {(row["gamma"], row["beta"]) for row in old["points"]}
    embedded = {(row["gamma"], row["beta"]) for row in grid["points"] if row["exp010d_original"]}
    assert len(embedded) == 25 and embedded == expected


def test_exact_88_pub_order_and_spanning_blocks() -> None:
    rows = load("execution-order.json")["sequence"]
    assert len(rows) == 88 and [row["execution"] for row in rows] == list(range(1, 89))
    assert sum(row["kind"] == "landscape" for row in rows) == 80
    assert sum(row["kind"] == "centre" for row in rows) == 4
    assert sum(row["kind"] == "control" for row in rows) == 4
    landscape = [row for row in rows if row["kind"] == "landscape"]
    assert len({row["point_id"] for row in landscape}) == 80
    assert all(row["shots"] == 4096 for row in rows)
    grid = {row["point_id"]: row for row in load("grid-manifest.json")["points"]}
    for block in range(1, 5):
        selected = [row for row in rows if row["block"] == block]
        expected = ["control", "centre"] if block % 2 else ["centre", "control"]
        assert len(selected) == 22 and [row["kind"] for row in selected[:2]] == expected
        cells = [grid[row["point_id"]] for row in selected[2:]]
        assert {0, 8} <= {row["gamma_index"] for row in cells}
        assert {0, 8} <= {row["beta_index"] for row in cells}


def test_ideal_landscape_and_fail_closed_template() -> None:
    ideal = load("ideal-landscape.json")
    assert len(ideal["cells"]) == 81
    assert all(abs(sum(row["ideal_distribution"].values()) - 1) < 1e-12 for row in ideal["cells"])
    assert ideal["summary"]["centre_ideal_rank"] <= 5
    manifest = load("hardware-workload-manifest.template.json")
    assert manifest["authorization_required"] == AUTHORIZATION
    assert manifest["pub_executions"] == 88 and manifest["absolute_qpu_seconds_ceiling"] == 100
    assert not manifest["authorization"] and not manifest["submitted"]
    assert manifest["job_id"] is None and not manifest["intent_created"]
    IDENTITY.validate()


def test_generator_has_no_ibm_surface_or_live_artifacts() -> None:
    source = Path("scripts/build_exp011_plan.py").read_text(encoding="utf-8")
    for forbidden in (
        "QiskitRuntimeService",
        "qiskit_ibm_runtime",
        "SamplerV2",
        "service.backends",
    ):
        assert forbidden not in source
    assert not any(ROOT.glob("*intent*")) and not any(ROOT.glob("*receipt*"))
