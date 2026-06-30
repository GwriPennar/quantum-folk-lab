from __future__ import annotations

from .models import Melody, NoteEvent


def transpose(melody: Melody, steps: int, tune_id: str) -> Melody:
    events = tuple(NoteEvent(e.pitch + steps, e.duration) for e in melody.events)
    return Melody(tune_id, melody.family, events, (*melody.transformations, f"transpose:{steps}"))


def substitute(melody: Melody, index: int, delta: int, tune_id: str) -> Melody:
    events = list(melody.events)
    old = events[index]
    events[index] = NoteEvent(old.pitch + delta, old.duration)
    return Melody(
        tune_id,
        melody.family,
        tuple(events),
        (*melody.transformations, f"substitute:{index}:{delta}"),
    )


def insert_note(melody: Melody, index: int, pitch: int, duration: int, tune_id: str) -> Melody:
    events = list(melody.events)
    events.insert(index, NoteEvent(pitch, duration))
    return Melody(
        tune_id, melody.family, tuple(events), (*melody.transformations, f"insert:{index}")
    )


def delete_note(melody: Melody, index: int, tune_id: str) -> Melody:
    events = list(melody.events)
    del events[index]
    return Melody(
        tune_id, melody.family, tuple(events), (*melody.transformations, f"delete:{index}")
    )


def alter_duration(melody: Melody, index: int, duration: int, tune_id: str) -> Melody:
    events = list(melody.events)
    old = events[index]
    events[index] = NoteEvent(old.pitch, duration)
    return Melody(
        tune_id,
        melody.family,
        tuple(events),
        (*melody.transformations, f"duration:{index}:{duration}"),
    )
