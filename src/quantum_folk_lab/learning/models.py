"""Typed portable lesson content models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class LessonMode(StrEnum):
    GUIDED = "guided"
    RESEARCHER = "researcher"


class LessonStatus(StrEnum):
    PILOT = "pilot"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class BlockKind(StrEnum):
    MARKDOWN = "markdown"
    MERMAID = "mermaid"
    VISUAL = "visual"
    INTERACTION = "interaction"
    REGISTERED_DATA = "registered_data"
    DISCLOSURE = "disclosure"
    GLOSSARY = "glossary"


@dataclass(frozen=True)
class SemanticContract:
    required_markers: tuple[str, ...] = ()
    forbidden_markers: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompletionRule:
    type: str
    legacy_key: str | None = None


@dataclass(frozen=True)
class LessonMetadata:
    id: str
    version: int
    title: str
    mode: LessonMode
    section: str
    order: int
    route: str
    status: LessonStatus
    estimated_minutes: int | None = None
    visuals: tuple[str, ...] = ()
    interactions: tuple[str, ...] = ()
    glossary_terms: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()
    next_lesson: str | None = None
    learning_objectives: tuple[str, ...] = ()
    check_question: str = ""
    learned_summary: str = ""
    lab_link: str | None = None
    foundations_nav: bool = False
    static_export: bool = True
    completion: CompletionRule | None = None
    semantic: SemanticContract = field(default_factory=SemanticContract)
    legacy_progress_key: str | None = None
    source_path: str | None = None


@dataclass(frozen=True)
class MarkdownBlock:
    kind: BlockKind = BlockKind.MARKDOWN
    text: str = ""
    line: int = 0


@dataclass(frozen=True)
class MermaidBlock:
    source: str
    diagram_id: str
    line: int = 0
    kind: BlockKind = BlockKind.MERMAID


@dataclass(frozen=True)
class VisualDirective:
    visual_id: str
    line: int = 0
    kind: BlockKind = BlockKind.VISUAL


@dataclass(frozen=True)
class InteractionDirective:
    interaction_id: str
    params: dict[str, Any] = field(default_factory=dict)
    line: int = 0
    kind: BlockKind = BlockKind.INTERACTION


@dataclass(frozen=True)
class RegisteredDataDirective:
    data_id: str
    source: str
    view: str
    line: int = 0
    kind: BlockKind = BlockKind.REGISTERED_DATA


@dataclass(frozen=True)
class DisclosureDirective:
    disclosure_id: str
    label: str
    level: str
    body: str = ""
    line: int = 0
    kind: BlockKind = BlockKind.DISCLOSURE


@dataclass(frozen=True)
class GlossaryDirective:
    scope: str = "foundations"
    line: int = 0
    kind: BlockKind = BlockKind.GLOSSARY


LessonBlock = (
    MarkdownBlock
    | MermaidBlock
    | VisualDirective
    | InteractionDirective
    | RegisteredDataDirective
    | DisclosureDirective
    | GlossaryDirective
)


@dataclass(frozen=True)
class LessonSection:
    heading: str | None
    blocks: tuple[LessonBlock, ...]


@dataclass(frozen=True)
class LessonDocument:
    metadata: LessonMetadata
    sections: tuple[LessonSection, ...]
    blocks: tuple[LessonBlock, ...]

    def all_markdown_text(self) -> str:
        parts: list[str] = [self.metadata.title]
        for block in self.blocks:
            if isinstance(block, MarkdownBlock):
                parts.append(block.text)
        return "\n".join(parts)
