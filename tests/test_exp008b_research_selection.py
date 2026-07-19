import json
from pathlib import Path

import pytest

from quantum_folk_lab.research_selection import (
    ExternalResearchDataUnavailable,
    canonical_record_sha256,
    cosine_similarity,
    hashed_interval_ngrams,
    normalized_melody_fingerprint,
    select_exact_match,
    verify_external_files,
)


def test_fingerprint_and_similarity_are_transposition_invariant() -> None:
    first = "X:1\nM:4/4\nK:C\nC D E G | E D C2 |"
    transposed = "X:2\nM:4/4\nK:G\nG A B d | B A G2 |"

    assert normalized_melody_fingerprint(first) == normalized_melody_fingerprint(transposed)
    assert cosine_similarity(
        hashed_interval_ngrams(first), hashed_interval_ngrams(transposed)
    ) == pytest.approx(1.0)


def test_canonical_record_hash_is_key_order_independent() -> None:
    left = {"control code": "S:1", "abc notation": "X:1\nK:C\nC2"}
    right = {"abc notation": "X:1\nK:C\nC2", "control code": "S:1"}

    assert canonical_record_sha256(left) == canonical_record_sha256(right)


def test_exact_match_uses_train_then_lowest_index() -> None:
    fingerprint = "f" * 64
    matches = [
        {"split": "validation", "row_index": 1, "normalized_fingerprint": fingerprint},
        {"split": "train", "row_index": 9, "normalized_fingerprint": fingerprint},
        {"split": "train", "row_index": 3, "normalized_fingerprint": fingerprint},
    ]

    assert select_exact_match(fingerprint, matches)["row_index"] == 3


def test_exact_match_does_not_silently_use_approximation() -> None:
    with pytest.raises(ValueError, match="No exact"):
        select_exact_match(
            "a" * 64,
            [{"split": "train", "row_index": 0, "normalized_fingerprint": "b" * 64}],
        )


def test_external_data_absence_and_hash_mismatch_fail_clearly(tmp_path: Path) -> None:
    with pytest.raises(ExternalResearchDataUnavailable, match="absent"):
        verify_external_files(tmp_path, {"train.json": "0" * 64})

    (tmp_path / "train.json").write_text("[]", encoding="utf-8")
    with pytest.raises(ExternalResearchDataUnavailable, match="hash check"):
        verify_external_files(tmp_path, {"train.json": "0" * 64})


def test_external_data_accepts_pinned_synthetic_file(tmp_path: Path) -> None:
    path = tmp_path / "train.json"
    path.write_text("[]", encoding="utf-8")
    expected = "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"

    verify_external_files(tmp_path, {"train.json": expected})


def test_public_manifest_has_four_by_two_shape_without_raw_abc() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "experiments" / "EXP-008B-alaw-irishman-selection" / "selection-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    settings = manifest["settings"]
    families = {setting["family_id"] for setting in settings}

    assert len(settings) == 8
    assert len(families) == 4
    assert all(
        sum(setting["family_id"] == family for setting in settings) == 2 for family in families
    )
    assert all(setting["research_computation_eligible"] for setting in settings)
    assert all(not setting["public_redistribution_eligible"] for setting in settings)
    assert "abc notation" not in path.read_text(encoding="utf-8").lower()
