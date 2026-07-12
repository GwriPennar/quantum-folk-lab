"""Semantic state marker generation and validation."""

from __future__ import annotations

import html
import re

from quantum_folk_lab.learning.models import LessonDocument

FORBIDDEN_STATE_PATTERN = re.compile(
    r"(C:\\Users\\|/Users/[^/\s]+|api[_-]?key|token|credential)",
    re.I,
)


def semantic_marker_html(
    lesson: LessonDocument,
    *,
    renderer: str = "streamlit",
) -> str:
    meta = lesson.metadata
    return (
        f'<div data-qfl-state="{html.escape(meta.id)}" '
        f'data-qfl-route="{html.escape(meta.route)}" '
        f'data-qfl-mode="{html.escape(meta.mode)}" '
        f'data-qfl-content-version="{meta.version}" '
        f'data-qfl-renderer="{html.escape(renderer)}"></div>'
    )


def validate_semantic_text(text: str, lesson: LessonDocument) -> list[str]:
    errors: list[str] = []
    if FORBIDDEN_STATE_PATTERN.search(text):
        errors.append("forbidden path or secret pattern in rendered output")
    contract = lesson.metadata.semantic
    for marker in contract.required_markers:
        if marker not in text:
            errors.append(f"missing required marker: {marker}")
    for marker in contract.forbidden_markers:
        if marker in text:
            errors.append(f"forbidden stale marker present: {marker}")
    if lesson.metadata.id not in text and "data-qfl-state" not in text:
        errors.append("semantic state marker missing")
    return errors
