"""Render a portable LessonDocument in the public Learning Console."""

from __future__ import annotations

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


def render_lesson(lesson: LessonDocument, registry: LessonRegistry) -> None:
    errors = validate_lesson_document(lesson, registry)
    if errors:
        st.warning("Validation notes:\n" + "\n".join(f"- {e}" for e in errors))

    st.subheader(lesson.metadata.title)
    st.caption(f"Route `{lesson.metadata.route}` · content v{lesson.metadata.version}")
    st.markdown(semantic_marker_html(lesson, renderer="streamlit"), unsafe_allow_html=True)

    if lesson.metadata.learning_objectives:
        with st.expander("Learning objectives"):
            for obj in lesson.metadata.learning_objectives:
                st.markdown(f"- {obj}")

    for block in lesson.blocks:
        if isinstance(block, MarkdownBlock):
            st.markdown(block.text)
        elif isinstance(block, MermaidBlock):
            st.code(block.source, language="text")
            st.caption(f"Diagram `{block.diagram_id}` (Mermaid source; see dev/learning/MERMAID-POLICY.md)")
        elif isinstance(block, VisualDirective):
            render_visual(block.visual_id)
        elif isinstance(block, InteractionDirective):
            render_interaction(block.interaction_id, block.params)
        elif isinstance(block, DisclosureDirective):
            with st.expander(block.label):
                st.caption("Optional detail — keep plain language first.")
        elif isinstance(block, GlossaryDirective):
            st.info("Open the Glossary tab for portable definitions.")

    nxt = registry.next_entry(lesson.metadata.id)
    if nxt:
        st.info(f"Suggested next: **{nxt.title}**")
