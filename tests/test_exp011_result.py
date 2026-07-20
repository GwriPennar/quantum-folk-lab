from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

ROOT = Path("experiments/EXP-011-dense-hardware-landscape-run")
JOB_ID = "d9et3cineu4c739os5mg"


def load(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((ROOT / name).read_text(encoding="utf-8")))


def test_all_frozen_pubs_are_present_and_complete() -> None:
    counts = load("hardware-counts.json")
    assert counts["job_id"] == JOB_ID and counts["pub_count"] == 88
    pubs = counts["pubs"]
    assert len(pubs) == 88
    assert [row["execution"] for row in pubs] == list(range(1, 89))
    assert all(sum(row["counts"].values()) == 4096 for row in pubs)
    assert sum(row["kind"] == "landscape" for row in pubs) == 80
    assert sum(row["kind"] == "centre" for row in pubs) == 4
    assert sum(row["kind"] == "control" for row in pubs) == 4


def test_frozen_primary_and_replication_results() -> None:
    analysis = load("hardware-analysis.json")
    primary = analysis["primary"]
    secondary = analysis["secondary"]
    assert analysis["terminal_status"] == "DONE" and analysis["job_id"] == JOB_ID
    assert abs(primary["spearman_rho"] - 0.9046747967479675) < 1e-15
    assert primary["permutation_p_value"] == 0.00000999990000099999
    assert primary["classification"] == "STRONGLY REPLICATED"
    assert primary["permutations"] == 100000 and primary["bootstrap_resamples"] == 10000
    assert secondary["centre_rank"] == 4
    assert secondary["centre_top_five"] is True and secondary["centre_top_three"] is False
    assert abs(secondary["embedded_25_ideal_hardware_rho"] - 0.9315384615384615) < 1e-15
    assert abs(secondary["cross_run_25_cell_rho"] - 0.9776923076923076) < 1e-15


def test_warning_and_submission_evidence_are_preserved() -> None:
    analysis = load("hardware-analysis.json")
    assert analysis["warnings"] == {
        "absolute_mean_control_r_gt_0_05": True,
        "centre_sample_sd_gt_0_05": False,
        "cross_run_25_cell_rho_lt_0_70": False,
        "embedded_25_rho_lt_0_50": False,
    }
    execution = load("execution-manifest.json")
    assert execution["job_id"] == JOB_ID and execution["retry"] is False
    assert execution["pub_count"] == 88 and execution["shots_per_pub"] == 4096
    assert execution["all_pubs_present"] is True
    identity = load("run-identity.json")
    assert identity["submitted"] is True and identity["job_id"] == JOB_ID
    assert identity["intent_created"] is True and identity["receipt_created"] is True
    assert not (ROOT / "submission-intent.json").exists()
    assert not (ROOT / "submission-receipt.json").exists()
