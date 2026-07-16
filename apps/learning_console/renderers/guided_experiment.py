"""Progressive Streamlit renderer for the Build Week Guided Experiment."""

from __future__ import annotations

import streamlit as st
from services.build_week_service import GuidedExperimentView, execute_quick_qiskit

from quantum_folk_lab.build_week import LearnerLevel, explain_result

LEVEL_LABELS = {
    "First encounter": LearnerLevel.FIRST_ENCOUNTER,
    "Technical learner": LearnerLevel.TECHNICAL_LEARNER,
    "Research detail": LearnerLevel.RESEARCH_DETAIL,
}


def render_guided_experiment(view: GuidedExperimentView) -> None:
    result = view.result
    st.header("Guided Experiment")
    st.caption("A fixed synthetic music question, solved transparently from evidence to result.")

    st.subheader("1–2 · Meet the fixture and question")
    st.write(result.fixture_description)
    st.info(
        "Can interval, contour, and rhythm similarities separate these eight synthetic tune "
        "variants into two unlabeled families? Labels are hidden until evaluation."
    )

    with st.expander("3 · Inspect the musical evidence"):
        pairs = result.evidence_summary["pairs"]
        st.dataframe(pairs, width="stretch", hide_index=True)
        st.caption(
            "An edge joins a pair when its combined synthetic similarity passes the fixed graph "
            "threshold. This is not authentic cultural data."
        )

    with st.expander("4 · Understand the model"):
        st.write(
            "Each tune receives a 0 or 1. The verified QUBO rewards a coherent, balanced split; "
            "0 and 1 are exchangeable family labels."
        )
        st.json({"parameters": result.parameters, "QUBO summary": result.qubo_summary})

    st.subheader("5–6 · Exact result computed now")
    exact = result.exact_result
    left, middle, right = st.columns(3)
    left.metric("Minimum energy", f"{float(exact['minimum_energy']):.6f}")
    middle.metric("Canonical split", str(exact["canonical_complement_class"]))
    right.metric("Assignments checked", str(exact["evaluated_assignments"]))
    st.success(
        "Exhaustive enumeration is authoritative for this eight-variable fixture. The global "
        "bitwise complement denotes the same unlabeled partition."
    )

    st.subheader("7–8 · Optional local-Qiskit comparison")
    st.write(view.quantum.message)
    if view.quantum.available:
        if st.button("Run bounded local Qiskit (p=1, 256 shots)"):
            with st.spinner("Running the fixed local ideal-simulator experiment…"):
                try:
                    st.session_state["build_week_quantum"] = execute_quick_qiskit()
                except RuntimeError as exc:
                    st.warning(f"The quick run is unavailable: {exc}")
        quantum = st.session_state.get("build_week_quantum")
        if quantum:
            st.markdown("**Quick local-Qiskit result computed now**")
            st.json(quantum)
            st.warning(
                "A best sampled optimum does not prove an optimal expectation, speedup, or "
                "quantum advantage."
            )
    else:
        st.code(view.quantum.install_command)
    with st.expander("Historical registered evidence boundary"):
        st.write(
            "EXP-005A includes separate registered 4,096-shot historical evidence. It is not "
            "loaded or presented as this current quick run."
        )

    st.subheader("9–10 · Explain this result")
    label = st.selectbox("Explanation level", list(LEVEL_LABELS))
    level = LEVEL_LABELS[label]
    explanation = view.explanation(level)
    if st.button("Explain this result with optional GPT-5.6"):
        generated = explain_result(result, level)
        explanation = generated.text
        if generated.fallback_reason:
            st.caption(
                "Using the deterministic explanation because the optional AI path was "
                "unavailable or invalid."
            )
        else:
            st.caption(f"Validated grounded explanation from {generated.model}.")
    st.write(explanation)

    st.subheader("11 · Export a reproducibility record")
    first, second = st.columns(2)
    first.download_button(
        "Download validated JSON",
        view.json_export(),
        "qfl-guided-experiment.json",
        "application/json",
    )
    second.download_button(
        "Download readable Markdown",
        view.markdown_export(level),
        "qfl-guided-experiment.md",
        "text/markdown",
    )

    st.subheader("12 · Limitations")
    for boundary in result.claims_boundary:
        st.write(f"- {boundary}")
