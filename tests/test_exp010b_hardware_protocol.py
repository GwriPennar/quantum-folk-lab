import json
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

import quantum_folk_lab.compact_hardware_protocol as protocol
from quantum_folk_lab.compact_hardware_protocol import (
    AMBIGUOUS_OUTCOME,
    AUTHORIZATION,
    BETA,
    GAMMA,
    ISING_HASH,
    QUBO_HASH,
    Readiness,
    SubmissionMetadata,
    displayed_bitstring,
    select_layout,
    submit_one_job,
)


def ready() -> Readiness:
    return Readiness(QUBO_HASH, ISING_HASH, GAMMA, BETA, True, True)


def metadata() -> SubmissionMetadata:
    return SubmissionMetadata(
        exp010b_commit="frozen-commit",
        backend="fixture-backend",
        backend_snapshot="fixture-snapshot",
        layout=(0, 1, 2, 3),
        qaoa_circuit_hash="qaoa-hash",
        control_circuit_hash="control-hash",
        shots_per_pub=4096,
        pub_count=2,
    )


def invoke(
    tmp_path: Path,
    *,
    readiness: Readiness | None = None,
    credential_reader: Callable[[], Any] = lambda: "credential",
    runtime_factory: Callable[[Any], Any] = lambda _: "runtime",
    submitter: Callable[[Any], str] = lambda _: "mock-job",
    intent: Path | None = None,
    receipt: Path | None = None,
) -> str:
    return submit_one_job(
        submit=True,
        phrase=AUTHORIZATION,
        readiness=readiness or ready(),
        metadata=metadata(),
        intent=intent or tmp_path / "intent.json",
        receipt=receipt or tmp_path / "receipt.json",
        credential_reader=credential_reader,
        runtime_factory=runtime_factory,
        submitter=submitter,
    )


def test_bit_order() -> None:
    assert displayed_bitstring("0101") == "1010"
    with pytest.raises(ValueError):
        displayed_bitstring("10")


@pytest.mark.parametrize("submit,phrase", [(False, AUTHORIZATION), (True, "wrong")])
def test_authorization_guard_precedes_external_calls(
    tmp_path: Path, submit: bool, phrase: str
) -> None:
    calls: list[str] = []
    with pytest.raises(PermissionError):
        submit_one_job(
            submit=submit,
            phrase=phrase,
            readiness=ready(),
            metadata=metadata(),
            intent=tmp_path / "intent.json",
            receipt=tmp_path / "receipt.json",
            credential_reader=lambda: calls.append("credential"),
            runtime_factory=lambda _: calls.append("runtime"),
            submitter=lambda _: "job",
        )
    assert calls == []


@pytest.mark.parametrize("field", ["hash", "angle", "equivalence", "backend"])
def test_readiness_failures_never_read_credentials(tmp_path: Path, field: str) -> None:
    values = ready().__dict__.copy()
    if field == "hash":
        values["qubo_hash"] = "bad"
    elif field == "angle":
        values["gamma"] = 0.0
    elif field == "equivalence":
        values["equivalence_passed"] = False
    else:
        values["backend_gates_passed"] = False
    called = False

    def reader() -> None:
        nonlocal called
        called = True

    with pytest.raises(RuntimeError):
        invoke(tmp_path, readiness=Readiness(**values), credential_reader=reader)
    assert not called


@pytest.mark.parametrize("existing", ["intent", "receipt"])
def test_existing_record_blocks_before_credentials(tmp_path: Path, existing: str) -> None:
    path = tmp_path / f"{existing}.json"
    path.write_text("do-not-overwrite", encoding="utf-8")
    called = False

    def reader() -> None:
        nonlocal called
        called = True

    with pytest.raises(RuntimeError):
        invoke(
            tmp_path,
            intent=path if existing == "intent" else None,
            receipt=path if existing == "receipt" else None,
            credential_reader=reader,
        )
    assert not called
    assert path.read_text(encoding="utf-8") == "do-not-overwrite"


