"""Build deterministic, offline-only EXP-011 planning evidence."""

from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "EXP-011-dense-hardware-landscape"
EXACT = ROOT / "experiments" / "EXP-010A-compact-family-encoding" / "compact-exact-result.json"
QUBO_HASH = "96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e"
ISING_HASH = "635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5"
GAMMAS = [
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
BETAS = [
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
SEED = 20260720
SHOTS = 4096


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def mixer(beta: float) -> np.ndarray:
    one = np.array(
        [[math.cos(beta), -1j * math.sin(beta)], [-1j * math.sin(beta), math.cos(beta)]],
        dtype=complex,
    )
    result = np.array([[1.0 + 0.0j]])
    for _ in range(4):
        result = np.kron(result, one)
    return result


def distribution(gamma: float, beta: float, normalized: np.ndarray) -> np.ndarray:
    return np.abs(mixer(beta) @ (np.exp(-1j * gamma * normalized) / 4)) ** 2


def spanning_chunks(points: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Frozen rejection shuffle; every 20-cell block spans both full axes."""
    rng = random.Random(SEED)
    candidate = list(points)
    for _attempt in range(1, 100001):
        rng.shuffle(candidate)
        chunks = [candidate[offset : offset + 20] for offset in range(0, 80, 20)]
        if all(
            {0, 8} <= {int(row["gamma_index"]) for row in chunk}
            and {0, 8} <= {int(row["beta_index"]) for row in chunk}
            for chunk in chunks
        ):
            return [list(chunk) for chunk in chunks]
    raise RuntimeError("no spanning ordering found after 100000 attempts")


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    exact = json.loads(EXACT.read_text(encoding="utf-8"))
    states = [f"{value:04b}" for value in range(16)]
    energy_by_state = {
        row["compact_bitstring"]: float(row["compact_direct_energy"]) for row in exact["mapping"]
    }
    energies = np.array([energy_by_state[state] for state in states])
    e_min, e_uniform = float(np.min(energies)), float(np.mean(energies))
    normalized = (energies - e_min) / float(exact["spectral_range"])
    cells: list[dict[str, Any]] = []
    for gi, gamma_text in enumerate(GAMMAS):
        for bi, beta_text in enumerate(BETAS):
            probabilities = distribution(float(gamma_text), float(beta_text), normalized)
            expected = float(probabilities @ energies)
            likely = min(range(16), key=lambda k: (-float(probabilities[k]), states[k]))
            cells.append(
                {
                    "point_id": f"g{gi}_b{bi}",
                    "gamma_index": gi,
                    "beta_index": bi,
                    "gamma": gamma_text,
                    "beta": beta_text,
                    "ideal_distribution": {
                        s: float(probabilities[k]) for k, s in enumerate(states)
                    },
                    "expected_energy": expected,
                    "r": (e_uniform - expected) / (e_uniform - e_min),
                    "p_1010": float(probabilities[10]),
                    "most_likely_state": states[likely],
                    "ring": "centre"
                    if (gi, bi) == (4, 4)
                    else ("outer" if gi in {0, 8} or bi in {0, 8} else "inner"),
                    "exp010d_original": gi in {0, 2, 4, 6, 8} and bi in {0, 2, 4, 6, 8},
                }
            )
    points = [
        {
            key: cell[key]
            for key in (
                "point_id",
                "gamma_index",
                "beta_index",
                "gamma",
                "beta",
                "ring",
                "exp010d_original",
            )
        }
        for cell in cells
    ]
    grid = {
        "schema_version": 1,
        "experiment_id": "EXP-011",
        "generation": "exact decimal strings",
        "gamma_values": GAMMAS,
        "beta_values": BETAS,
        "point_count": 81,
        "points": points,
        "embedded_exp010d_indices": [0, 2, 4, 6, 8],
    }
    centre = next(cell for cell in cells if cell["point_id"] == "g4_b4")
    ordered = sorted(cells, key=lambda cell: (-float(cell["r"]), cell["point_id"]))
    outer = [float(cell["r"]) for cell in cells if cell["ring"] == "outer"]
    original = [cell for cell in cells if cell["exp010d_original"]]
    landscape = {
        "schema_version": 1,
        "experiment_id": "EXP-011",
        "qubo_sha256": QUBO_HASH,
        "ising_sha256": ISING_HASH,
        "state_order": states,
        "energy_uniform16": e_uniform,
        "energy_minimum": e_min,
        "cells": cells,
        "summary": {
            "best_ideal_cell": ordered[0]["point_id"],
            "best_ideal_r": ordered[0]["r"],
            "centre_ideal_rank": 1 + next(i for i, cell in enumerate(ordered) if cell is centre),
            "centre_r": centre["r"],
            "outer_ring_median_r": float(np.median(outer)),
            "centre_to_outer_ring_gap": float(centre["r"] - np.median(outer)),
            "embedded_exp010d_point_ids": [cell["point_id"] for cell in original],
        },
    }
    noncentre = [point for point in points if point["point_id"] != "g4_b4"]
    chunks = spanning_chunks(noncentre)
    sequence: list[dict[str, Any]] = []
    for block, chunk in enumerate(chunks, start=1):
        anchors = ("control", "centre") if block % 2 else ("centre", "control")
        for kind in anchors:
            sequence.append(
                {
                    "execution": len(sequence) + 1,
                    "block": block,
                    "kind": kind,
                    "point_id": "uniform_control" if kind == "control" else "g4_b4",
                    "gamma": "0" if kind == "control" else GAMMAS[4],
                    "beta": "0" if kind == "control" else BETAS[4],
                    "shots": SHOTS,
                }
            )
        for point in chunk:
            sequence.append(
                {
                    "execution": len(sequence) + 1,
                    "block": block,
                    "kind": "landscape",
                    "point_id": point["point_id"],
                    "gamma": point["gamma"],
                    "beta": point["beta"],
                    "shots": SHOTS,
                }
            )
    order = {
        "schema_version": 1,
        "experiment_id": "EXP-011",
        "seed": SEED,
        "algorithm": "stateful Random(seed).shuffle rejection until all blocks span both axes",
        "total_executions": 88,
        "block_size": 22,
        "sequence": sequence,
    }
    template = {
        "schema_version": 1,
        "experiment_id": "EXP-011",
        "protocol_only": True,
        "submission_default": False,
        "authorization_required": "I AUTHORIZE ONE EXP-011 IBM QPU JOB",
        "prior_authorization_phrases_accepted": False,
        "backend": "ibm_fez",
        "required_layout": [20, 21, 23, 22],
        "required_physical_set": [20, 21, 22, 23],
        "transpiler_seed": 44,
        "shots_per_execution": SHOTS,
        "pub_executions": 88,
        "hardware_jobs": 1,
        "automatic_retries": 0,
        "target_qpu_seconds": 90,
        "preferred_qpu_seconds": [85, 95],
        "absolute_qpu_seconds_ceiling": 100,
        "parameterised_isa_qpy_sha256": None,
        "preflight_required": True,
        "authorization": False,
        "submitted": False,
        "job_id": None,
        "intent_created": False,
        "receipt_created": False,
        "grid_sha256": digest(grid),
        "ideal_landscape_sha256": digest(landscape),
        "execution_order_sha256": digest(order),
    }
    template["frozen_parameter_rows_sha256"] = digest(sequence)
    write_json(OUT / "grid-manifest.json", grid)
    write_json(OUT / "ideal-landscape.json", landscape)
    write_json(OUT / "execution-order.json", order)
    write_json(OUT / "hardware-workload-manifest.template.json", template)
    (OUT / "PLAN.md").write_text(
        "# EXP-011 dense hardware landscape replication\n\n"
        "EXP-011 is a predeclared 9×9 replication and resolution study of the governed "
        "four-qubit EXP-010D circuit. Exact classical evaluation remains authoritative. "
        "No quantum advantage, speedup, generalisation, or commercial superiority is claimed.\n\n"
        "The frozen workload contains 88 PUBs at 4,096 shots: 80 non-centre cells once, "
        "four centre executions, and four zero-angle controls. One IBM job and zero retries "
        "are permitted only after a passing merged preflight and the exact authorization "
        "phrase.\n\n"
        "Primary analysis uses average-rank Spearman correlation across 81 aggregated cells, "
        "100,000 one-sided permutations and a 10,000 paired-cell percentile bootstrap, all "
        "with seed 20260720. Thresholds are: strongly replicated rho >= 0.80 and p < 0.01; "
        "replicated rho >= 0.50 and p < 0.05; weak or inconclusive rho > 0 otherwise; not "
        "replicated rho <= 0. The declared repeatability, control, cross-run, subset, TV-distance "
        "and drift analyses are secondary and cannot replace the primary result.\n",
        encoding="utf-8",
    )
    return {
        "grid_sha256": digest(grid),
        "ideal_sha256": digest(landscape),
        "order_sha256": digest(order),
        "rows_sha256": digest(sequence),
        **landscape["summary"],
    }


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True))
