"""One bounded, read-only IBM metadata query followed by local transpilation only."""

from __future__ import annotations

import hashlib
import io
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import qiskit  # type: ignore
from qiskit import QuantumCircuit, qpy
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager  # type: ignore
from qiskit_ibm_runtime import QiskitRuntimeService  # type: ignore

from quantum_folk_lab.compact_hardware_protocol import (  # type: ignore
    BETA,
    EXP010A_SQUASH,
    GAMMA,
    ISING_HASH,
    QUBO_HASH,
    build_circuit,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "EXP-010C-read-only-ibm-preflight"
EXP010B_SQUASH = "42f9eb8f60946a795d7e632343b18c53802a9039"
SEEDS = range(42, 50)
SHOTS = 4096


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _qpy_bytes(circuit: QuantumCircuit) -> bytes:
    stream = io.BytesIO()
    qpy.dump(circuit, stream)
    return stream.getvalue()


def _uniform_control() -> QuantumCircuit:
    circuit = QuantumCircuit(4, 4)
    circuit.h(range(4))
    circuit.measure(range(4), range(4))
    return circuit


def _two_qubit_metrics(
    circuit: QuantumCircuit, target: Any
) -> tuple[int, int, float, list[list[int]]]:
    operations: list[tuple[str, tuple[int, ...]]] = []
    qubit_index = {qubit: index for index, qubit in enumerate(circuit.qubits)}
    for instruction in circuit.data:
        physical = tuple(qubit_index[q] for q in instruction.qubits)
        if len(physical) == 2:
            operations.append((instruction.operation.name, physical))
    layers: list[set[int]] = []
    for _, pair in operations:
        for occupied in layers:
            if not occupied.intersection(pair):
                occupied.update(pair)
                break
        else:
            layers.append(set(pair))
    errors: list[float] = []
    couplers: set[tuple[int, ...]] = set()
    for name, pair in operations:
        properties = target[name].get(pair)
        if properties is None or properties.error is None:
            raise RuntimeError("missing mapped two-qubit properties")
        errors.append(float(properties.error))
        couplers.add(tuple(sorted(pair)))
    if not errors:
        raise RuntimeError("no mapped two-qubit operations")
    return (
        len(operations),
        len(layers),
        sum(errors) / len(errors),
        [list(x) for x in sorted(couplers)],
    )


def _candidate(
    backend: Any, seed: int, qaoa: QuantumCircuit, control: QuantumCircuit
) -> tuple[dict[str, Any], QuantumCircuit, QuantumCircuit]:
    manager = generate_preset_pass_manager(
        backend=backend, optimization_level=3, seed_transpiler=seed
    )
    qaoa_isa = manager.run(qaoa)
    layout = tuple(int(x) for x in qaoa_isa.layout.final_index_layout()[:4])
    control_manager = generate_preset_pass_manager(
        backend=backend, optimization_level=3, seed_transpiler=seed, initial_layout=list(layout)
    )
    control_isa = control_manager.run(control)
    count, two_depth, two_error, couplers = _two_qubit_metrics(qaoa_isa, backend.target)
    touched = sorted({q for pair in couplers for q in pair} | set(layout))
    readout: list[float] = []
    for qubit in touched:
        properties = backend.target["measure"].get((qubit,))
        if properties is None or properties.error is None:
            raise RuntimeError("missing mapped readout properties")
        readout.append(float(properties.error))
    duration_s = float(qaoa_isa.estimate_duration(backend.target, unit="s"))
    queue = int(backend.status().pending_jobs)
    metrics: dict[str, Any] = {
        "backend": str(backend.name),
        "layout": list(layout),
        "seed": seed,
        "queue_depth": queue,
        "two_qubit_count": count,
        "two_qubit_depth": two_depth,
        "total_depth": int(qaoa_isa.depth()),
        "duration_us": duration_s * 1e6,
        "mean_two_qubit_error": two_error,
        "mean_readout_error": sum(readout) / len(readout),
        "touched_qubits": touched,
        "touched_couplers": couplers,
    }
    metrics["passes"] = bool(
        count <= 24
        and two_depth <= 18
        and metrics["total_depth"] <= 120
        and metrics["duration_us"] <= 150
        and two_error <= 0.02
        and metrics["mean_readout_error"] <= 0.05
    )
    return metrics, qaoa_isa, control_isa


def main() -> int:
    timestamp = datetime.now(UTC).isoformat()
    service = QiskitRuntimeService()
    backends = service.backends(
        simulator=False, operational=True, min_num_qubits=4, use_fractional_gates=False
    )
    qaoa = build_circuit(measured=True)
    control = _uniform_control()
    snapshots: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    circuits: dict[tuple[str, int, tuple[int, ...]], tuple[QuantumCircuit, QuantumCircuit]] = {}
    for backend in sorted(backends, key=lambda item: str(item.name)):
        snapshots.append(
            {
                "backend": str(backend.name),
                "qubits": int(backend.num_qubits),
                "operational": bool(backend.status().operational),
                "queue_depth": int(backend.status().pending_jobs),
                "snapshot_utc": timestamp,
            }
        )
        for seed in SEEDS:
            try:
                metrics, qaoa_isa, control_isa = _candidate(backend, seed, qaoa, control)
                candidates.append(metrics)
                circuits[(metrics["backend"], seed, tuple(metrics["layout"]))] = (
                    qaoa_isa,
                    control_isa,
                )
            except Exception as error:
                candidates.append(
                    {
                        "backend": str(backend.name),
                        "seed": seed,
                        "passes": False,
                        "reason": type(error).__name__,
                    }
                )
    _json(OUT / "backend-snapshot.json", {"query_utc": timestamp, "backends": snapshots})
    _json(OUT / "transpilation-candidates.json", candidates)
    passing = [row for row in candidates if row.get("passes")]
    if not passing:
        (OUT / "PREFLIGHT-REPORT.md").write_text(
            "# EXP-010C preflight\n\n"
            "No candidate passed every frozen gate. No workload was submitted.\n",
            encoding="utf-8",
        )
        return 2
    keys = (
        "two_qubit_count",
        "two_qubit_depth",
        "total_depth",
        "duration_us",
        "mean_two_qubit_error",
        "mean_readout_error",
        "backend",
        "layout",
        "seed",
    )
    selected = min(passing, key=lambda row: tuple(row[key] for key in keys))
    qaoa_isa, control_isa = circuits[
        (selected["backend"], selected["seed"], tuple(selected["layout"]))
    ]
    qaoa_bytes, control_bytes = _qpy_bytes(qaoa_isa), _qpy_bytes(control_isa)
    (OUT / "qaoa.qpy").write_bytes(qaoa_bytes)
    (OUT / "control.qpy").write_bytes(control_bytes)
    selected["qaoa_circuit_sha256"] = _sha(qaoa_bytes)
    selected["control_circuit_sha256"] = _sha(control_bytes)
    _json(OUT / "selected-candidate.json", selected)
    manifest = {
        "schema_version": 1,
        "experiment_id": "EXP-010C",
        "exp010a_squash": EXP010A_SQUASH,
        "exp010b_squash": EXP010B_SQUASH,
        "qubo_hash": QUBO_HASH,
        "ising_hash": ISING_HASH,
        "gamma": GAMMA,
        "beta": BETA,
        "backend": selected["backend"],
        "layout": selected["layout"],
        "transpiler_seed": selected["seed"],
        "qaoa_circuit_sha256": selected["qaoa_circuit_sha256"],
        "control_circuit_sha256": selected["control_circuit_sha256"],
        "pub_order": ["qaoa", "uniform_control"],
        "authorization": False,
        "submitted": False,
        "job_id": None,
        "intent_created": False,
        "receipt_created": False,
        "shots_per_pub": SHOTS,
        "pub_count": 2,
        "python": sys.version.split()[0],
        "qiskit": qiskit.__version__,
        "platform": platform.system(),
    }
    _json(OUT / "submission-manifest.json", manifest)
    (OUT / "PREFLIGHT-REPORT.md").write_text(
        "# EXP-010C read-only IBM preflight\n\n"
        f"Selected `{selected['backend']}` layout `{selected['layout']}` "
        f"with seed `{selected['seed']}`. "
        "Authentication and one filtered backend query were read-only. "
        "No primitive, session, batch, intent, receipt, or job was created.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
