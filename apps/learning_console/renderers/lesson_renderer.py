"""Render a portable LessonDocument in the public Learning Console."""

from __future__ import annotations

import html
import re

import streamlit as st

from quantum_folk_lab.learning.models import (
    DisclosureDirective,
    GlossaryDirective,
    InteractionDirective,
    LessonDocument,
    MarkdownBlock,
    MermaidBlock,
    VisualDirective,
)
from quantum_folk_lab.learning.registry import LessonRegistry
from quantum_folk_lab.learning.semantic_state import semantic_marker_html
from quantum_folk_lab.learning.validation import validate_lesson_document
from renderers.directives import render_interaction, render_visual

FLOWCHART_HEADER_RE = re.compile(r"^flowchart\s+(LR|TB)$")
FLOWCHART_EDGE_RE = re.compile(
    r'^([A-Za-z][A-Za-z0-9_]*)(?:\["([^"]+)"\])?\s*-->\s*'
    r'([A-Za-z][A-Za-z0-9_]*)(?:\["([^"]+)"\])?$'
)


def _flowchart_paths(source: str) -> tuple[str, tuple[tuple[str, ...], ...]] | None:
    """Parse the repository's small, validated Mermaid flowchart subset."""

    lines = [line.strip() for line in source.splitlines() if line.strip()]
    if not lines or not (header := FLOWCHART_HEADER_RE.fullmatch(lines[0])):
        return None
    labels: dict[str, str] = {}
    children: dict[str, list[str]] = {}
    targets: set[str] = set()
    node_order: list[str] = []
    for line in lines[1:]:
        edge = FLOWCHART_EDGE_RE.fullmatch(line)
        if edge is None:
            return None
        source_id, source_label, target_id, target_label = edge.groups()
        for node_id in (source_id, target_id):
            if node_id not in node_order:
                node_order.append(node_id)
        if source_label:
            labels[source_id] = source_label
        if target_label:
            labels[target_id] = target_label
        children.setdefault(source_id, []).append(target_id)
        targets.add(target_id)
    if not node_order or any(node_id not in labels for node_id in node_order):
        return None
    roots = [node_id for node_id in node_order if node_id not in targets]
    if not roots:
        return None
    paths: list[tuple[str, ...]] = []

    def visit(node_id: str, path: tuple[str, ...]) -> bool:
        if node_id in path:
            return False
        next_path = (*path, node_id)
        next_nodes = children.get(node_id, [])
        if not next_nodes:
            paths.append(tuple(labels[item] for item in next_path))
            return True
        return all(visit(child, next_path) for child in next_nodes)

    if not all(visit(root, ()) for root in roots):
        return None
    return header.group(1), tuple(paths)


def _flowchart_html(source: str) -> str | None:
    parsed = _flowchart_paths(source)
    if parsed is None:
        return None
    direction, paths = parsed
    arrow = "→" if direction == "LR" else "↓"
    rows: list[str] = []
    for path in paths:
        parts: list[str] = []
        for index, label in enumerate(path):
            if index:
                parts.append(f'<span aria-hidden="true" style="font-size:1.4rem">{arrow}</span>')
            parts.append(
                '<span style="border:1px solid rgba(128,128,128,.55);border-radius:.5rem;'
                'padding:.55rem .75rem;background:rgba(128,128,128,.10);text-align:center">'
                f"{html.escape(label)}</span>"
            )
        flex_direction = "row" if direction == "LR" else "column"
        rows.append(
            f'<div style="display:flex;flex-direction:{flex_direction};align-items:center;'
            f'justify-content:center;gap:.55rem;flex-wrap:wrap">{"".join(parts)}</div>'
        )
    return (
        '<div role="img" aria-label="Concept flow diagram" style="display:grid;gap:.7rem;'
        'padding:.85rem;border:1px solid rgba(128,128,128,.3);border-radius:.6rem">'
        f"{''.join(rows)}</div>"
    )


def render_lesson(lesson: LessonDocument, registry: LessonRegistry) -> None:
    errors = validate_lesson_document(lesson, registry)
    if errors:
        st.warning("Validation notes:\n" + "\n".join(f"- {e}" for e in errors))

    if lesson.metadata.learning_objectives:
        st.write(f"**Why this matters here:** {lesson.metadata.learning_objectives[0]}")
    st.markdown(semantic_marker_html(lesson, renderer="streamlit"), unsafe_allow_html=True)

    if lesson.metadata.learning_objectives:
        with st.expander("Learning objectives"):
            for obj in lesson.metadata.learning_objectives:
                st.markdown(f"- {obj}")

    for block in lesson.blocks:
        if isinstance(block, MarkdownBlock):
            st.markdown(block.text)
        elif isinstance(block, MermaidBlock):
            rendered_flowchart = _flowchart_html(block.source)
            if rendered_flowchart is None:
                st.warning("This concept diagram could not be rendered safely.")
            else:
                st.markdown(rendered_flowchart, unsafe_allow_html=True)
            with st.expander("View diagram source"):
                st.code(block.source, language="text")
        elif isinstance(block, VisualDirective):
            render_visual(block.visual_id)
        elif isinstance(block, InteractionDirective):
            render_interaction(block.interaction_id, block.params)
        elif isinstance(block, DisclosureDirective):
            # Disclosure directives currently carry metadata but no associated body.
            # Rendering nothing is safer than presenting an empty interactive control.
            pass
        elif isinstance(block, GlossaryDirective):
            st.info("Open the Glossary tab for portable definitions.")

    nxt = registry.next_entry(lesson.metadata.id)
    if nxt:
        st.info(f"Suggested next: **{nxt.title}**")
