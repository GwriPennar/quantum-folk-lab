"""Validated read models for governed EXP-010D and EXP-011 public evidence."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HardwareLandscapeEvidence:
    """Judge-facing fields loaded from one immutable experiment result package."""

    experiment_id: str
    backend: str
    unique_cells: int
    pub_count: int
    shots_per_pub: int
    spearman_rho: float
    classification: str
    centre_rank: int
    centre_most_likely_state: str
    embedded_25_rho: float | None = None
    cross_run_rho: float | None = None
    cross_run_mean_absolute_difference: float | None = None


@dataclass(frozen=True)
class IdealHardwarePoint:
    """One governed EXP-010D cell for the ideal/hardware chart."""

    cell_id: str
    ideal_r: float
    hardware_r: float


@dataclass(frozen=True)
class CrossRunPoint:
    """One governed cell shared by EXP-010D and EXP-011."""

    cell_id: str
    exp010d_r: float
    exp011_r: float


@dataclass(frozen=True)
class HardwareReplicationEvidence:
    """The two governed layers shown together in the Learning Console."""

    exp010d: HardwareLandscapeEvidence
    exp011: HardwareLandscapeEvidence
    ideal_hardware_points: tuple[IdealHardwarePoint, ...]
    cross_run_points: tuple[CrossRunPoint, ...]


def _object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"governed evidence could not be loaded: {path.name}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"governed evidence must be a JSON object: {path.name}")
    return value


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"governed evidence field is malformed: {field}")
    return value


def _list(value: object, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"governed evidence field is malformed: {field}")
    return value


def _string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"governed evidence field is malformed: {field}")
    return value


def _integer(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"governed evidence field is malformed: {field}")
    return value


def _number(value: object, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"governed evidence field is malformed: {field}")
    return float(value)


def _assert_equal(actual: object, expected: object, field: str) -> None:
    if actual != expected:
        raise ValueError(f"governed evidence mismatch: {field}")


def _cell_map(analysis: dict[str, Any], experiment: str) -> dict[str, dict[str, Any]]:
    cells: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(_list(analysis.get("cells"), f"{experiment} cells")):
        cell = _mapping(value, f"{experiment} cell {index}")
        point_id = _string(cell.get("point_id"), f"{experiment} point_id")
        if point_id in cells:
            raise ValueError(f"governed evidence contains duplicate cell: {point_id}")
        cells[point_id] = cell
    return cells


def _exp011_shared_id(exp010d_id: str) -> str:
    match = re.fullmatch(r"g([+-][0-2])_b([+-][0-2])", exp010d_id)
    if match is None:
        raise ValueError(f"governed EXP-010D cell id is malformed: {exp010d_id}")
    gamma_index = 2 * (int(match.group(1)) + 2)
    beta_index = 2 * (int(match.group(2)) + 2)
    return f"g{gamma_index}_b{beta_index}"


def _load_landscape(
    root: Path,
    *,
    expected_id: str,
    expected_cells: int,
    expected_pubs: int,
    expected_classification: str,
    warning_field: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    analysis = _object(root / "hardware-analysis.json")
    manifest = _object(root / "execution-manifest.json")
    _assert_equal(analysis.get("experiment_id"), expected_id, "experiment_id")
    _assert_equal(manifest.get("experiment_id"), expected_id, "manifest experiment_id")
    _assert_equal(analysis.get("terminal_status"), "DONE", "terminal_status")
    _assert_equal(len(_list(analysis.get("cells"), "cells")), expected_cells, "unique cells")
    _assert_equal(analysis.get("pub_count"), expected_pubs, "analysis pub_count")
    _assert_equal(manifest.get("pub_count"), expected_pubs, "manifest pub_count")
    _assert_equal(manifest.get("backend"), "ibm_fez", "backend")
    _assert_equal(manifest.get("shots_per_pub"), 4096, "shots_per_pub")
    primary = _mapping(analysis.get("primary"), "primary")
    _assert_equal(primary.get("classification"), expected_classification, "classification")
    warnings = _mapping(analysis.get("warnings"), "warnings")
    _assert_equal(warnings.get(warning_field), True, "control warning")
    return analysis, manifest


def load_hardware_replication_evidence(repo_root: Path) -> HardwareReplicationEvidence:
    """Load governed aggregate evidence without computation or external services."""

    experiments = repo_root / "experiments"
    exp010d_root = experiments / "EXP-010D-hardware-parameter-landscape-run"
    exp011_root = experiments / "EXP-011-dense-hardware-landscape-run"
    d_analysis, d_manifest = _load_landscape(
        exp010d_root,
        expected_id="EXP-010D-R3",
        expected_cells=25,
        expected_pubs=32,
        expected_classification="LANDSCAPE SUPPORTED",
        warning_field="control_quality",
    )
    e_analysis, e_manifest = _load_landscape(
        exp011_root,
        expected_id="EXP-011",
        expected_cells=81,
        expected_pubs=88,
        expected_classification="STRONGLY REPLICATED",
        warning_field="absolute_mean_control_r_gt_0_05",
    )
    d_primary = _mapping(d_analysis["primary"], "EXP-010D primary")
    d_secondary = _mapping(d_analysis["secondary"], "EXP-010D secondary")
    e_primary = _mapping(e_analysis["primary"], "EXP-011 primary")
    e_secondary = _mapping(e_analysis["secondary"], "EXP-011 secondary")
    d_cells = _cell_map(d_analysis, "EXP-010D")
    e_cells = _cell_map(e_analysis, "EXP-011")

    exp010d = HardwareLandscapeEvidence(
        experiment_id=_string(d_analysis["experiment_id"], "EXP-010D id"),
        backend=_string(d_manifest["backend"], "EXP-010D backend"),
        unique_cells=len(_list(d_analysis["cells"], "EXP-010D cells")),
        pub_count=_integer(d_analysis["pub_count"], "EXP-010D pub_count"),
        shots_per_pub=_integer(d_manifest["shots_per_pub"], "EXP-010D shots"),
        spearman_rho=_number(d_primary["spearman_rho"], "EXP-010D rho"),
        classification=_string(d_primary["classification"], "EXP-010D classification"),
        centre_rank=_integer(d_secondary["centre_rank"], "EXP-010D centre rank"),
        centre_most_likely_state=_string(
            d_secondary["aggregate_most_likely_state"], "EXP-010D centre state"
        ),
    )
    exp011 = HardwareLandscapeEvidence(
        experiment_id=_string(e_analysis["experiment_id"], "EXP-011 id"),
        backend=_string(e_manifest["backend"], "EXP-011 backend"),
        unique_cells=len(_list(e_analysis["cells"], "EXP-011 cells")),
        pub_count=_integer(e_analysis["pub_count"], "EXP-011 pub_count"),
        shots_per_pub=_integer(e_manifest["shots_per_pub"], "EXP-011 shots"),
        spearman_rho=_number(e_primary["spearman_rho"], "EXP-011 rho"),
        classification=_string(e_primary["classification"], "EXP-011 classification"),
        centre_rank=_integer(e_secondary["centre_rank"], "EXP-011 centre rank"),
        centre_most_likely_state=_string(
            e_secondary["centre_most_likely_state"], "EXP-011 centre state"
        ),
        embedded_25_rho=_number(
            e_secondary["embedded_25_ideal_hardware_rho"], "EXP-011 embedded rho"
        ),
        cross_run_rho=_number(e_secondary["cross_run_25_cell_rho"], "EXP-011 cross-run rho"),
        cross_run_mean_absolute_difference=_number(
            e_secondary["cross_run_25_cell_mean_absolute_difference_r"],
            "EXP-011 cross-run difference",
        ),
    )
    ideal_hardware_points = tuple(
        IdealHardwarePoint(
            cell_id=point_id,
            ideal_r=_number(cell.get("ideal_r"), f"EXP-010D {point_id} ideal_r"),
            hardware_r=_number(cell.get("r"), f"EXP-010D {point_id} r"),
        )
        for point_id, cell in sorted(d_cells.items())
    )
    cross_run_points = tuple(
        CrossRunPoint(
            cell_id=point_id,
            exp010d_r=_number(cell.get("r"), f"EXP-010D {point_id} r"),
            exp011_r=_number(
                e_cells.get(_exp011_shared_id(point_id), {}).get("r"),
                f"EXP-011 match for {point_id}",
            ),
        )
        for point_id, cell in sorted(d_cells.items())
    )
    _assert_equal(len(ideal_hardware_points), 25, "EXP-010D chart point count")
    _assert_equal(len(cross_run_points), 25, "cross-run chart point count")
    return HardwareReplicationEvidence(
        exp010d=exp010d,
        exp011=exp011,
        ideal_hardware_points=ideal_hardware_points,
        cross_run_points=cross_run_points,
    )
