"""EXP-011 one-query read-only metadata preflight; contains no submission surface."""

from __future__ import annotations

import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any, cast

from qiskit import QuantumCircuit, qpy  # type: ignore[import-not-found]
from qiskit.circuit import Parameter  # type: ignore[import-not-found]
from qiskit.transpiler.preset_passmanagers import (  # type: ignore[import-not-found]
    generate_preset_pass_manager,
)

from quantum_folk_lab.compact_hardware_protocol import (
    ENERGY_RANGE,
    ISING_HASH,
    QUBO_HASH,
    H,
    J,
)
from quantum_folk_lab.exp010d_layout import decode_qiskit_key, validate_layout
from quantum_folk_lab.exp011_submission import canonical_workload_hash

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "experiments" / "EXP-011-dense-hardware-landscape"
OUT = ROOT / "experiments" / "EXP-011-dense-hardware-landscape-run"
BACKEND = "ibm_fez"
LAYOUT = [20, 21, 23, 22]
SEED = 44
SHOTS = 4096
PUB_COUNT = 88
USAGE_CEILING_S = 100.0


def parameterised_circuit() -> tuple[QuantumCircuit, Parameter, Parameter]:
    gamma, beta = Parameter("gamma"), Parameter("beta")
    circuit = QuantumCircuit(4, 4)
    circuit.h(range(4))
    for index, coefficient in enumerate(H):
        circuit.rz(2.0 * gamma * coefficient / ENERGY_RANGE, index)
    for (left, right), coefficient in J.items():
        circuit.rzz(2.0 * gamma * coefficient / ENERGY_RANGE, left, right)
    circuit.rx(2.0 * beta, range(4))
    circuit.measure(range(4), range(4))
    return circuit, gamma, beta


def load_and_validate_rows() -> list[dict[str, Any]]:
    record = json.loads((PLAN / "execution-order.json").read_text(encoding="utf-8"))
    rows = record["sequence"]
    if len(rows) != PUB_COUNT or [row["execution"] for row in rows] != list(range(1, 89)):
        raise RuntimeError("frozen execution sequence is incomplete or reordered")
    kinds = Counter(row["kind"] for row in rows)
    if kinds != {"landscape": 80, "centre": 4, "control": 4}:
        raise RuntimeError("frozen workload counts differ")
    landscape = [row["point_id"] for row in rows if row["kind"] == "landscape"]
    if len(set(landscape)) != 80:
        raise RuntimeError("non-centre grid rows are missing or duplicated")
    expected_anchors = {
        1: ("control", "centre"),
        2: ("centre", "control"),
        3: ("control", "centre"),
        4: ("centre", "control"),
    }
    for block, expected in expected_anchors.items():
        block_rows = [row for row in rows if row["block"] == block]
        if tuple(row["kind"] for row in block_rows[:2]) != expected or len(block_rows) != 22:
            raise RuntimeError("frozen block anchor positions differ")
    if any(row["shots"] != SHOTS for row in rows):
        raise RuntimeError("shot count differs")
    return cast(list[dict[str, Any]], rows)


def _qpy_bytes(circuit: QuantumCircuit) -> bytes:
    stream = io.BytesIO()
    qpy.dump(circuit, stream)
    return stream.getvalue()


def _two_qubit_metrics(
    circuit: QuantumCircuit, target: Any
) -> tuple[int, int, float, list[list[int]]]:
    index = {qubit: number for number, qubit in enumerate(circuit.qubits)}
    operations = [
        (item.operation.name, tuple(index[q] for q in item.qubits))
        for item in circuit.data
        if len(item.qubits) == 2
    ]
    layers: list[set[int]] = []
    errors: list[float] = []
    couplers: set[tuple[int, ...]] = set()
    for name, pair in operations:
        for occupied in layers:
            if not occupied.intersection(pair):
                occupied.update(pair)
                break
        else:
            layers.append(set(pair))
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


