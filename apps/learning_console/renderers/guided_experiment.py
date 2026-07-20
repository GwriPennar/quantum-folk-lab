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


def _render_landscape(view: GuidedExperimentView) -> None:
    landscape = view.landscape
    rows = landscape.chart_rows()
    order = [f"{value:04b}" for value in range(16)]
    tooltips = [
        {"field": "assignment", "type": "nominal", "title": "Assignment"},
        {"field": "integer_index", "type": "quantitative", "title": "Integer index"},
        {
            "field": "display_energy",
            "type": "quantitative",
            "title": "Exact energy",
            "format": ".6f",
        },
        {"field": "energy_rank", "type": "quantitative", "title": "Energy rank"},
        {"field": "hamming_weight", "type": "quantitative", "title": "Hamming weight"},
        {"field": "is_global_optimum", "type": "nominal", "title": "Global optimum"},
        {
            "field": "is_canonical_representative",
            "type": "nominal",
            "title": "Canonical",
        },
        {"field": "complement", "type": "nominal", "title": "Complement"},
    ]
    st.vega_lite_chart(
        rows,
        {
            "height": 520,
            "mark": {"type": "rect"},
            "encoding": {
                "x": {
                    "field": "column_bits",
                    "type": "ordinal",
                    "sort": order,
                    "axis": {"title": "Low four bits (binary index layout)"},
                },
                "y": {
                    "field": "row_bits",
                    "type": "ordinal",
                    "sort": order,
                    "axis": {"title": "High four bits (binary index layout)"},
                },
                "color": {
                    "field": "display_energy",
                    "type": "quantitative",
                    "scale": {"scheme": "viridis", "reverse": True},
                    "legend": {"title": "Exact energy"},
                },
                "stroke": {
                    "condition": {"test": "datum.is_global_optimum", "value": "white"},
                    "value": "transparent",
                },
                "strokeWidth": {
                    "condition": {"test": "datum.is_global_optimum", "value": 4},
                    "value": 0,
                },
                "tooltip": tooltips,
            },
            "config": {"view": {"stroke": None}},
        },
        width="stretch",
    )
    st.caption(
        "Grid mapping: row = high four bits; column = low four bits. Adjacency is only binary "
        "index layout and has no musical meaning. The two outlined cells are global optima: "
        "top-right is the Canonical representative; bottom-left is the Equivalent complement."
    )
    st.success(
        "You just checked every possible answer. The outlined cells are the best groupings — "
        "not a prediction, but the exact result."
    )
    left, middle, right = st.columns(3)
    left.metric("Assignments checked", str(len(landscape.entries)))
    middle.metric("Distinct energy levels", str(landscape.distinct_energy_levels))
    right.metric("Gap to next best", f"{landscape.optimum_to_next_gap:.6f}")
    st.success(
        "Because the problem is deliberately small, the app does not ask the learner to trust "
        "a prediction. It evaluates every possible assignment and establishes the complete "
        "answer space first."
    )
    st.markdown(
        f"**Canonical representative:** `{landscape.canonical_representative}`  \n"
        f"**Equivalent complement:** `{landscape.global_optima[1]}`"
    )
    with st.expander("Accessible table of all 256 assignments"):
        st.dataframe(rows, width="stretch", hide_index=True)


def _render_registered_comparison(view: GuidedExperimentView) -> None:
    evidence = view.registered_qaoa
    st.subheader("How did the quantum method do?")
    st.markdown(
        "**Registered evidence · Local ideal simulation · Not quantum hardware · "
        "No quantum advantage claimed**"
    )
    st.write(
        "The bounded quantum method found one of the best answers far more often than random "
        "guessing."
    )
    exact_column, qaoa_column, random_column = st.columns(3)
    exact_column.metric("Exact enumeration", "256 / 256 checked")
    exact_column.caption("Authoritative answer space — not a sampling probability.")
    qaoa_column.metric("Registered optimum-class mass", f"{evidence.optimum_class_probability:.2%}")
    qaoa_column.caption(
        f"{evidence.optimum_class_count:,} / {evidence.shots:,} samples across both optima."
    )
    random_column.metric(
        "Uniform random baseline", f"{evidence.uniform_optimum_class_probability:.5%}"
    )
    random_column.caption("Two optima among 256 assignments.")
    comparison = [
        {
            "method": "Registered p=1 QAOA",
            "probability": evidence.optimum_class_probability,
            "label": f"{evidence.optimum_class_probability:.2%}",
        },
        {
            "method": "Uniform random",
            "probability": evidence.uniform_optimum_class_probability,
            "label": f"{evidence.uniform_optimum_class_probability:.5%}",
        },
    ]
    st.vega_lite_chart(
        comparison,
        {
            "height": 190,
            "layer": [
                {
                    "mark": {"type": "bar"},
                    "encoding": {
                        "y": {"field": "method", "type": "nominal", "sort": None, "title": None},
                        "x": {
                            "field": "probability",
                            "type": "quantitative",
                            "axis": {
                                "title": "Probability mass across both exact optima",
                                "format": ".0%",
                            },
                        },
                        "color": {"field": "method", "type": "nominal", "legend": None},
                        "tooltip": [
                            {"field": "method", "type": "nominal"},
                            {"field": "probability", "type": "quantitative", "format": ".6%"},
                        ],
                    },
                },
                {
                    "mark": {"type": "text", "align": "left", "dx": 6},
                    "encoding": {
                        "y": {"field": "method", "type": "nominal", "sort": None},
                        "x": {"field": "probability", "type": "quantitative"},
                        "text": {"field": "label"},
                    },
                },
            ],
        },
        width="stretch",
    )
    st.info(
        "53.10% is the total registered sample mass across both complement-equivalent global "
        "optima. It is not the probability of the canonical representative alone and is not "
        "the current 256-shot quick run."
    )
    with st.expander("Registered experiment contract"):
        st.json(
            {
                "experiment": evidence.experiment_identifier,
                "depth": f"p={evidence.depth}",
                "shots": evidence.shots,
                "optimiser": evidence.optimiser,
                "optimiser maximum iterations": evidence.optimiser_max_iterations,
                "fixed initial points": evidence.initial_point_count,
                "sampler / estimator / transpiler seeds": evidence.sampler_seed,
                "00001111": {
                    "count": evidence.canonical_count,
                    "probability": evidence.canonical_probability,
                },
                "11110000": {
                    "count": evidence.complement_count,
                    "probability": evidence.complement_probability,
                },
            }
        )


