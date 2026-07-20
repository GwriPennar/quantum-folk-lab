"""Build deterministic, offline-only EXP-010D planning evidence."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "EXP-010D-hardware-parameter-landscape"
EXACT = ROOT / "experiments" / "EXP-010A-compact-family-encoding" / "compact-exact-result.json"
QUBO_HASH = "96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e"
ISING_HASH = "635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5"
GAMMA0 = 3.3177975191929154
BETA0 = 2.476505299986026
GAMMAS = [
    "2.517797519192915",
    "2.9177975191929155",
    "3.3177975191929154",
    "3.7177975191929153",
    "4.117797519192916",
]
BETAS = [
    "2.0765052999860263",
    "2.276505299986026",
    "2.476505299986026",
    "2.6765052999860264",
    "2.876505299986026",
]
SEED = 20260720
SHOTS = 4096


def _json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _mixer(beta: float) -> np.ndarray:
    single = np.array(
        [[math.cos(beta), -1j * math.sin(beta)], [-1j * math.sin(beta), math.cos(beta)]],
        dtype=complex,
    )
    result = np.array([[1.0 + 0.0j]])
    for _ in range(4):
        result = np.kron(result, single)
    return result


def _distribution(gamma: float, beta: float, normalized: np.ndarray) -> np.ndarray:
    phased = np.exp(-1j * gamma * normalized) / 4
    return np.abs(_mixer(beta) @ phased) ** 2


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
    for i, gamma_text in zip(range(-2, 3), GAMMAS, strict=True):
        for j, beta_text in zip(range(-2, 3), BETAS, strict=True):
            probabilities = _distribution(float(gamma_text), float(beta_text), normalized)
            expected = float(probabilities @ energies)
            most_likely_index = min(
                range(16), key=lambda index: (-float(probabilities[index]), states[index])
            )
            cells.append(
                {
                    "point_id": f"g{i:+d}_b{j:+d}",
                    "i": i,
                    "j": j,
                    "gamma": gamma_text,
                    "beta": beta_text,
                    "ideal_distribution": {
                        state: float(probabilities[index]) for index, state in enumerate(states)
                    },
                    "expected_energy": expected,
                    "r": (e_uniform - expected) / (e_uniform - e_min),
                    "p_1010": float(probabilities[states.index("1010")]),
                    "most_likely_state": states[most_likely_index],
                    "ring": "centre"
                    if i == 0 and j == 0
                    else ("outer" if max(abs(i), abs(j)) == 2 else "inner"),
                }
            )
    centre = next(cell for cell in cells if cell["i"] == 0 and cell["j"] == 0)
    outer = [float(cell["r"]) for cell in cells if cell["ring"] == "outer"]
    envelope = {
        "best_ideal_r": max(float(cell["r"]) for cell in cells),
        "lowest_grid_r": min(float(cell["r"]) for cell in cells),
        "centre_r": centre["r"],
        "centre_is_best": centre["r"] == max(float(cell["r"]) for cell in cells),
        "outer_ring_median_r": float(np.median(outer)),
        "centre_to_outer_ring_median_gap": float(centre["r"] - np.median(outer)),
    }
    grid: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": "EXP-010D",
        "gamma_formula": "gamma0 + i * 0.4",
        "beta_formula": "beta0 + j * 0.2",
        "gamma0": str(GAMMA0),
        "beta0": str(BETA0),
        "gamma_values": GAMMAS,
        "beta_values": BETAS,
        "point_count": 25,
        "points": [
            {key: cell[key] for key in ("point_id", "i", "j", "gamma", "beta", "ring")}
            for cell in cells
        ],
    }
    non_centre = [point for point in grid["points"] if point["point_id"] != "g+0_b+0"]
    random.Random(SEED).shuffle(non_centre)
    sequence: list[dict[str, Any]] = []
    for block in range(1, 5):
        anchors = ["control", "centre"] if block % 2 else ["centre", "control"]
        for kind in anchors:
            sequence.append(
                {
                    "execution": len(sequence) + 1,
                    "block": block,
                    "kind": kind,
                    "point_id": "uniform_control" if kind == "control" else "g+0_b+0",
                    "gamma": "0" if kind == "control" else str(GAMMA0),
                    "beta": "0" if kind == "control" else str(BETA0),
                    "shots": SHOTS,
                }
            )
        for point in non_centre[(block - 1) * 6 : block * 6]:
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
    _json(OUT / "grid-manifest.json", grid)
    _json(
        OUT / "ideal-landscape.json",
        {
            "schema_version": 1,
            "experiment_id": "EXP-010D",
            "qubo_sha256": QUBO_HASH,
            "ising_sha256": ISING_HASH,
            "state_order": states,
            "energy_uniform16": e_uniform,
            "energy_minimum": e_min,
            "cells": cells,
            "envelope": envelope,
        },
    )
    _json(
        OUT / "execution-order.json",
        {
            "schema_version": 1,
            "seed": SEED,
            "shuffle_algorithm": "Python random.Random(seed).shuffle",
            "total_executions": 32,
            "sequence": sequence,
        },
    )
    _json(
        OUT / "hardware-workload-manifest.template.json",
        {
            "schema_version": 1,
            "experiment_id": "EXP-010D",
            "protocol_only": True,
            "submission_default": False,
            "authorization_required": "I AUTHORIZE ONE EXP-010D IBM QPU JOB",
            "exp010c_authorization_accepted": False,
            "backend": "ibm_fez",
            "required_layout": [20, 21, 23, 22],
            "transpiler_seed": 44,
            "shots_per_execution": SHOTS,
            "pub_executions": 32,
            "hardware_jobs": 1,
            "automatic_retries": 0,
            "billable_qpu_seconds_ceiling": 180,
            "parameterised_isa_qpy_sha256": None,
            "preflight_required": True,
            "authorization": False,
            "submitted": False,
            "job_id": None,
            "intent_created": False,
            "receipt_created": False,
        },
    )
    _json(
        OUT / "layout-contract.json",
        {
            "schema_version": 1,
            "experiment_id": "EXP-010D-R1",
            "required_initial_layout": [20, 21, 23, 22],
            "required_physical_set": [20, 21, 22, 23],
            "final_routing_permutation_may_be_non_identity": True,
            "required_layout_records": [
                "initial_index_layout",
                "routing_permutation",
                "final_index_layout",
                "physical_to_classical",
            ],
            "qiskit_display_order": "c3c2c1c0",
            "repository_logical_order": "q0q1q2q3",
            "all_basis_states_required": 16,
            "post_hoc_reinterpretation_allowed": False,
        },
    )
    (OUT / "IDEAL-LANDSCAPE-REPORT.md").write_text(
        "# EXP-010D ideal parameter landscape\n\n"
        "This deterministic statevector calculation covers all 25 frozen grid points. "
        "IBM was not contacted.\n\n"
        f"- Best ideal R: `{envelope['best_ideal_r']:.15f}`\n"
        f"- Lowest grid R: `{envelope['lowest_grid_r']:.15f}`\n"
        f"- Centre R: `{envelope['centre_r']:.15f}`\n"
        f"- Centre is best: `{str(envelope['centre_is_best']).lower()}`\n"
        "- Centre-to-outer-ring median R gap: "
        f"`{envelope['centre_to_outer_ring_median_gap']:.15f}`\n\n"
        "The centre reproduces the frozen ideal four-qubit result. Exact classical energy "
        "evaluation remains authoritative; no quantum advantage or speedup is claimed.\n",
        encoding="utf-8",
    )
    return envelope


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True))
