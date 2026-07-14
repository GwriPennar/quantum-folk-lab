"""Portable glossary loader."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from quantum_folk_lab.learning.paths import GLOSSARY_PATH


@dataclass(frozen=True)
class GlossaryTerm:
    term: str
    one_liner: str
    deeper: str
    related_lessons: tuple[str, ...] = ()


@lru_cache(maxsize=1)
def load_glossary(path: Path | None = None) -> tuple[GlossaryTerm, ...]:
    glossary_path = path or GLOSSARY_PATH
    raw = yaml.safe_load(glossary_path.read_text(encoding="utf-8"))
    return tuple(
        GlossaryTerm(
            term=item["term"],
            one_liner=item["one_liner"],
            deeper=item["deeper"],
            related_lessons=tuple(item.get("related_lessons", []) or []),
        )
        for item in raw["terms"]
    )


def glossary_index() -> dict[str, GlossaryTerm]:
    return {t.term.lower(): t for t in load_glossary()}


def validate_glossary_references(terms: tuple[str, ...]) -> list[str]:
    index = glossary_index()
    errors: list[str] = []
    for term in terms:
        if term.lower() not in index:
            errors.append(f"unknown glossary term: {term}")
    return errors
