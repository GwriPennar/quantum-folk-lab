"""Static Markdown and HTML export from portable lesson sources."""

from __future__ import annotations

import html
from pathlib import Path

from quantum_folk_lab.learning.models import (
    DisclosureDirective,
    GlossaryDirective,
    InteractionDirective,
    LessonDocument,
    MarkdownBlock,
    MermaidBlock,
    RegisteredDataDirective,
    VisualDirective,
)
from quantum_folk_lab.learning.registry import LessonRegistry
from quantum_folk_lab.learning.semantic_state import semantic_marker_html


def _render_block_markdown(block) -> str:
    if isinstance(block, MarkdownBlock):
        return block.text
    if isinstance(block, MermaidBlock):
        return f"```mermaid\n{block.source}\n```"
    if isinstance(block, VisualDirective):
        return f"*[Visual: {block.visual_id} — see Learning Console]*"
    if isinstance(block, InteractionDirective):
        return (
            f"> **Interactive in the Learning Console app:** "
            f"{block.interaction_id}"
        )
    if isinstance(block, RegisteredDataDirective):
        return f"*[Registered data: {block.data_id}]*"
    if isinstance(block, DisclosureDirective):
        return f"*[Optional disclosure ({block.level}): {block.label}]*"
    if isinstance(block, GlossaryDirective):
        return "*[Glossary terms — see learn/glossary.yaml]*"
    return ""


def export_lesson_markdown(doc: LessonDocument) -> str:
    parts = [f"# {doc.metadata.title}", f"<!-- lesson-id: {doc.metadata.id} -->"]
    if doc.metadata.learning_objectives:
        parts.append("## Learning objectives")
        parts.extend(f"- {obj}" for obj in doc.metadata.learning_objectives)
    for block in doc.blocks:
        chunk = _render_block_markdown(block)
        if chunk:
            parts.append(chunk)
    if doc.metadata.learned_summary:
        parts.append(f"**Learned:** {doc.metadata.learned_summary}")
    return "\n\n".join(parts) + "\n"


def export_lesson_html(doc: LessonDocument) -> str:
    body_parts = [f"<h1>{html.escape(doc.metadata.title)}</h1>"]
    body_parts.append(semantic_marker_html(doc, renderer="static-html"))
    for block in doc.blocks:
        if isinstance(block, MarkdownBlock):
            text = html.escape(block.text).replace("\n", "<br/>")
            body_parts.append(f"<p>{text}</p>")
        elif isinstance(block, MermaidBlock):
            body_parts.append(f"<pre>{html.escape(block.source)}</pre>")
        elif isinstance(block, VisualDirective):
            body_parts.append(
                f'<p class="visual-callout">Visual: {html.escape(block.visual_id)}</p>'
            )
        elif isinstance(block, InteractionDirective):
            body_parts.append(
                "<p><em>Interactive in Learning Console: "
                f"{html.escape(block.interaction_id)}</em></p>"
            )
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'/>"
        f"<title>{html.escape(doc.metadata.title)}</title>"
        "<style>body{font-family:system-ui;max-width:48rem;margin:2rem auto;line-height:1.5}"
        ".visual-callout{border-left:4px solid #334155;padding-left:1rem}</style>"
        "</head><body>"
        + "".join(body_parts)
        + "</body></html>"
    )


def export_registry_bundle(registry: LessonRegistry, out_dir: Path) -> dict[str, int]:
    md_dir = out_dir / "markdown"
    html_dir = out_dir / "html"
    md_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    counts = {"markdown": 0, "html": 0}
    for entry in registry.ordered():
        doc = registry.load_document(entry.id)
        if not doc.metadata.static_export:
            continue
        slug = entry.id.replace(".", "-")
        (md_dir / f"{slug}.md").write_text(export_lesson_markdown(doc), encoding="utf-8")
        (html_dir / f"{slug}.html").write_text(export_lesson_html(doc), encoding="utf-8")
        counts["markdown"] += 1
        counts["html"] += 1
    return counts
