"""Public Foundations visual and interaction adapters."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_visual(visual_id: str) -> None:
    if visual_id == "bit-vs-qubit":
        probability = st.slider(
            "Chance of measuring 1",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            key="foundations-qubit-probability",
            help="The state also has phase information, which this probability view cannot show.",
        )
        st.bar_chart(
            {"Measured outcome": ["0", "1"], "Probability": [100 - probability, probability]},
            x="Measured outcome",
            y="Probability",
            horizontal=True,
        )
        st.caption(
            "Takeaway: amplitudes determine measurement probabilities, while phase affects how "
            "later operations interfere. A qubit is not simply ‘both values at once’."
        )
        return
    if visual_id == "hadamard-probability-split":
        shots = st.select_slider(
            "Illustrated shot count",
            options=[8, 32, 128, 512],
            value=32,
            key="foundations-shot-count",
        )
        zero_count = shots // 2
        rows = [
            {"Outcome": "0", "Count": zero_count},
            {"Outcome": "1", "Count": shots - zero_count},
        ]
        st.bar_chart(rows, x="Outcome", y="Count", horizontal=True)
        st.caption(
            "Takeaway: each shot produces one bit; repeated shots build an estimated distribution."
        )
        return
    if visual_id == "ideal-vs-noisy":
        noise = st.slider(
            "Illustrative hardware noise",
            min_value=0,
            max_value=20,
            value=8,
            step=2,
            key="foundations-noise-level",
            help="A teaching illustration, not a model of a particular device.",
        )
        rows = [
            {"Evidence": "Ideal simulator", "Expected answer": 80, "Other answers": 20},
            {
                "Evidence": "Illustrative hardware",
                "Expected answer": 80 - noise,
                "Other answers": 20 + noise,
            },
        ]
        st.bar_chart(rows, x="Evidence", y=["Expected answer", "Other answers"])
        st.caption(
            "Takeaway: noise can blur a distribution, so hardware is compared with an exact "
            "reference rather than treated as truth by itself."
        )
        return
    if visual_id == "z-phase-reveal":
        st.markdown("**Same immediate probabilities:** 50% `0`, 50% `1`  ")
        st.markdown(
            "**Different relative phase:** later gates can make the amplitudes add or cancel."
        )
        st.caption("Takeaway: probability alone does not describe phase or interference.")
        return
    if visual_id == "double-h-interference":
        st.bar_chart(
            {"Measured outcome": ["0", "1"], "Probability": [100, 0]},
            x="Measured outcome",
            y="Probability",
            horizontal=True,
        )
        st.caption(
            "Takeaway: two Hadamard gates can interfere back to the definite starting state."
        )
        return
    if visual_id == "bell-correlation":
        st.bar_chart(
            {"Joint outcome": ["00", "01", "10", "11"], "Probability": [50, 0, 0, 50]},
            x="Joint outcome",
            y="Probability",
        )
        st.caption("Takeaway: the pair is correlated even though either result alone is uncertain.")
        return
    if visual_id == "x-gate-visual":
        st.bar_chart(
            {"Input": ["0", "1"], "After X": [1, 0]},
            x="Input",
            y="After X",
        )
        st.caption("Takeaway: X swaps the computational-basis states 0 and 1.")
        return
    captions = {
        "circuit-thumbnail": "Circuit journey: prepare → apply a gate → measure → record one bit.",
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
