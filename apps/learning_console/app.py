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

from renderers.guided_experiment import render_guided_experiment  # noqa: E402
from renderers.lesson_renderer import render_lesson  # noqa: E402
from services.build_week_service import load_guided_experiment  # noqa: E402

from quantum_folk_lab.learning.glossary import load_glossary  # noqa: E402
from quantum_folk_lab.learning.registry import load_registry  # noqa: E402

st.set_page_config(
    page_title="QFL Learning Console — Foundations",
    page_icon="⚛",
    layout="wide",
)

st.title("Quantum Folk Lab — Learning Console")
st.caption(
    "Public experimental edition. Portable Markdown lessons under `learn/`. "
    "Simulator-first. No claim of quantum advantage."
)

route = st.sidebar.radio("Explore", ["Guided Experiment", "Foundations", "Glossary"])
registry = load_registry()

if route == "Guided Experiment":
    render_guided_experiment(load_guided_experiment())
elif route == "Foundations":
    st.header("Foundations")
    entries = registry.ordered()
    labels = [f"{e.order}. {e.title}" for e in entries]
    choice = st.selectbox("Lesson", labels, index=0)
    entry = entries[labels.index(choice)]
    lesson = registry.load_document(entry.id)
    render_lesson(lesson, registry)
else:
    st.header("Glossary")
    query = st.text_input("Search glossary", placeholder="e.g. qubit, QAOA, shot")
    terms = load_glossary()
    for term in terms:
        term_hit = query.lower() in term.term.lower() if query else True
        deeper_hit = query.lower() in term.deeper.lower() if query else True
        if query and not term_hit and not deeper_hit:
            continue
        with st.expander(term.term):
            st.markdown(f"**One sentence:** {term.one_liner}")
            st.markdown(f"**Deeper:** {term.deeper}")
