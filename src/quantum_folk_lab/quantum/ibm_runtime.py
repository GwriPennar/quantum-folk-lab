from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

HARDWARE_CONFIRMATION = "I AUTHORIZE ONE IBM QPU JOB"


def require_confirmation(*, submit_hardware: bool, confirmation: str) -> None:
    if not submit_hardware:
        raise PermissionError("IBM QPU execution requires --submit-hardware.")
    if confirmation != HARDWARE_CONFIRMATION:
        raise PermissionError("IBM QPU execution requires the exact confirmation phrase.")


def import_runtime() -> object:
    try:
        import qiskit_ibm_runtime  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install the optional ibm extra to use IBM Runtime.") from exc
    return qiskit_ibm_runtime


def load_api_token(credential_file: Path) -> str:
    """Read one supported token field without exposing credential contents."""
    try:
        with credential_file.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("IBM credential file could not be read safely.") from exc
    if not isinstance(payload, dict):
        raise ValueError("IBM credential JSON must be an object.")
    supported_fields = ("api" + "key", "api" + "_key", "token")
    present = [key for key in supported_fields if key in payload]
    if len(present) != 1:
        raise ValueError("IBM credential JSON must contain exactly one supported token field.")
    token = payload[present[0]]
    if not isinstance(token, str) or not token.strip():
        raise ValueError("IBM credential token must be a non-empty string.")
    return token.strip()


def build_hello_folk_circuit() -> Any:
    """Build a measured Bell pair, thematically labelled call-and-response."""
    try:
        from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install the optional quantum extra to build the circuit.") from exc
    qubits = QuantumRegister(2, "call_response")
    measurements = ClassicalRegister(2, "measure")
    circuit = QuantumCircuit(qubits, measurements, name="hello_folk_music_world")
    circuit.h(qubits[0])
    circuit.cx(qubits[0], qubits[1])
    circuit.measure(qubits, measurements)
    return circuit


def extract_v2_counts(pub_result: Any) -> dict[str, int]:
    """Extract counts from the named V2 classical-register result container."""
    try:
        counts = pub_result.data.measure.get_counts()
    except (AttributeError, TypeError) as exc:
        raise RuntimeError("SamplerV2 result did not contain the expected measure data.") from exc
    if not isinstance(counts, dict) or not counts:
        raise RuntimeError("SamplerV2 returned no measurement counts.")
    clean = {str(bitstring): int(count) for bitstring, count in counts.items()}
    if any(count < 0 for count in clean.values()):
        raise RuntimeError("SamplerV2 returned an invalid negative count.")
    return clean


@dataclass(frozen=True)
class HardwareSmokeResult:
    experiment: str
    classification: str
    backend: str
    job_id: str
    shots: int
    counts: dict[str, int]
    isa_qubits: int
    isa_depth: int
    qiskit_version: str
    qiskit_ibm_runtime_version: str
    interpretation: dict[str, bool]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def run_hardware_smoke(
    *, token: str, shots: int, submit_hardware: bool, confirmation: str
) -> HardwareSmokeResult:
    """Submit exactly one bounded Bell-state circuit in SamplerV2 backend-job mode."""
    require_confirmation(submit_hardware=submit_hardware, confirmation=confirmation)
    if not 1 <= shots <= 4096:
        raise ValueError("shots must be between 1 and 4096")

    try:
        import qiskit
        import qiskit_ibm_runtime
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install the quantum and ibm extras to execute on hardware.") from exc

    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
    pass_manager = generate_preset_pass_manager(
        target=backend.target, optimization_level=1, seed_transpiler=42
    )
    isa_circuit = pass_manager.run(build_hello_folk_circuit())
    sampler = SamplerV2(mode=backend)
    job = sampler.run([isa_circuit], shots=shots)
    pub_result = job.result()[0]
    counts = extract_v2_counts(pub_result)
    if sum(counts.values()) != shots:
        raise RuntimeError("SamplerV2 count total did not match the requested shot count.")
    backend_name = getattr(backend, "name", "unknown")
    if callable(backend_name):
        backend_name = backend_name()
    return HardwareSmokeResult(
        experiment="EXP-007 Hello Folk Music World",
        classification="real-QPU connectivity and execution smoke test",
        backend=str(backend_name),
        job_id=str(job.job_id()),
        shots=shots,
        counts=counts,
        isa_qubits=isa_circuit.num_qubits,
        isa_depth=isa_circuit.depth(),
        qiskit_version=str(qiskit.__version__),
        qiskit_ibm_runtime_version=str(qiskit_ibm_runtime.__version__),
        interpretation={
            "connectivity_smoke_only": True,
            "music_analysis_result": False,
            "real_folk_data_used": False,
            "quantum_advantage_claimed": False,
            "exp_005a_result": False,
        },
    )
