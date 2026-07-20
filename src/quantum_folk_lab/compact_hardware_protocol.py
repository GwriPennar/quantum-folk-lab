"""Frozen, offline EXP-010B circuit contract and fail-closed submission guard."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GAMMA = 3.3177975191929154
BETA = 2.476505299986026
ENERGY_RANGE = 0.031425180740004
QUBO_HASH = "96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e"
ISING_HASH = "635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5"
AUTHORIZATION = "I AUTHORIZE ONE IBM QPU JOB"
H = (0.00801636532609275, -0.0032326639995157516, 0.001000256952986247, -3.0310519998752797e-05)
J = {
    (0, 1): 0.0002744091897435002,
    (0, 2): -0.0012127821489684998,
    (0, 3): -0.000308898952806249,
    (1, 2): 0.0012438312019450014,
    (1, 3): -0.0023158466462862466,
    (2, 3): 0.000934910694694752,
}


def displayed_bitstring(qiskit_key: str) -> str:
    """Convert Qiskit's c3..c0 display to frozen q0..q3 display order."""
    bits = qiskit_key.replace(" ", "")
    if len(bits) != 4 or set(bits) - {"0", "1"}:
        raise ValueError("expected exactly four measured bits")
    return bits[::-1]


def build_circuit(*, measured: bool = True) -> Any:
    """Build the explicit H/RZ/RZZ/RX frozen logical circuit."""
    from qiskit import QuantumCircuit  # type: ignore[import-not-found,import-untyped]

    circuit = QuantumCircuit(4, 4 if measured else 0)
    circuit.h(range(4))
    for i, coefficient in enumerate(H):
        circuit.rz(2.0 * GAMMA * coefficient / ENERGY_RANGE, i)
    for (i, j), coefficient in J.items():
        circuit.rzz(2.0 * GAMMA * coefficient / ENERGY_RANGE, i, j)
    circuit.rx(2.0 * BETA, range(4))
    if measured:
        circuit.measure(range(4), range(4))
    return circuit


@dataclass(frozen=True)
class Readiness:
    qubo_hash: str
    ising_hash: str
    gamma: float
    beta: float
    equivalence_passed: bool
    backend_gates_passed: bool


def validate_submission(submit: bool, phrase: str, readiness: Readiness, receipt: Path) -> None:
    """Perform every fail-closed check before any external dependency is called."""
    if not submit or phrase != AUTHORIZATION:
        raise PermissionError("explicit one-job authorization is required")
    if readiness.qubo_hash != QUBO_HASH or readiness.ising_hash != ISING_HASH:
        raise RuntimeError("evidence hash mismatch")
    if readiness.gamma != GAMMA or readiness.beta != BETA:
        raise RuntimeError("frozen angle mismatch")
    if not readiness.equivalence_passed or not readiness.backend_gates_passed:
        raise RuntimeError("readiness gate failed")
    if receipt.exists():
        raise RuntimeError("job receipt already exists; retry forbidden")


def submit_one_job(
    *,
    submit: bool,
    phrase: str,
    readiness: Readiness,
    intent: Path,
    receipt: Path,
    credential_reader: Callable[[], Any],
    runtime_factory: Callable[[Any], Any],
    submitter: Callable[[Any], str],
) -> str:
    """Guard one injected submission; production IBM wiring is intentionally absent."""
    validate_submission(submit, phrase, readiness, receipt)
    intent.write_text(json.dumps({"state": "authorized", "retry": False}) + "\n", encoding="utf-8")
    try:
        credential = credential_reader()
        runtime = runtime_factory(credential)
        job_id = submitter(runtime)
    except Exception as exc:
        raise RuntimeError("hardware submission failed; automatic retry forbidden") from exc
    receipt.write_text(json.dumps({"job_id": job_id, "retry": False}) + "\n", encoding="utf-8")
    return job_id


def select_layout(records: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Apply the frozen snapshot-only gates and deterministic ranking."""
    eligible = [
        r
        for r in records
        if r["operational"]
        and not r["simulator"]
        and r["qubits"] >= 4
        and r["transpiled"]
        and r["two_qubit_count"] <= 24
        and r["two_qubit_depth"] <= 18
        and r["depth"] <= 120
        and r["duration_us"] <= 150
        and r["two_qubit_error"] <= 0.02
        and r["readout_error"] <= 0.05
        and not r["unavailable"]
    ]
    if not eligible:
        raise RuntimeError("no fixture candidate passes frozen backend gates")
    keys = (
        "two_qubit_count",
        "two_qubit_depth",
        "depth",
        "duration_us",
        "two_qubit_error",
        "readout_error",
        "usage",
        "backend",
        "layout",
    )
    return min(eligible, key=lambda r: tuple(r[k] for k in keys))
