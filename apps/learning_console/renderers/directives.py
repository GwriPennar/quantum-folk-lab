"""Public Foundations visual and interaction adapters."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_visual(visual_id: str) -> None:
    captions = {
        "bit-vs-qubit": "Classical bit: definite 0 or 1. Qubit: amplitudes until measurement.",
        "hadamard-probability-split": "After H on |0⟩, Theory predicts equal P(0) and P(1).",
        "z-phase-reveal": (
            "A Z gate can change phase without changing computational-basis probabilities."
        ),
        "double-h-interference": "H then H can return to |0⟩ because amplitudes interfere.",
        "bell-correlation": "Bell outcomes favour 00 and 11; each bit alone looks random.",
        "circuit-thumbnail": "Circuit sketch placeholder — use EXP-001 for full circuit diagrams.",
        "x-gate-visual": "X gate swaps |0⟩ and |1⟩.",
    }
    st.info(captions.get(visual_id, f"Visual: {visual_id}"))


def render_interaction(interaction_id: str, params: dict[str, Any]) -> None:
    if interaction_id == "x-gate-input":
        state = st.radio(
            "Input state for X gate",
            ["|0⟩", "|1⟩"],
            horizontal=True,
            key="pub-x-input",
        )
        if state == "|0⟩":
            st.write("Before: 0: 100% → After X: 1: 100%")
        else:
            st.write("Before: 1: 100% → After X: 0: 100%")
        return

    if interaction_id == "quantum-prediction":
        st.markdown("**Make a prediction before you run.**")
        prediction = st.radio(
            "Which outcome pattern do you expect after H?",
            ["Roughly 50/50", "Mostly 0", "Mostly 1"],
            key="pub-h-predict",
        )
        if st.button("Run local Aer simulation (optional)", key="pub-h-run"):
            try:
                from services.exp001_optional import run_hadamard

                result = run_hadamard(shots=int(params.get("shots_default", 1024)))
                st.write(result)
                st.caption(f"Prediction recorded: {prediction}")
            except Exception as exc:  # noqa: BLE001
                st.warning(
                    "Optional Qiskit/Aer not available. Install with "
                    '`pip install -e ".[quantum]"` to enable live demos. '
                    f"({type(exc).__name__})"
                )
                st.caption(f"Prediction recorded: {prediction}")
        return

    st.caption(f"Interaction `{interaction_id}` is documented for static export.")
