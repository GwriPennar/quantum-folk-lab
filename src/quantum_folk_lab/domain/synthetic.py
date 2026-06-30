from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import Melody, NoteEvent
from .transforms import alter_duration, delete_note, insert_note, substitute, transpose


def _melody(tune_id: str, family: str, pitches: list[int], durations: list[int]) -> Melody:
    return Melody(
        tune_id,
        family,
        tuple(NoteEvent(p, d) for p, d in zip(pitches, durations, strict=True)),
        ("base",),
    )


def generate_benchmark(seed: int = 42, variants_per_family: int = 4) -> list[Melody]:
    if variants_per_family != 4:
        raise ValueError("the checked MVP benchmark uses exactly four variants per family")
    base_a = _melody("fam_a_base", "A", [0, 2, 4, 5, 7, 5, 4, 2], [1, 1, 1, 1, 2, 1, 1, 2])
    base_b = _melody("fam_b_base", "B", [7, 5, 3, 2, 0, 2, 3, 5], [1, 2, 1, 1, 1, 1, 2, 1])
    return [
        base_a,
        transpose(base_a, 3, "fam_a_transposed"),
        substitute(base_a, 3, 1, "fam_a_substitution"),
        alter_duration(base_a, 4, 1 + seed % 2, "fam_a_rhythm"),
        base_b,
        transpose(base_b, -2, "fam_b_transposed"),
        insert_note(base_b, 4, 1, 1, "fam_b_inserted"),
        delete_note(base_b, 2, "fam_b_deleted"),
    ]


def labels(melodies: list[Melody]) -> list[int]:
    families = {family: index for index, family in enumerate(sorted({m.family for m in melodies}))}
    return [families[m.family] for m in melodies]


def to_jsonable(melodies: list[Melody]) -> list[dict[str, object]]:
    return [asdict(melody) for melody in melodies]


def write_json(path: Path, melodies: list[Melody]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_jsonable(melodies), indent=2), encoding="utf-8")
