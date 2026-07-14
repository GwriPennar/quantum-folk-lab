"""Approved public content roots and path resolution."""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PACKAGE_ROOT.parent
CONTENT_ROOT = REPO_ROOT / "learn"
LESSONS_ROOT = CONTENT_ROOT / "lessons"
DIAGRAMS_SOURCE = CONTENT_ROOT / "diagrams" / "source"
REGISTRY_PATH = CONTENT_ROOT / "registry.yaml"
SCHEMA_PATH = CONTENT_ROOT / "schemas" / "lesson.schema.json"
GLOSSARY_PATH = CONTENT_ROOT / "glossary.yaml"

APPROVED_ROOTS = (CONTENT_ROOT,)


def resolve_lesson_path(relative: str) -> Path:
    candidate = (CONTENT_ROOT / relative).resolve()
    content_root = CONTENT_ROOT.resolve()
    if content_root not in candidate.parents and candidate != content_root:
        raise ValueError(f"lesson path outside approved roots: {relative}")
    if not str(candidate).startswith(str(content_root)):
        raise ValueError(f"lesson path outside approved roots: {relative}")
    return candidate
