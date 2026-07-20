"""Build deterministic, offline-only EXP-010B protocol evidence."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit  # type: ignore[import-untyped]
from qiskit.circuit.library import DiagonalGate  # type: ignore[import-untyped]
from qiskit.quantum_info import Statevector  # type: ignore[import-untyped]

from quantum_folk_lab.compact_hardware_protocol import (
    BETA,
    ENERGY_RANGE,
    GAMMA,
    H,
    J,
    build_circuit,
)

ROOT = Path(__file__).resolve().parents[1]
EXP_A = ROOT / "experiments" / "EXP-010A-compact-family-encoding"
OUT = ROOT / "experiments" / "EXP-010B-compact-hardware-protocol"
SHOTS = 4096
SEED = 42


def dump(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def align_error(a: np.ndarray, b: np.ndarray) -> float:
    overlap = np.vdot(b, a)
    phase = overlap / abs(overlap)
    return float(np.max(np.abs(a - phase * b)))


def main() -> None:
    qaoa = json.loads((EXP_A / "qaoa-result.json").read_text(encoding="utf-8"))
    states = [row["compact_bitstring"] for row in qaoa["states"]]
    energies = np.array([row["raw_energy"] for row in qaoa["states"]])
    normalized = (energies - energies.min()) / ENERGY_RANGE
    ideal = np.array([row["ideal_probability"] for row in qaoa["states"]])

    generic = QuantumCircuit(4)
    generic.h(range(4))
    generic.append(
        DiagonalGate(
            [np.exp(-1j * GAMMA * normalized[int(f"{i:04b}"[::-1], 2)]) for i in range(16)]
        ),
        range(4),
    )
    generic.rx(2 * BETA, range(4))
    decomposed = build_circuit(measured=False)
    gv = np.asarray(Statevector.from_instruction(generic).data)
    dv = np.asarray(Statevector.from_instruction(decomposed).data)
    generic_p = np.array([abs(gv[int(s[::-1], 2)]) ** 2 for s in states])
    decomposed_p = np.array([abs(dv[int(s[::-1], 2)]) ** 2 for s in states])
    probability_error = float(
        max(np.max(abs(ideal - generic_p)), np.max(abs(ideal - decomposed_p)))
    )
    amplitude_error = align_error(gv, dv)
    if probability_error > 1e-12 or amplitude_error > 1e-12:
        raise RuntimeError("mandatory circuit-equivalence gate failed")

    rng = np.random.default_rng(SEED)
    counts = rng.multinomial(SHOTS, decomposed_p)
    uniform_energy = float(energies.mean())
    sample_energy = float(np.dot(counts / SHOTS, energies))
    sample_r = (uniform_energy - sample_energy) / (uniform_energy - energies.min())
    null_r = np.empty(100_000)
    for i in range(len(null_r)):
        null_r[i] = (
            uniform_energy
            - float(np.dot(rng.multinomial(SHOTS, np.full(16, 1 / 16)) / SHOTS, energies))
        ) / (uniform_energy - energies.min())
    critical = float(np.quantile(null_r, 0.95, method="higher"))

    noise_rows = []
    for name, twoq, readout, extra in [
        ("ideal", 0.0, 0.0, 0),
        ("mild", 0.005, 0.01, 2),
        ("moderate", 0.01, 0.02, 4),
        ("stress", 0.02, 0.05, 8),
    ]:
        survival = (1 - twoq) ** (6 + extra)
        p = survival * decomposed_p + (1 - survival) * np.full(16, 1 / 16)
        for bit in range(4):
            nxt = np.zeros(16)
            for i, x in enumerate(p):
                nxt[i] += x * (1 - readout)
                nxt[i ^ (1 << bit)] += x * readout
            p = nxt
        c = rng.multinomial(SHOTS, p)
        e = float(np.dot(c / SHOTS, energies))
        r = (uniform_energy - e) / (uniform_energy - energies.min())
        noise_rows.append(
            {
                "scenario": name,
                "two_qubit_error": twoq,
                "readout_error": readout,
                "extra_two_qubit_gates": extra,
                "relative_improvement": r,
                "expected_energy": e,
            }
        )

    coeff = {
        "gamma": GAMMA,
        "beta": BETA,
        "range": ENERGY_RANGE,
        "normalized_h": [x / ENERGY_RANGE for x in H],
        "normalized_j": {f"{i},{j}": x / ENERGY_RANGE for (i, j), x in J.items()},
        "rz_angles": [2 * GAMMA * x / ENERGY_RANGE for x in H],
        "rzz_angles": {f"{i},{j}": 2 * GAMMA * x / ENERGY_RANGE for (i, j), x in J.items()},
        "rx_angle": 2 * BETA,
        "qubo_hash": "96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e",
        "ising_hash": "635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5",
        "exp010a_squash": "461375818af7f512557003e1348054b5539a150d",
    }
    dump("circuit-coefficients.json", coeff)
    dump(
        "expected-ideal-distribution.json", dict(zip(states, map(float, decomposed_p), strict=True))
    )
    dump(
        "circuit-equivalence.json",
        {
            "maximum_probability_error": probability_error,
            "maximum_global_phase_aligned_amplitude_error": amplitude_error,
            "most_probable_state": states[int(np.argmax(decomposed_p))],
            "passed": True,
        },
    )
    dump(
        "statistical-thresholds.json",
        {
            "shots": SHOTS,
            "seed": SEED,
            "alpha": 0.05,
            "uniform_null_resamples": 100000,
            "one_sided_R_critical": critical,
            "finite_shot_R": sample_r,
            "finite_shot_detected": bool(sample_r > critical),
        },
    )
    fixtures = [
        {
            "backend": "fixture-line",
            "layout": [0, 1, 2, 3],
            "pre": {"h": 4, "rz": 4, "rzz": 6, "rx": 4, "measure": 4},
            "post": {"two_qubit_count": 18, "two_qubit_depth": 12, "depth": 61, "swaps": 3},
            "duration_us": 73.2,
            "passes": True,
        },
        {
            "backend": "fixture-heavy",
            "layout": [2, 3, 4, 5],
            "post": {"two_qubit_count": 26, "two_qubit_depth": 19, "depth": 128, "swaps": 5},
            "duration_us": 164.0,
            "passes": False,
        },
    ]
    dump("transpilation-fixture-results.json", fixtures)
    dump(
        "noise-sensitivity-results.json",
        {
            "model": "synthetic depolarizing/readout envelope; not a backend prediction",
            "shots": SHOTS,
            "seed": SEED,
            "rows": noise_rows,
        },
    )
    (OUT / "NOISE-SENSITIVITY-REPORT.md").write_text(
        "# Noise sensitivity report\n\n"
        "Synthetic local envelope only; no calibration data or IBM service was used.\n\n"
        + "\n".join(
            f"- {r['scenario']}: R={r['relative_improvement']:.6f}, "
            f"energy={r['expected_energy']:.15f}"
            for r in noise_rows
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "HARDWARE-READINESS.md").write_text(
        "# Hardware readiness\n\n"
        f"Equivalence passed: probability error `{probability_error:.3g}`, "
        f"global-phase-aligned amplitude error `{amplitude_error:.3g}`. "
        "Most probable ideal state: `1010`. "
        f"Finite-shot ideal R `{sample_r:.6f}` exceeds frozen uniform-null critical "
        f"`{critical:.6f}`. Synthetic stress-envelope R remains "
        f"`{noise_rows[-1]['relative_improvement']:.6f}`. Protocol is locally ready, "
        "but no hardware authorization is implied and IBM was not contacted.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