def run(service: Any) -> tuple[str, dict[str, Any]]:
    """Perform one named-backend metadata query and local work only."""
    rows = load_and_validate_rows()
    backend = service.backend(BACKEND, use_fractional_gates=False)
    status = backend.status()
    if str(backend.name) != BACKEND or not status.operational:
        return "NO-GO", {"reason": "frozen backend is unavailable"}
    circuit, gamma, beta = parameterised_circuit()
    manager = generate_preset_pass_manager(
        backend=backend, optimization_level=3, seed_transpiler=SEED, initial_layout=LAYOUT
    )
    isa = manager.run(circuit)
    initial = [int(value) for value in isa.layout.initial_index_layout(filter_ancillas=True)]
    mapped = [int(value) for value in isa.layout.final_index_layout(filter_ancillas=True)]
    routing = [int(value) for value in isa.layout.routing_permutation()]
    qubit_index = {qubit: index for index, qubit in enumerate(isa.qubits)}
    used = {qubit_index[q] for item in isa.data for q in item.qubits}
    try:
        validate_layout(initial, used)
    except RuntimeError as error:
        return "NO-GO", {"reason": str(error)}
    physical_to_classical = {
        qubit_index[item.qubits[0]]: isa.find_bit(item.clbits[0]).index
        for item in isa.data
        if item.operation.name == "measure"
    }
    for value in range(16):
        logical = f"{value:04b}"
        classical = ["0"] * 4
        for logical_index, physical in enumerate(mapped):
            classical[physical_to_classical[physical]] = logical[logical_index]
        displayed = "".join(reversed(classical))
        if decode_qiskit_key(displayed, mapped, physical_to_classical) != logical:
            return "NO-GO", {"reason": "all-state decoding verification failed"}
    two_count, two_depth, two_error, couplers = _two_qubit_metrics(isa, backend.target)
    readout = []
    for qubit in LAYOUT:
        properties = backend.target["measure"].get((qubit,))
        if properties is None or properties.error is None:
            return "NO-GO", {"reason": "mapped readout properties unavailable"}
        readout.append(float(properties.error))
    duration_s = float(isa.estimate_duration(backend.target, unit="s"))
    duration_us = duration_s * 1e6
    # Governed conservative estimator: circuit time plus one second per PUB.
    conservative_usage_s = duration_s * SHOTS * PUB_COUNT + PUB_COUNT
    operation_counts = {str(key): int(value) for key, value in isa.count_ops().items()}
    gates_pass = bool(
        two_count <= 24
        and two_depth <= 18
        and isa.depth() <= 120
        and duration_us <= 150
        and two_error <= 0.02
        and sum(readout) / len(readout) <= 0.05
        and conservative_usage_s <= USAGE_CEILING_S
    )
    qpy_bytes = _qpy_bytes(isa)
    bindings = [
        {
            "execution": row["execution"],
            "point_id": row["point_id"],
            "kind": row["kind"],
            "parameters": {str(gamma): row["gamma"], str(beta): row["beta"]},
            "shots": row["shots"],
        }
        for row in rows
    ]
    if len(bindings) != PUB_COUNT or any(row["shots"] != SHOTS for row in bindings):
        raise RuntimeError("in-memory PUB validation failed")
    metrics: dict[str, Any] = {
        "backend": BACKEND,
        "operational": bool(status.operational),
        "accepting_jobs": bool(status.status_msg != "internal"),
        "queue_depth": int(status.pending_jobs),
        "layout": mapped,
        "initial_layout": initial,
        "routing_permutation_on_physical_set": {str(q): routing[q] for q in sorted(used)},
        "physical_qubit_set": sorted(used),
        "physical_to_classical": {
            str(key): value for key, value in sorted(physical_to_classical.items())
        },
        "all_basis_states_decoded": 16,
        "seed": SEED,
        "total_operation_count": int(sum(operation_counts.values())),
        "operation_counts": operation_counts,
        "total_depth": int(isa.depth()),
        "two_qubit_count": two_count,
        "two_qubit_depth": two_depth,
        "duration_us": duration_us,
        "mean_two_qubit_error": two_error,
        "mean_readout_error": sum(readout) / len(readout),
        "touched_couplers": couplers,
        "swap_count": operation_counts.get("swap", 0),
        "direction_corrections_or_routing": operation_counts.get("swap", 0),
        "parameterised_isa_qpy_sha256": hashlib.sha256(qpy_bytes).hexdigest(),
        "pub_count": len(bindings),
        "shots_per_pub": SHOTS,
        "conservative_usage_seconds": conservative_usage_s,
        "usage_ceiling_seconds": USAGE_CEILING_S,
        "passes": gates_pass,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "parameterised-isa.qpy").write_bytes(qpy_bytes)
    (OUT / "sanitized-preflight.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    workload_hash = canonical_workload_hash(
        experiment_id="EXP-011",
        backend=BACKEND,
        initial_layout=initial,
        physical_qubit_set=sorted(used),
        routing_permutation={str(q): routing[q] for q in sorted(used)},
        final_layout=mapped,
        physical_to_classical={str(key): value for key, value in physical_to_classical.items()},
        isa_qpy_sha256=str(metrics["parameterised_isa_qpy_sha256"]),
        rows=rows,
        transpiler_seed=SEED,
    )
    manifest = {
        "experiment_id": "EXP-011",
        "authorization": False,
        "submitted": False,
        "job_id": None,
        "intent_created": False,
        "receipt_created": False,
        "backend": BACKEND,
        "layout": LAYOUT,
        "transpiler_seed": SEED,
        "qubo_sha256": QUBO_HASH,
        "ising_sha256": ISING_HASH,
        "parameterised_isa_qpy_sha256": metrics["parameterised_isa_qpy_sha256"],
        "pub_count": PUB_COUNT,
        "shots_per_pub": SHOTS,
        "hardware_jobs_if_authorized": 1,
        "automatic_retries": 0,
        "bindings_sha256": hashlib.sha256(
            (json.dumps(bindings, sort_keys=True) + "\n").encode()
        ).hexdigest(),
        "canonical_workload_sha256": workload_hash,
    }
    (OUT / "sanitized-workload-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return ("GO" if gates_pass else "NO-GO"), metrics
