"""Canonical public lesson registry."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from quantum_folk_lab.learning.models import LessonDocument
from quantum_folk_lab.learning.parser import load_lesson
from quantum_folk_lab.learning.paths import REGISTRY_PATH


@dataclass(frozen=True)
class RegistryEntry:
    id: str
    path: str
    route: str
    mode: str
    order: int
    title: str
    legacy_progress_key: str | None = None
    foundations_nav: bool = False
    section: str = ""


@dataclass
class LessonRegistry:
    version: int
    entries: tuple[RegistryEntry, ...]

    def by_id(self, lesson_id: str) -> RegistryEntry:
        for entry in self.entries:
            if entry.id == lesson_id:
                return entry
        raise KeyError(lesson_id)

    def by_route(self, route: str) -> RegistryEntry:
        for entry in self.entries:
            if entry.route == route:
                return entry
        raise KeyError(route)

    def ordered(self) -> tuple[RegistryEntry, ...]:
        return tuple(sorted(self.entries, key=lambda e: e.order))

    def foundations_entries(self) -> tuple[RegistryEntry, ...]:
        return tuple(e for e in self.ordered() if e.foundations_nav)

    def next_entry(self, lesson_id: str) -> RegistryEntry | None:
        ordered = self.ordered()
        ids = [e.id for e in ordered]
        if lesson_id not in ids:
            return ordered[0] if ordered else None
        idx = ids.index(lesson_id)
        doc = self.load_document(lesson_id)
        if doc.metadata.next_lesson:
            try:
                return self.by_id(doc.metadata.next_lesson)
            except KeyError:
                pass
        if idx + 1 < len(ordered):
            return ordered[idx + 1]
        return None

    def load_document(self, lesson_id: str) -> LessonDocument:
        entry = self.by_id(lesson_id)
        return load_lesson(entry.path)


@lru_cache(maxsize=1)
def load_registry(path: Path | None = None) -> LessonRegistry:
    registry_path = path or REGISTRY_PATH
    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    entries = tuple(
        RegistryEntry(
            id=item["id"],
            path=item["path"],
            route=item["route"],
            mode=item["mode"],
            order=int(item["order"]),
            title=item["title"],
            legacy_progress_key=item.get("legacy_progress_key"),
            foundations_nav=bool(item.get("foundations_nav", False)),
            section=str(item.get("section", "")),
        )
        for item in raw["lessons"]
    )
    ids = [e.id for e in entries]
    routes = [e.route for e in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate lesson ids in registry")
    if len(routes) != len(set(routes)):
        raise ValueError("duplicate routes in registry")
    return LessonRegistry(version=int(raw.get("version", 1)), entries=entries)


def clear_registry_cache() -> None:
    load_registry.cache_clear()
