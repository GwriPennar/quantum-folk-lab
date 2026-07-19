"""Offline helpers for optional external research-data selection.

This module has no configured data path and performs no I/O on import. Callers must
provide an external IrishMAN cache explicitly and must not treat matching as a
copyright or provenance determination.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


class ExternalResearchDataUnavailable(RuntimeError):
    """Raised when explicitly requested external research data is unavailable."""


_HEADER_RE = re.compile(r"^[A-Za-z]:")
_NOTE_RE = re.compile(
    r"(?:\^{1,2}|_{1,2}|=)?(?P<note>[A-Ga-g])(?P<oct>[,']*)"
    r"(?:\d+(?:/\d*)?|/+)?"
)


def _diatonic_intervals(abc: str) -> list[int]:
    music_lines = [
        line.split("%", 1)[0] for line in abc.splitlines() if not _HEADER_RE.match(line.strip())
    ]
    music = "\n".join(music_lines)
    music = re.sub(
        r'"[^"]*"|![^!]*!|\{[^}]*\}|\[[A-Za-z]:[^]]*\]',
        "",
        music,
    )
    pitches: list[int] = []
    for match in _NOTE_RE.finditer(music):
        letter = match.group("note")
        octave = int(letter.islower())
        octave += match.group("oct").count("'")
        octave -= match.group("oct").count(",")
        pitches.append("CDEFGAB".index(letter.upper()) + 7 * octave)
    return [right - left for left, right in zip(pitches, pitches[1:], strict=False)]


def normalized_melody_fingerprint(abc: str) -> str:
    """Hash a transposition-invariant, non-note-bearing interval representation."""

    intervals = _diatonic_intervals(abc)
    payload = ",".join(map(str, intervals)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def hashed_interval_ngrams(abc: str) -> Counter[str]:
    """Return hashed interval 2–4-gram counts without exposing ordered sequences."""

    intervals = _diatonic_intervals(abc)
    result: Counter[str] = Counter()
    for width in (2, 3, 4):
        for start in range(max(0, len(intervals) - width + 1)):
            gram = ",".join(map(str, intervals[start : start + width]))
            token = hashlib.sha256(f"{width}:{gram}".encode("ascii")).hexdigest()[:16]
            result[token] += 1
    return result


def cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    """Compute cosine similarity over hashed frequency mappings."""

    dot = sum(value * right.get(key, 0) for key, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def canonical_record_sha256(record: Mapping[str, Any]) -> str:
    """Hash a JSON record using a documented deterministic serialization."""

    payload = json.dumps(
        record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_external_files(root: Path, expected_sha256: Mapping[str, str]) -> None:
    """Fail clearly unless explicitly supplied external files match pinned hashes."""

    for filename, expected in expected_sha256.items():
        path = root / filename
        if not path.is_file():
            raise ExternalResearchDataUnavailable(
                f"External IrishMAN file is absent: {filename}. "
                "Obtain the pinned dataset separately and pass its cache directory explicitly."
            )
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ExternalResearchDataUnavailable(
                f"External IrishMAN file failed its pinned hash check: {filename}."
            )


def select_exact_match(
    candidate_fingerprint: str,
    matches: Iterable[Mapping[str, Any]],
) -> Mapping[str, Any]:
    """Select the lowest split/index exact match using a deterministic tie-break."""

    split_order = {"train": 0, "validation": 1}
    exact = [
        match for match in matches if match.get("normalized_fingerprint") == candidate_fingerprint
    ]
    if not exact:
        raise ValueError("No exact normalized-fingerprint match exists.")
    return min(
        exact,
        key=lambda match: (
            split_order.get(str(match.get("split")), 2),
            int(match["row_index"]),
        ),
    )
