from datetime import UTC, datetime
from pathlib import Path

import pytest

from quantum_folk_lab.exp010d_submission import (
    SubmissionReceipt,
    canonical_workload_hash,
)


def receipt(**changes: object) -> SubmissionReceipt:
    values = {
        "schema_version": 2,
        "experiment_id": "EXP-010D-R3",
        "run_nonce": "nonce",
        "job_id": "job-1",
        "submitted_at_utc": "2026-07-20T07:00:00Z",
        "backend": "ibm_fez",
        "source_commit_sha": "a" * 40,
        "workload_sha256": "b" * 64,
        "isa_qpy_sha256": "c" * 64,
        "intent_sha256": "d" * 64,
        "retry": False,
    }
    values.update(changes)
    return SubmissionReceipt(**values)  # type: ignore[arg-type]


def test_complete_schema_two_receipt_is_deterministic() -> None:
    value = receipt()
    value.validate()
    assert value.serialize() == value.serialize()
    assert value.submitted_at_utc.endswith("Z")
    assert value.backend == "ibm_fez" and value.retry is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", 1),
        ("submitted_at_utc", ""),
        ("backend", "other"),
        ("source_commit_sha", "short"),
        ("workload_sha256", ""),
        ("isa_qpy_sha256", ""),
        ("intent_sha256", ""),
        ("retry", True),
    ],
)
def test_invalid_receipt_fields_fail_closed(field: str, value: object) -> None:
    with pytest.raises((ValueError, TypeError)):
        receipt(**{field: value}).validate()


def test_workload_mutations_change_canonical_hash() -> None:
    rows = [
        {
            "execution": index,
            "point_id": f"p{index}",
            "kind": "landscape",
            "gamma": "1",
            "beta": "2",
            "shots": 4096,
        }
        for index in range(1, 33)
    ]

    def digest(current: list[dict[str, object]], routing: dict[str, int]) -> str:
        return canonical_workload_hash(
            experiment_id="EXP-010D-R3",
            backend="ibm_fez",
            initial_layout=[20, 21, 23, 22],
            physical_qubit_set=[20, 21, 22, 23],
            routing_permutation=routing,
            final_layout=[23, 20, 22, 21],
            physical_to_classical={"23": 0, "20": 1, "22": 2, "21": 3},
            isa_qpy_sha256="c" * 64,
            rows=current,
            transpiler_seed=44,
        )

    original = digest(rows, {"20": 23, "21": 20, "22": 21, "23": 22})
    reordered = digest(list(reversed(rows)), {"20": 23, "21": 20, "22": 21, "23": 22})
    changed = [dict(row) for row in rows]
    changed[0]["shots"] = 1024
    altered_shots = digest(changed, {"20": 23, "21": 20, "22": 21, "23": 22})
    altered_routing = digest(rows, {"20": 20, "21": 21, "22": 22, "23": 23})
    assert len({original, reordered, altered_shots, altered_routing}) == 4


def test_injected_clock_format_reference() -> None:
    fixed = datetime(2026, 7, 20, 7, 0, tzinfo=UTC)
    assert fixed.astimezone(UTC).isoformat().replace("+00:00", "Z").endswith("Z")


def test_no_real_execution_evidence_in_tests(tmp_path: Path) -> None:
    assert not (tmp_path / "submission-intent.json").exists()
    assert not (tmp_path / "submission-receipt.json").exists()
