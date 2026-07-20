"""Fail-closed EXP-011 submission identity built on governed EXP-010D machinery."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from quantum_folk_lab.exp010d_submission import canonical_workload_hash

AUTHORIZATION = "I AUTHORIZE ONE EXP-011 IBM QPU JOB"
EXPERIMENT_ID = "EXP-011"
BACKEND = "ibm_fez"
INITIAL_LAYOUT = (20, 21, 23, 22)
PHYSICAL_SET = (20, 21, 22, 23)
PUB_COUNT = 88
SHOTS = 4096
USAGE_CEILING = 100.0


@dataclass(frozen=True)
class ExperimentIdentity:
    experiment_id: str
    authorization_phrase: str
    pub_count: int
    shots_per_pub: int
    backend: str

    def validate(self) -> None:
        if self.experiment_id != EXPERIMENT_ID or self.authorization_phrase != AUTHORIZATION:
            raise ValueError("EXP-011 identity or authorization mismatch")
        if self.pub_count != PUB_COUNT or self.shots_per_pub != SHOTS:
            raise ValueError("EXP-011 workload mismatch")
        if self.backend != BACKEND:
            raise ValueError("EXP-011 backend mismatch")


IDENTITY = ExperimentIdentity(EXPERIMENT_ID, AUTHORIZATION, PUB_COUNT, SHOTS, BACKEND)


def validate_preflight_usage(seconds: float) -> None:
    if not 0 <= seconds <= USAGE_CEILING:
        raise ValueError("EXP-011 usage estimate exceeds hard ceiling")


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _durable_create(path: Path, payload: bytes) -> str:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if path.read_bytes().replace(b"\r\n", b"\n") != payload:
        raise RuntimeError("durable EXP-011 evidence verification failed")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class SubmissionIntent:
    schema_version: int
    experiment_id: str
    source_commit_sha: str
    run_nonce: str
    workload_sha256: str
    isa_qpy_sha256: str
    authorization_phrase: str
    pub_count: int
    shots_per_pub: int
    backend: str
    conservative_usage_seconds: float

    def validate(self) -> None:
        IDENTITY.validate()
        if self.schema_version != 1 or self.experiment_id != EXPERIMENT_ID:
            raise ValueError("stale or foreign intent identity")
        if self.authorization_phrase != AUTHORIZATION:
            raise ValueError("EXP-011 authorization mismatch")
        if len(self.source_commit_sha) != 40 or not self.run_nonce:
            raise ValueError("source SHA or run nonce malformed")
        if any(len(value) != 64 for value in (self.workload_sha256, self.isa_qpy_sha256)):
            raise ValueError("intent hash malformed")
        if self.pub_count != PUB_COUNT or self.shots_per_pub != SHOTS or self.backend != BACKEND:
            raise ValueError("intent workload mismatch")
        validate_preflight_usage(self.conservative_usage_seconds)

    def serialize(self) -> bytes:
        self.validate()
        return _canonical(asdict(self))


@dataclass(frozen=True)
class SubmissionReceipt:
    schema_version: int
    experiment_id: str
    run_nonce: str
    job_id: str
    submitted_at_utc: str
    backend: str
    source_commit_sha: str
    workload_sha256: str
    isa_qpy_sha256: str
    intent_sha256: str
    retry: bool

    def validate(self) -> None:
        if self.schema_version != 1 or self.experiment_id != EXPERIMENT_ID:
            raise ValueError("stale or foreign receipt identity")
        if not self.job_id or not self.run_nonce or self.backend != BACKEND or self.retry:
            raise ValueError("receipt job, backend, nonce, or retry invalid")
        if len(self.source_commit_sha) != 40:
            raise ValueError("receipt source SHA malformed")
        if any(
            len(value) != 64
            for value in (
                self.workload_sha256,
                self.isa_qpy_sha256,
                self.intent_sha256,
            )
        ):
            raise ValueError("receipt hash malformed")
        datetime.fromisoformat(self.submitted_at_utc.removesuffix("Z") + "+00:00")

    def serialize(self) -> bytes:
        self.validate()
        return _canonical(asdict(self))


def execute_once(
    *,
    intent: SubmissionIntent,
    intent_path: Path,
    receipt_path: Path,
    credential_reader: Callable[[], Any],
    service_factory: Callable[[Any], Any],
    sampler_factory: Callable[[Any], Any],
    submitter: Callable[[Any], str],
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> str:
    """Validate, persist intent, then permit exactly one injected submission call."""
    if intent_path.exists() or receipt_path.exists():
        raise RuntimeError("stale EXP-011 intent or receipt blocks execution")
    intent.validate()
    intent_hash = _durable_create(intent_path, intent.serialize())
    credential = credential_reader()
    service = service_factory(credential)
    sampler = sampler_factory(service)
    job_id = submitter(sampler)
    if not job_id:
        raise RuntimeError("EXP-011 submission returned no job ID")
    receipt = SubmissionReceipt(
        schema_version=1,
        experiment_id=EXPERIMENT_ID,
        run_nonce=intent.run_nonce,
        job_id=job_id,
        submitted_at_utc=clock().astimezone(UTC).isoformat().replace("+00:00", "Z"),
        backend=BACKEND,
        source_commit_sha=intent.source_commit_sha,
        workload_sha256=intent.workload_sha256,
        isa_qpy_sha256=intent.isa_qpy_sha256,
        intent_sha256=intent_hash,
        retry=False,
    )
    _durable_create(receipt_path, receipt.serialize())
    return job_id


__all__ = [
    "AUTHORIZATION",
    "BACKEND",
    "EXPERIMENT_ID",
    "IDENTITY",
    "INITIAL_LAYOUT",
    "PHYSICAL_SET",
    "PUB_COUNT",
    "SHOTS",
    "USAGE_CEILING",
    "canonical_workload_hash",
    "SubmissionIntent",
    "SubmissionReceipt",
    "execute_once",
    "validate_preflight_usage",
]
