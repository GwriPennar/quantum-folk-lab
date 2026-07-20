from __future__ import annotations

import copy

import pytest

from quantum_folk_lab.exp011_submission import (
    AUTHORIZATION,
    IDENTITY,
    SubmissionIntent,
    canonical_workload_hash,
    validate_preflight_usage,
)


def rows() -> list[dict[str, object]]:
    return [
        {
            "execution": i,
            "point_id": f"p{i}",
            "kind": "landscape",
            "gamma": "1",
            "beta": "2",
            "shots": 4096,
        }
        for i in range(1, 89)
    ]


def digest(value: list[dict[str, object]]) -> str:
    return canonical_workload_hash(
        experiment_id="EXP-011",
        backend="ibm_fez",
        initial_layout=[20, 21, 23, 22],
        physical_qubit_set=[20, 21, 22, 23],
        routing_permutation={"20": 23, "21": 20, "22": 21, "23": 22},
        final_layout=[23, 20, 22, 21],
        physical_to_classical={"23": 0, "20": 1, "22": 2, "21": 3},
        isa_qpy_sha256="a" * 64,
        rows=value,
        transpiler_seed=44,
    )


def test_mutations_change_workload_hash() -> None:
    original = rows()
    reordered = list(reversed(original))
    changed_cell, changed_shots = copy.deepcopy(original), copy.deepcopy(original)
    changed_cell[0]["gamma"] = "1.1"
    changed_shots[0]["shots"] = 1024
    assert (
        len({digest(original), digest(reordered), digest(changed_cell), digest(changed_shots)}) == 4
    )


def test_exp011_identity_rejects_prior_authorization() -> None:
    IDENTITY.validate()
    assert AUTHORIZATION == "I AUTHORIZE ONE EXP-011 IBM QPU JOB"
    assert AUTHORIZATION != "I AUTHORIZE ONE EXP-010D IBM QPU JOB"


def test_usage_gate_fails_closed() -> None:
    validate_preflight_usage(89.278869504)
    with pytest.raises(ValueError, match="ceiling"):
        validate_preflight_usage(100.000001)


def intent(**changes: object) -> SubmissionIntent:
    values: dict[str, object] = {
        "schema_version": 1,
        "experiment_id": "EXP-011",
        "source_commit_sha": "a" * 40,
        "run_nonce": "fresh",
        "workload_sha256": "b" * 64,
        "isa_qpy_sha256": "c" * 64,
        "authorization_phrase": AUTHORIZATION,
        "pub_count": 88,
        "shots_per_pub": 4096,
        "backend": "ibm_fez",
        "conservative_usage_seconds": 89.278869504,
    }
    values.update(changes)
    return SubmissionIntent(**values)  # type: ignore[arg-type]


def test_stale_exp010d_identity_cannot_authorize_exp011() -> None:
    with pytest.raises(ValueError, match="foreign"):
        intent(experiment_id="EXP-010D-R3").validate()
    with pytest.raises(ValueError, match="authorization"):
        intent(authorization_phrase="I AUTHORIZE ONE EXP-010D IBM QPU JOB").validate()
