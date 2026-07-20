from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from quantum_folk_lab.exp010d_submission import (
    AUTHORIZATION,
    SubmissionEvidence,
    build_evidence,
    execute_once,
)


def fixture(
    tmp_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Path]]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in (
        "decoding_manifest",
        "grid_manifest",
        "execution_order",
        "workload_template",
        "ideal_landscape",
    ):
        files[name] = tmp_path / f"{name}.json"
        files[name].write_text('{"schema_version":1}\n', encoding="utf-8")
    files["isa_qpy"] = tmp_path / "isa.qpy"
    files["isa_qpy"].write_bytes(b"qpy")
    import hashlib

    qpy_hash = hashlib.sha256(b"qpy").hexdigest()
    workload = {
        "backend": "ibm_fez",
        "layout": [20, 21, 23, 22],
        "parameterised_isa_qpy_sha256": qpy_hash,
        "qubo_sha256": "96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e",
        "ising_sha256": "635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5",
        "pub_count": 32,
        "shots_per_pub": 4096,
    }
    preflight = {
        "initial_layout": [20, 21, 23, 22],
        "physical_qubit_set": [20, 21, 22, 23],
        "routing_permutation_on_physical_set": {"20": 23, "21": 20, "22": 21, "23": 22},
        "layout": [23, 20, 22, 21],
        "physical_to_classical": {"23": 0, "20": 1, "22": 2, "21": 3},
        "conservative_usage_seconds": 32.5,
        "passes": True,
    }
    rows = [
        {
            "execution": i,
            "point_id": f"p{i}",
            "kind": "landscape",
            "gamma": "1",
            "beta": "2",
            "shots": 4096,
        }
        for i in range(1, 33)
    ]
    return workload, preflight, rows, files


def evidence(tmp_path: Path, nonce: str = "nonce") -> SubmissionEvidence:
    workload, preflight, rows, paths = fixture(tmp_path)
    return build_evidence(
        source_commit_sha="a" * 40,
        run_nonce=nonce,
        workload=workload,
        preflight=preflight,
        rows=rows,
        paths=paths,
    )


def test_valid_complete_evidence_is_deterministic_and_typed(tmp_path: Path) -> None:
    value = evidence(tmp_path)
    assert value.initial_layout == (20, 21, 23, 22)
    assert value.physical_qubit_set == (20, 21, 22, 23)
    assert value.final_logical_to_physical == (23, 20, 22, 21)
    assert value.authorization_phrase == AUTHORIZATION
    assert value.serialize() == value.serialize()
    assert evidence(tmp_path, "different").run_nonce != value.run_nonce


@pytest.mark.parametrize(
    "key", ["routing_permutation_on_physical_set", "layout", "physical_to_classical"]
)
def test_missing_routing_evidence_fails_closed(tmp_path: Path, key: str) -> None:
    workload, preflight, rows, paths = fixture(tmp_path)
    del preflight[key]
    with pytest.raises(ValueError, match="preflight routing"):
        build_evidence(
            source_commit_sha="a" * 40,
            run_nonce="n",
            workload=workload,
            preflight=preflight,
            rows=rows,
            paths=paths,
        )


def test_missing_or_mismatched_isa_fails_closed(tmp_path: Path) -> None:
    workload, preflight, rows, paths = fixture(tmp_path)
    workload.pop("parameterised_isa_qpy_sha256")
    with pytest.raises(ValueError, match="workload evidence"):
        build_evidence(
            source_commit_sha="a" * 40,
            run_nonce="n",
            workload=workload,
            preflight=preflight,
            rows=rows,
            paths=paths,
        )
    workload, preflight, rows, paths = fixture(tmp_path)
    paths["isa_qpy"].write_bytes(b"changed")
    with pytest.raises(ValueError, match="ISA hash"):
        build_evidence(
            source_commit_sha="a" * 40,
            run_nonce="n",
            workload=workload,
            preflight=preflight,
            rows=rows,
            paths=paths,
        )


@pytest.mark.parametrize(("field", "value"), [("pub_count", 31), ("shots_per_pub", 1024)])
def test_pub_and_shot_changes_fail_closed(tmp_path: Path, field: str, value: int) -> None:
    workload, preflight, rows, paths = fixture(tmp_path)
    workload[field] = value
    with pytest.raises(ValueError):
        build_evidence(
            source_commit_sha="a" * 40,
            run_nonce="n",
            workload=workload,
            preflight=preflight,
            rows=rows,
            paths=paths,
        )


def test_stale_intent_or_receipt_blocks_before_credential(tmp_path: Path) -> None:
    called = []
    for occupied in ("intent", "receipt"):
        intent, receipt = tmp_path / f"{occupied}-intent", tmp_path / f"{occupied}-receipt"
        (intent if occupied == "intent" else receipt).write_text("stale", encoding="utf-8")
        with pytest.raises(RuntimeError, match="stale"):
            execute_once(
                evidence=evidence(tmp_path / occupied),
                intent_path=intent,
                receipt_path=receipt,
                credential_reader=lambda: called.append("credential"),
                service_factory=lambda _: None,
                sampler_factory=lambda _: None,
                submitter=lambda _: "job",
            )
    assert called == []


def test_offline_rehearsal_orders_one_call_and_writes_receipt(tmp_path: Path) -> None:
    events: list[str] = []
    calls = 0

    def submit(_: object) -> str:
        nonlocal calls
        calls += 1
        events.append("submit")
        return "job-1"

    def credential() -> str:
        events.append("credential")
        return "secret"

    def service(_: object) -> object:
        events.append("service")
        return object()

    def sampler(_: object) -> object:
        events.append("sampler")
        return object()

    job = execute_once(
        evidence=evidence(tmp_path),
        intent_path=tmp_path / "intent",
        receipt_path=tmp_path / "receipt",
        credential_reader=credential,
        service_factory=service,
        sampler_factory=sampler,
        submitter=submit,
    )
    assert job == "job-1" and calls == 1
    assert events == ["credential", "service", "sampler", "submit"]
    assert json.loads((tmp_path / "receipt").read_text())["job_id"] == "job-1"


def test_submission_exception_is_never_retried(tmp_path: Path) -> None:
    calls = 0

    def fail(_: object) -> str:
        nonlocal calls
        calls += 1
        raise RuntimeError("ambiguous")

    with pytest.raises(RuntimeError, match="ambiguous"):
        execute_once(
            evidence=evidence(tmp_path),
            intent_path=tmp_path / "intent",
            receipt_path=tmp_path / "receipt",
            credential_reader=lambda: "secret",
            service_factory=lambda _: object(),
            sampler_factory=lambda _: object(),
            submitter=fail,
        )
    assert calls == 1 and (tmp_path / "intent").exists() and not (tmp_path / "receipt").exists()
