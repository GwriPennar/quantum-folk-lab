"""Frozen, offline EXP-010B circuit contract and fail-closed submission guard."""

from __future__ import annotations

import json
import os
import stat
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

GAMMA = 3.3177975191929154
BETA = 2.476505299986026
ENERGY_RANGE = 0.031425180740004
QUBO_HASH = "96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e"
ISING_HASH = "635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5"
AUTHORIZATION = "I AUTHORIZE ONE IBM QPU JOB"
EXPERIMENT_ID = "EXP-010B"
EXP010A_SQUASH = "461375818af7f512557003e1348054b5539a150d"
AMBIGUOUS_OUTCOME = (
    "submission outcome may be ambiguous; automatic retry forbidden; "
    "reconcile the durable intent against IBM job history"
)
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
    from qiskit import QuantumCircuit  # type: ignore

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


@dataclass(frozen=True)
class SubmissionMetadata:
    exp010b_commit: str
    backend: str
    backend_snapshot: str | None
    layout: tuple[int, ...]
    qaoa_circuit_hash: str
    control_circuit_hash: str
    shots_per_pub: int
    pub_count: int


def validate_submission(
    submit: bool, phrase: str, readiness: Readiness, intent: Path, receipt: Path
) -> None:
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
    if intent.exists():
        raise RuntimeError(AMBIGUOUS_OUTCOME)


def _durable_exclusive_json(path: Path, record: Mapping[str, Any]) -> None:
    """Create one restrictive JSON record durably, without ever overwriting it."""
    payload = (json.dumps(record, sort_keys=True) + "\n").encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, payload)
        os.fsync(descriptor)
        fchmod = getattr(os, "fchmod", None)
        if fchmod is not None:
            try:
                fchmod(descriptor, stat.S_IRUSR | stat.S_IWUSR)
            except OSError:
                pass
    finally:
        os.close(descriptor)
    try:
        directory = os.open(path.parent, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(directory)
    except OSError:
        pass
    finally:
        os.close(directory)


def submit_one_job(
    *,
    submit: bool,
    phrase: str,
    readiness: Readiness,
    metadata: SubmissionMetadata,
    intent: Path,
    receipt: Path,
    credential_reader: Callable[[], Any],
    runtime_factory: Callable[[Any], Any],
    submitter: Callable[[Any], str],
) -> str:
    """Guard one injected submission; production IBM wiring is intentionally absent."""
    validate_submission(submit, phrase, readiness, intent, receipt)
    attempt_id = str(uuid.uuid4())
    created_at = datetime.now(UTC).isoformat()
    intent_record = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "attempt_id": attempt_id,
        "created_at_utc": created_at,
        "exp010a_squash": EXP010A_SQUASH,
        "exp010b_commit": metadata.exp010b_commit,
        "qubo_hash": readiness.qubo_hash,
        "ising_hash": readiness.ising_hash,
        "gamma": readiness.gamma,
        "beta": readiness.beta,
        "backend": metadata.backend,
        "backend_snapshot": metadata.backend_snapshot,
        "layout": metadata.layout,
        "qaoa_circuit_hash": metadata.qaoa_circuit_hash,
        "control_circuit_hash": metadata.control_circuit_hash,
        "shots_per_pub": metadata.shots_per_pub,
        "pub_count": metadata.pub_count,
        "retry": False,
        "state": "submission_intent_created",
    }
    try:
        _durable_exclusive_json(intent, intent_record)
    except FileExistsError:
        raise RuntimeError(AMBIGUOUS_OUTCOME) from None
    try:
        credential = credential_reader()
        runtime = runtime_factory(credential)
        job_id = submitter(runtime)
    except Exception:
        raise RuntimeError(AMBIGUOUS_OUTCOME) from None
    receipt_record = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "attempt_id": attempt_id,
        "job_id": job_id,
        "backend": metadata.backend,
        "qaoa_circuit_hash": metadata.qaoa_circuit_hash,
        "control_circuit_hash": metadata.control_circuit_hash,
        "shots_per_pub": metadata.shots_per_pub,
        "pub_count": metadata.pub_count,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "retry": False,
        "state": "job_receipt_created",
    }
    try:
        _durable_exclusive_json(receipt, receipt_record)
    except Exception:
        raise RuntimeError(AMBIGUOUS_OUTCOME) from None
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
