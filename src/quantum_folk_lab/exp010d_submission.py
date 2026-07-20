"""Fail-closed EXP-010D submission evidence and orchestration."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

AUTHORIZATION = "I AUTHORIZE ONE EXP-010D IBM QPU JOB"
BACKEND = "ibm_fez"
INITIAL_LAYOUT = (20, 21, 23, 22)
PHYSICAL_SET = (20, 21, 22, 23)
PUB_COUNT = 32
SHOTS = 4096
USAGE_CEILING = 180.0
QUBO_HASH = "96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e"
ISING_HASH = "635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def portable_file_hash(path: Path) -> str:
    return sha256_bytes(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode())


def parameter_row_hash(rows: Sequence[Mapping[str, Any]]) -> str:
    compact = [
        {
            "execution": row["execution"],
            "point_id": row["point_id"],
            "kind": row["kind"],
            "gamma": row["gamma"],
            "beta": row["beta"],
            "shots": row["shots"],
        }
        for row in rows
    ]
    return sha256_bytes(canonical_json(compact))


@dataclass(frozen=True)
class SubmissionEvidence:
    schema_version: int
    experiment_id: str
    source_commit_sha: str
    backend: str
    initial_layout: tuple[int, ...]
    physical_qubit_set: tuple[int, ...]
    routing_permutation: tuple[tuple[int, int], ...]
    final_logical_to_physical: tuple[int, ...]
    physical_to_classical: tuple[tuple[int, int], ...]
    decoding_manifest_sha256: str
    isa_qpy_sha256: str
    qubo_sha256: str
    ising_sha256: str
    grid_manifest_sha256: str
    execution_order_sha256: str
    workload_template_sha256: str
    ideal_landscape_sha256: str
    pub_count: int
    shots_per_pub: int
    parameter_row_sha256: str
    conservative_usage_seconds: float
    authorization_phrase: str
    run_nonce: str

    def validate(self) -> None:
        if self.schema_version != 1 or self.experiment_id != "EXP-010D-R2":
            raise ValueError("intent identity or schema mismatch")
        if self.backend != BACKEND or self.initial_layout != INITIAL_LAYOUT:
            raise ValueError("backend or initial layout mismatch")
        if self.physical_qubit_set != PHYSICAL_SET:
            raise ValueError("physical set mismatch")
        if len(self.routing_permutation) != 4 or len(self.final_logical_to_physical) != 4:
            raise ValueError("routing metadata incomplete")
        if len(self.physical_to_classical) != 4:
            raise ValueError("measurement mapping incomplete")
        hashes = (
            self.decoding_manifest_sha256,
            self.isa_qpy_sha256,
            self.grid_manifest_sha256,
            self.execution_order_sha256,
            self.workload_template_sha256,
            self.ideal_landscape_sha256,
            self.parameter_row_sha256,
        )
        if any(len(value) != 64 for value in hashes):
            raise ValueError("mandatory hash missing or malformed")
        if self.qubo_sha256 != QUBO_HASH or self.ising_sha256 != ISING_HASH:
            raise ValueError("scientific hash mismatch")
        if self.pub_count != PUB_COUNT or self.shots_per_pub != SHOTS:
            raise ValueError("PUB or shot contract mismatch")
        if not 0 <= self.conservative_usage_seconds <= USAGE_CEILING:
            raise ValueError("usage estimate exceeds ceiling")
        if self.authorization_phrase != AUTHORIZATION or not self.run_nonce:
            raise ValueError("authorization or nonce missing")

    def serialize(self) -> bytes:
        self.validate()
        return canonical_json(asdict(self))


def build_evidence(
    *,
    source_commit_sha: str,
    run_nonce: str,
    workload: Mapping[str, Any],
    preflight: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    paths: Mapping[str, Path],
) -> SubmissionEvidence:
    """Build evidence with one declared source for every safety-critical field."""
    required_workload = {
        "backend",
        "layout",
        "parameterised_isa_qpy_sha256",
        "qubo_sha256",
        "ising_sha256",
        "pub_count",
        "shots_per_pub",
    }
    required_preflight = {
        "initial_layout",
        "physical_qubit_set",
        "routing_permutation_on_physical_set",
        "layout",
        "physical_to_classical",
        "conservative_usage_seconds",
        "passes",
    }
    if not required_workload.issubset(workload):
        raise ValueError("workload evidence is incomplete")
    if not required_preflight.issubset(preflight):
        raise ValueError("preflight routing evidence is incomplete")
    if not preflight["passes"]:
        raise ValueError("preflight did not pass")
    if workload["parameterised_isa_qpy_sha256"] != sha256_bytes(paths["isa_qpy"].read_bytes()):
        raise ValueError("ISA hash mismatch")
    if len(rows) != PUB_COUNT or any(row["shots"] != SHOTS for row in rows):
        raise ValueError("row workload mismatch")
    evidence = SubmissionEvidence(
        schema_version=1,
        experiment_id="EXP-010D-R2",
        source_commit_sha=source_commit_sha,
        backend=str(workload["backend"]),
        initial_layout=tuple(preflight["initial_layout"]),
        physical_qubit_set=tuple(preflight["physical_qubit_set"]),
        routing_permutation=tuple(
            sorted(
                (int(key), int(value))
                for key, value in preflight["routing_permutation_on_physical_set"].items()
            )
        ),
        final_logical_to_physical=tuple(preflight["layout"]),
        physical_to_classical=tuple(
            sorted(
                (int(key), int(value)) for key, value in preflight["physical_to_classical"].items()
            )
        ),
        decoding_manifest_sha256=portable_file_hash(paths["decoding_manifest"]),
        isa_qpy_sha256=str(workload["parameterised_isa_qpy_sha256"]),
        qubo_sha256=str(workload["qubo_sha256"]),
        ising_sha256=str(workload["ising_sha256"]),
        grid_manifest_sha256=portable_file_hash(paths["grid_manifest"]),
        execution_order_sha256=portable_file_hash(paths["execution_order"]),
        workload_template_sha256=portable_file_hash(paths["workload_template"]),
        ideal_landscape_sha256=portable_file_hash(paths["ideal_landscape"]),
        pub_count=int(workload["pub_count"]),
        shots_per_pub=int(workload["shots_per_pub"]),
        parameter_row_sha256=parameter_row_hash(rows),
        conservative_usage_seconds=float(preflight["conservative_usage_seconds"]),
        authorization_phrase=AUTHORIZATION,
        run_nonce=run_nonce,
    )
    evidence.validate()
    return evidence


def durable_create(path: Path, payload: bytes) -> str:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    observed = path.read_bytes().replace(b"\r\n", b"\n")
    if observed != payload:
        raise RuntimeError("durable intent verification failed")
    return sha256_bytes(payload)


def execute_once(
    *,
    evidence: SubmissionEvidence,
    intent_path: Path,
    receipt_path: Path,
    credential_reader: Callable[[], Any],
    service_factory: Callable[[Any], Any],
    sampler_factory: Callable[[Any], Any],
    submitter: Callable[[Any], str],
) -> str:
    """Enforce validation → intent → credential → service → sampler → one call → receipt."""
    if intent_path.exists() or receipt_path.exists():
        raise RuntimeError("stale intent or receipt blocks execution")
    intent_hash = durable_create(intent_path, evidence.serialize())
    credential = credential_reader()
    service = service_factory(credential)
    sampler = sampler_factory(service)
    job_id = submitter(sampler)
    if not job_id:
        raise RuntimeError("submission returned no job ID")
    receipt = canonical_json(
        {
            "schema_version": 1,
            "experiment_id": evidence.experiment_id,
            "run_nonce": evidence.run_nonce,
            "job_id": job_id,
            "intent_sha256": intent_hash,
            "retry": False,
        }
    )
    durable_create(receipt_path, receipt)
    return job_id
