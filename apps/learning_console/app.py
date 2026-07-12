"""Public Foundations Learning Console (experimental).

Run from the repository root:

    streamlit run apps/learning_console/app.py

Requires optional dependency ``PyYAML`` (``pip install pyyaml``).
Optional Qiskit extras enable live Aer demos for X-gate and Hadamard.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from quantum_folk_lab.learning.glossary import load_glossary
from quantum_folk_lab.learning.registry import load_registry
from renderers.lesson_renderer import render_lesson

st.set_page_config(
    page_title="QFL Learning Console — Foundations",
    page_icon="⚛",
    layout="wide",
)

st.title("Learning Console — Foundations")
st.caption(
    "Public experimental edition. Portable Markdown lessons under `learn/`. "
    "Simulator-first. No claim of quantum advantage."
)

registry = load_registry()
entries = registry.ordered()
labels = [f"{e.order}. {e.title}" for e in entries]
choice = st.sidebar.selectbox("Lesson", labels, index=0)
entry = entries[labels.index(choice)]

tab_lesson, tab_glossary = st.tabs(["Lesson", "Glossary"])

with tab_lesson:
    lesson = registry.load_document(entry.id)
    render_lesson(lesson, registry)

with tab_glossary:
    query = st.text_input("Search glossary", placeholder="e.g. qubit, QAOA, shot")
    terms = load_glossary()
    for term in terms:
        if query and query.lower() not in term.term.lower() and query.lower() not in term.deeper.lower():
            continue
        with st.expander(term.term):
            st.markdown(f"**One sentence:** {term.one_liner}")
            st.markdown(f"**Deeper:** {term.deeper}")
