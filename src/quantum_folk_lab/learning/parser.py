"""Markdown + YAML front matter loader for public Foundations lessons."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import yaml

from quantum_folk_lab.learning.directives import DIRECTIVE_PATTERN, parse_directive_block
from quantum_folk_lab.learning.models import (
    CompletionRule,
    LessonBlock,
    LessonDocument,
    LessonMetadata,
    LessonMode,
    LessonSection,
    LessonStatus,
    MarkdownBlock,
    MermaidBlock,
    SemanticContract,
)
from quantum_folk_lab.learning.paths import CONTENT_ROOT, resolve_lesson_path

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MERMAID_FENCE_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def _parse_metadata(raw: dict[str, Any], source_path: Path) -> LessonMetadata:
    semantic_raw = raw.get("semantic", {}) or {}
    completion_raw = raw.get("completion", {}) or {}
    completion = None
    if completion_raw:
        completion = CompletionRule(
            type=str(completion_raw.get("type", "view")),
            legacy_key=completion_raw.get("legacy_key"),
        )
    try:
        rel = str(source_path.resolve().relative_to(CONTENT_ROOT.resolve()))
    except ValueError:
        rel = source_path.name
    return LessonMetadata(
        id=str(raw["id"]),
        version=int(raw.get("version", 1)),
        title=str(raw["title"]),
        mode=LessonMode(str(raw["mode"])),
        section=str(raw["section"]),
        order=int(raw["order"]),
        route=str(raw["route"]),
        status=LessonStatus(str(raw.get("status", "active"))),
        estimated_minutes=raw.get("estimated_minutes"),
        visuals=tuple(raw.get("visuals", []) or []),
        interactions=tuple(raw.get("interactions", []) or []),
        glossary_terms=tuple(raw.get("glossary_terms", []) or []),
        prerequisites=tuple(raw.get("prerequisites", []) or []),
        next_lesson=raw.get("next_lesson"),
        learning_objectives=tuple(raw.get("learning_objectives", []) or []),
        check_question=str(raw.get("check_question", "")),
        learned_summary=str(raw.get("learned_summary", "")),
        lab_link=raw.get("lab_link"),
        foundations_nav=bool(raw.get("foundations_nav", False)),
        static_export=bool(raw.get("static_export", True)),
        completion=completion,
        semantic=SemanticContract(
            required_markers=tuple(semantic_raw.get("required_markers", []) or []),
            forbidden_markers=tuple(semantic_raw.get("forbidden_markers", []) or []),
        ),
        legacy_progress_key=raw.get("legacy_progress_key"),
        source_path=rel,
    )


def _split_sections(blocks: list[LessonBlock]) -> tuple[LessonSection, ...]:
    sections: list[LessonSection] = []
    current_heading: str | None = None
    current_blocks: list[LessonBlock] = []

    def flush() -> None:
        nonlocal current_blocks, current_heading
        if current_blocks:
            sections.append(LessonSection(heading=current_heading, blocks=tuple(current_blocks)))
            current_blocks = []

    for block in blocks:
        if isinstance(block, MarkdownBlock) and block.text.startswith("## "):
            flush()
            current_heading = block.text.removeprefix("## ").strip()
            current_blocks.append(block)
        else:
            current_blocks.append(block)
    flush()
    if not sections and blocks:
        sections = [LessonSection(heading=None, blocks=tuple(blocks))]
    return tuple(sections)


def parse_lesson_markdown(text: str, source_path: Path) -> LessonDocument:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"missing YAML front matter: {source_path}")
    raw = yaml.safe_load(match.group(1))
    body = text[match.end() :]

    blocks: list[LessonBlock] = []
    line_offset = text[: match.end()].count("\n") + 1
    cursor = 0

    def line_at(pos: int) -> int:
        return line_offset + body[:pos].count("\n")

    while cursor < len(body):
        directive_match = DIRECTIVE_PATTERN.search(body, cursor)
        mermaid_match = MERMAID_FENCE_RE.search(body, cursor)
        next_special = None
        for candidate in (directive_match, mermaid_match):
            if candidate and (next_special is None or candidate.start() < next_special.start()):
                next_special = candidate

        if next_special is None:
            remainder = body[cursor:].strip()
            if remainder:
                blocks.append(MarkdownBlock(text=remainder, line=line_at(cursor)))
            break

        if next_special.start() > cursor:
            prose = body[cursor : next_special.start()].strip()
            if prose:
                blocks.append(MarkdownBlock(text=prose, line=line_at(cursor)))

        if next_special is mermaid_match:
            assert mermaid_match is not None
            source = mermaid_match.group(1).strip()
            diagram_id = hashlib.sha256(source.encode()).hexdigest()[:12]
            blocks.append(
                MermaidBlock(
                    source=source,
                    diagram_id=diagram_id,
                    line=line_at(mermaid_match.start()),
                )
            )
            cursor = mermaid_match.end()
        else:
            assert directive_match is not None
            kind = directive_match.group(1)
            body_text = directive_match.group(2)
            blocks.append(parse_directive_block(kind, body_text, line_at(directive_match.start())))
            cursor = directive_match.end()

    metadata = _parse_metadata(raw, source_path)
    return LessonDocument(metadata=metadata, blocks=tuple(blocks), sections=_split_sections(blocks))


def load_lesson(relative_path: str) -> LessonDocument:
    path = resolve_lesson_path(relative_path)
    text = path.read_text(encoding="utf-8")
    return parse_lesson_markdown(text, path)
