from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NoteEvent:
    pitch: int
    duration: int

    def __post_init__(self) -> None:
        if self.duration <= 0:
            raise ValueError("duration must be positive")


@dataclass(frozen=True)
class Melody:
    tune_id: str
    family: str
    events: tuple[NoteEvent, ...]
    transformations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.events) < 2:
            raise ValueError("a melody needs at least two events")

    @property
    def pitches(self) -> tuple[int, ...]:
        return tuple(event.pitch for event in self.events)

    @property
    def durations(self) -> tuple[int, ...]:
        return tuple(event.duration for event in self.events)

    @property
    def intervals(self) -> tuple[int, ...]:
        return tuple(b - a for a, b in zip(self.pitches, self.pitches[1:], strict=False))

    @property
    def contour(self) -> tuple[str, ...]:
        def sign(interval: int) -> str:
            return "U" if interval > 0 else "D" if interval < 0 else "S"

        return tuple(sign(interval) for interval in self.intervals)