def test_submitter_exception_preserves_intent_and_blocks_retry(tmp_path: Path) -> None:
    intent = tmp_path / "intent.json"
    external_secret = "credential-value-in-exception"

    def fail(_: Any) -> str:
        raise RuntimeError(external_secret)

    with pytest.raises(RuntimeError, match=AMBIGUOUS_OUTCOME):
        invoke(tmp_path, intent=intent, submitter=fail)
    assert intent.exists()
    assert external_secret not in intent.read_text(encoding="utf-8")
    credential_calls = 0

    def reader() -> None:
        nonlocal credential_calls
        credential_calls += 1

    with pytest.raises(RuntimeError, match=AMBIGUOUS_OUTCOME):
        invoke(tmp_path, intent=intent, credential_reader=reader)
    assert credential_calls == 0


def test_receipt_failure_preserves_intent_and_blocks_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    intent, receipt = tmp_path / "intent.json", tmp_path / "receipt.json"
    original = protocol._durable_exclusive_json

    def fail_receipt(path: Path, record: dict[str, Any]) -> None:
        if path == receipt:
            raise OSError("private external detail")
        original(path, record)

    monkeypatch.setattr(protocol, "_durable_exclusive_json", fail_receipt)
    with pytest.raises(RuntimeError, match=AMBIGUOUS_OUTCOME):
        invoke(tmp_path, intent=intent, receipt=receipt)
    assert intent.exists() and not receipt.exists()
    monkeypatch.setattr(protocol, "_durable_exclusive_json", original)
    with pytest.raises(RuntimeError, match=AMBIGUOUS_OUTCOME):
        invoke(tmp_path, intent=intent, receipt=receipt)


def test_concurrent_attempts_allow_only_one_submitter_call(tmp_path: Path) -> None:
    barrier = threading.Barrier(2)
    submit_calls = 0
    lock = threading.Lock()
    results: list[str] = []

    def submitter(_: Any) -> str:
        nonlocal submit_calls
        with lock:
            submit_calls += 1
        return "mock-job"

    def attempt() -> None:
        barrier.wait()
        try:
            results.append(invoke(tmp_path, submitter=submitter))
        except RuntimeError as error:
            results.append(str(error))

    threads = [threading.Thread(target=attempt) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert submit_calls == 1
    assert results.count("mock-job") == 1
    assert AMBIGUOUS_OUTCOME in results


def test_durable_records_have_required_fields_and_no_credential(tmp_path: Path) -> None:
    secret = "never-write-this-credential"
    assert invoke(tmp_path, credential_reader=lambda: secret) == "mock-job"
    intent = json.loads((tmp_path / "intent.json").read_text(encoding="utf-8"))
    receipt = json.loads((tmp_path / "receipt.json").read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "experiment_id",
        "attempt_id",
        "created_at_utc",
        "exp010a_squash",
        "exp010b_commit",
        "qubo_hash",
        "ising_hash",
        "gamma",
        "beta",
        "backend",
        "backend_snapshot",
        "layout",
        "qaoa_circuit_hash",
        "control_circuit_hash",
        "shots_per_pub",
        "pub_count",
        "retry",
        "state",
    }
    assert required <= intent.keys()
    assert receipt["attempt_id"] == intent["attempt_id"]
    assert receipt["job_id"] == "mock-job"
    assert secret not in json.dumps(intent) + json.dumps(receipt)


def test_selector_is_deterministic() -> None:
    base: dict[str, Any] = {
        "operational": True,
        "simulator": False,
        "qubits": 8,
        "transpiled": True,
        "two_qubit_depth": 8,
        "depth": 40,
        "duration_us": 50.0,
        "two_qubit_error": 0.01,
        "readout_error": 0.02,
        "usage": 1.0,
        "unavailable": False,
    }
    records = [
        dict(base, backend="fixture-b", layout=(1, 2, 3, 4), two_qubit_count=14),
        dict(base, backend="fixture-a", layout=(0, 1, 2, 3), two_qubit_count=12),
    ]
    assert select_layout(records)["backend"] == "fixture-a"
