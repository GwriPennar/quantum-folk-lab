from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, cast

ROOT = Path("experiments/EXP-010D-hardware-parameter-landscape")
QUBO_HASH = "96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e"
ISING_HASH = "635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5"


def load(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((ROOT / name).read_text(encoding="utf-8")))


def test_grid_is_complete_unique_and_frozen() -> None:
    grid = load("grid-manifest.json")
    points = grid["points"]
    assert isinstance(points, list) and len(points) == 25
    assert len({point["point_id"] for point in points}) == 25
    assert {(point["i"], point["j"]) for point in points} == {
        (i, j) for i in range(-2, 3) for j in range(-2, 3)
    }
    assert grid["gamma_values"] == [
        "2.517797519192915",
        "2.9177975191929155",
        "3.3177975191929154",
        "3.7177975191929153",
        "4.117797519192916",
    ]
    assert grid["beta_values"] == [
        "2.0765052999860263",
        "2.276505299986026",
        "2.476505299986026",
        "2.6765052999860264",
        "2.876505299986026",
    ]


def test_ideal_landscape_recomputes_frozen_centre_and_envelope() -> None:
    landscape = load("ideal-landscape.json")
    cells = landscape["cells"]
    assert isinstance(cells, list) and len(cells) == 25
    assert landscape["qubo_sha256"] == QUBO_HASH
    assert landscape["ising_sha256"] == ISING_HASH
    assert all(abs(sum(cell["ideal_distribution"].values()) - 1.0) < 1e-12 for cell in cells)
    centre = next(cell for cell in cells if cell["point_id"] == "g+0_b+0")
    assert abs(centre["r"] - 0.5999118429921135) < 1e-12
    assert centre["most_likely_state"] == "1010"
    envelope = landscape["envelope"]
    assert envelope["centre_is_best"] is True
    assert abs(envelope["lowest_grid_r"] - 0.3278159529446157) < 1e-12
    assert abs(envelope["centre_to_outer_ring_median_gap"] - 0.1980716306580208) < 1e-12


def test_execution_order_has_four_centres_controls_and_all_non_centre_points() -> None:
    order = load("execution-order.json")
    sequence = order["sequence"]
    assert isinstance(sequence, list) and len(sequence) == 32
    assert [row["execution"] for row in sequence] == list(range(1, 33))
    assert sum(row["kind"] == "centre" for row in sequence) == 4
    assert sum(row["kind"] == "control" for row in sequence) == 4
    landscape = [row for row in sequence if row["kind"] == "landscape"]
    assert len(landscape) == 24
    assert len({row["point_id"] for row in landscape}) == 24
    for block in range(1, 5):
        rows = [row for row in sequence if row["block"] == block]
        expected = ["control", "centre"] if block % 2 else ["centre", "control"]
        assert [row["kind"] for row in rows[:2]] == expected
        assert len(rows) == 8


def test_order_matches_single_seeded_shuffle() -> None:
    grid = load("grid-manifest.json")
    points = [point for point in grid["points"] if point["point_id"] != "g+0_b+0"]
    random.Random(20260720).shuffle(points)
    expected = [point["point_id"] for point in points]
    sequence = load("execution-order.json")["sequence"]
    actual = [row["point_id"] for row in sequence if row["kind"] == "landscape"]
    assert actual == expected


def test_workload_template_is_fail_closed_and_exp010d_specific() -> None:
    manifest = load("hardware-workload-manifest.template.json")
    assert manifest["submission_default"] is False
    assert manifest["authorization"] is False
    assert manifest["submitted"] is False
    assert manifest["job_id"] is None
    assert manifest["automatic_retries"] == 0
    assert manifest["pub_executions"] == 32
    assert manifest["hardware_jobs"] == 1
    assert manifest["authorization_required"] == "I AUTHORIZE ONE EXP-010D IBM QPU JOB"
    assert manifest["exp010c_authorization_accepted"] is False
    assert manifest["billable_qpu_seconds_ceiling"] == 180


def test_plan_has_no_live_or_result_artifacts_and_generator_has_no_ibm_surface() -> None:
    forbidden_names = {
        "submission-intent.json",
        "submission-receipt.json",
        "backend-snapshot.json",
        "hardware-result.json",
    }
    assert forbidden_names.isdisjoint(path.name for path in ROOT.iterdir())
    source = Path("scripts/build_exp010d_plan.py").read_text(encoding="utf-8")
    for forbidden in (
        "QiskitRuntimeService",
        "qiskit_ibm_runtime",
        "service.backends",
        "SamplerV2",
        "save_account",
    ):
        assert forbidden not in source