def _render_evidence_hierarchy() -> None:
    st.markdown(
        "**Exact enumeration**  \n"
        "↓ governs  \n"
        "**Qiskit heuristic comparison**  \n"
        "↓ interpreted through  \n"
        "**Validated GPT-5.6 explanation**"
    )
    st.info("GPT-5.6 may explain the validated result. It may not change the evidence.")
    st.caption("The AI can explain the experiment. It cannot rewrite the evidence.")
    st.write(
        "GPT-5.6 receives validated evidence; it does not calculate the objective, choose the "
        "optimum, or change registered values. Schema, grounding, numerical and claim checks "
        "apply. Invalid or unavailable output fails closed to the deterministic explanation, "
        "so the scientific result is identical without OpenAI access."
    )
    st.caption(
        "Codex helped implement and test this Build Week release under human-defined "
        "scientific contracts."
    )


def render_guided_experiment(view: GuidedExperimentView) -> None:
    result = view.result
    st.header("Can you spot the hidden split?")
    st.markdown(
        "**Eight tune variants. Two hidden families. 256 possible groupings.**\n\n"
        "Before revealing the answer, inspect the musical evidence and decide which variants "
        "you think belong together. You do not need to enter a formal answer — make a mental "
        "prediction, then test it."
    )

    with st.expander("Look at the musical evidence"):
        st.write(
            "Look for pairs with strong combined similarity. Connected pairs are clues that two "
            "variants may belong to the same hidden family. This is synthetic teaching material, "
            "not authentic cultural material."
        )
        pairs = result.evidence_summary["pairs"]
        st.dataframe(pairs, width="stretch", hide_index=True)
        st.caption(
            "An edge joins a pair when its combined synthetic similarity passes the fixed graph "
            "threshold. This is not authentic cultural data."
        )

    if st.button("Reveal all 256 answers", type="primary"):
        st.session_state["build_week_256_revealed"] = True
    if not st.session_state.get("build_week_256_revealed", False):
        st.caption("The answer stays hidden until you reveal it.")
        return

    st.subheader("What did every possible grouping score?")
    _render_landscape(view)

    st.subheader("What is the exact answer?")
    st.write("This answer is not a prediction — the computer tried every possibility.")
    exact = result.exact_result
    left, middle, right = st.columns(3)
    left.metric("Minimum energy", f"{float(exact['minimum_energy']):.6f}")
    middle.metric("Canonical split", str(exact["canonical_complement_class"]))
    right.metric("Assignments checked", str(exact["evaluated_assignments"]))
    st.success(
        "Exhaustive enumeration is authoritative for this eight-variable fixture. The global "
        "bitwise complement denotes the same unlabeled partition."
    )

    st.info(
        "Because the exact answer is known, every quantum result below can be checked rather "
        "than taken on trust."
    )
    _render_registered_comparison(view)

    st.subheader("How was the question turned into a model?")
    with st.expander("Technical model and QUBO"):
        st.write(result.fixture_description)
        st.write(
            "Each tune receives a 0 or 1. The verified QUBO rewards a coherent, balanced split; "
            "0 and 1 are exchangeable family labels."
        )
        st.json({"parameters": result.parameters, "QUBO summary": result.qubo_summary})

    st.subheader("Want to run a small local quantum comparison?")
    st.caption(
        "This live bounded quick run uses a smaller submission-safe contract. It is separate "
        "from the registered 4,096-shot evidence shown above."
    )
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
    st.subheader("Can AI explain the result safely?")
    _render_evidence_hierarchy()
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

    st.subheader("Want to inspect or share the reproducibility record?")
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

    st.subheader("Limitations")
    for boundary in result.claims_boundary:
        st.write(f"- {boundary}")
