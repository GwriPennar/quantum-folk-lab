"""Progressive Streamlit renderer for the Build Week Guided Experiment."""

from __future__ import annotations

import streamlit as st
from services.build_week_service import (
    VARIANT_DISPLAY_NAMES,
    GuidedExperimentView,
    PartitionView,
    execute_quick_qiskit,
    partition_from_indices,
    partitions_are_equivalent,
    summarise_quick_qiskit,
)

from quantum_folk_lab.build_week import LearnerLevel, explain_result

LEVEL_LABELS = {
    "First encounter": LearnerLevel.FIRST_ENCOUNTER,
    "Technical learner": LearnerLevel.TECHNICAL_LEARNER,
    "Research detail": LearnerLevel.RESEARCH_DETAIL,
}


def _evidence_identity(label: str, icon: str, authority: str) -> None:
    with st.container(border=True):
        st.markdown(f"### {icon} {label}")
        st.caption(authority)


def _display_evidence_pairs(view: GuidedExperimentView) -> list[dict[str, object]]:
    display_by_id = dict(zip(view.result.tune_ordering, VARIANT_DISPLAY_NAMES, strict=True))
    return [
        {
            "left variant": display_by_id[str(pair["left_tune"])],
            "right variant": display_by_id[str(pair["right_tune"])],
            "interval similarity": pair["interval_similarity"],
            "contour similarity": pair["contour_similarity"],
            "rhythm similarity": pair["rhythm_similarity"],
            "combined similarity": pair["combined_similarity"],
        }
        for pair in view.result.evidence_summary["pairs"]
    ]


def _render_partition(title: str, partition: PartitionView) -> None:
    st.markdown(f"**{title}**")
    left, right = st.columns(2)
    left.markdown("**One family**")
    left.write("\n".join(f"- {name}" for name in partition.first_group))
    right.markdown("**The complementary family**")
    right.write("\n".join(f"- {name}" for name in partition.second_group))


def _render_exit_check() -> None:
    st.subheader("Check what you now understand")
    st.write("Five short questions connect the exact answer, quantum evidence and AI boundary.")
    questions = (
        (
            "Why are there 256 possible groupings?",
            (
                "Eight independent binary choices give 2⁸ possibilities.",
                "The circuit uses 256 qubits.",
                "There are 256 tune recordings.",
            ),
            0,
            "Eight yes-or-no assignments create 2 × 2 × 2 × 2 × 2 × 2 × 2 × 2 = 256 states.",
        ),
        (
            "Why is exact classical calculation still the reference?",
            (
                "It evaluates every possible answer for this small problem.",
                "Classical computers are always faster.",
                "It removes all modelling choices.",
            ),
            0,
            "Complete enumeration checks the full finite answer space, so sampled methods can "
            "be judged against it.",
        ),
        (
            "Why does a quantum method return a distribution?",
            (
                "Each shot measures one outcome, so repeated shots accumulate counts.",
                "The answer changes culturally.",
                "The exact result is unknown.",
            ),
            0,
            "A circuit measurement yields one bitstring per shot; many shots estimate its "
            "outcome probabilities.",
        ),
        (
            "What is hardware noise?",
            (
                "Errors and disturbances in physical qubits, gates and measurements.",
                "Background music in the laboratory.",
                "A deliberate change to the exact score.",
            ),
            0,
            "Noise is the collective effect of physical imperfections; one disagreement does "
            "not identify a single cause.",
        ),
        (
            "What may GPT‑5.6 do here?",
            (
                "Explain a validated evidence packet without changing it.",
                "Calculate the exact optimum.",
                "Authorise new hardware jobs.",
            ),
            0,
            "GPT‑5.6 is an optional explanation layer; validation fails closed to "
            "deterministic text.",
        ),
    )
    with st.form("guided-exit-check"):
        answers = [
            st.radio(prompt, options, index=None, key=f"guided-exit-{index}")
            for index, (prompt, options, _, _) in enumerate(questions)
        ]
        submitted = st.form_submit_button("Check my answers")
    if submitted:
        st.session_state["guided_exit_submitted"] = True
    if st.session_state.get("guided_exit_submitted"):
        score = sum(
            answer == options[correct]
            for answer, (_, options, correct, _) in zip(answers, questions, strict=True)
        )
        st.success(f"You answered {score} of 5 correctly.")
        for answer, (prompt, options, correct, explanation) in zip(answers, questions, strict=True):
            status = "Correct" if answer == options[correct] else "Review"
            st.markdown(f"**{status} — {prompt}**  \n{explanation}")
        if st.button("Try the exit check again"):
            st.session_state["guided_exit_submitted"] = False
            st.rerun()
    st.info(
        "Quantum computers are a different way to process a scored problem, not magic. For this "
        "small experiment, exact classical calculation supplies the truth. Simulation and hardware "
        "can then be compared with it. The evidence is educational—not a claim of quantum "
        "advantage."
    )


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
                    "legend": {"title": "Exact energy (lower = better)"},
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
    _evidence_identity(
        "IDEAL OR REGISTERED SIMULATION",
        "◫",
        "Committed simulated measurement evidence; not physical hardware.",
    )
    st.subheader("What does the quantum method actually do?")
    st.write(
        "A quantum computer does not print one authoritative answer. The circuit is prepared "
        "and measured once — one shot — and that measurement returns one candidate grouping. "
        "Repeating this thousands of times creates a distribution of answers. A useful "
        "optimisation method should place more measurement weight on better-scoring groupings. "
        "The exact calculation above remains the authority used to judge it."
    )
    st.markdown("### What did 4,096 shots actually return?")
    measurement_rows = [item.chart_row() for item in view.registered_measurements]
    measurement_order = [item["bitstring"] for item in measurement_rows]
    st.vega_lite_chart(
        measurement_rows,
        {
            "height": 320,
            "layer": [
                {
                    "mark": {"type": "bar"},
                    "encoding": {
                        "y": {
                            "field": "bitstring",
                            "type": "nominal",
                            "sort": measurement_order,
                            "title": "Returned grouping",
                        },
                        "x": {
                            "field": "count",
                            "type": "quantitative",
                            "title": "Registered measurement count",
                        },
                        "color": {
                            "field": "status",
                            "type": "nominal",
                            "scale": {
                                "domain": ["Exact optimum", "Other grouping"],
                                "range": ["#2a9d8f", "#6c83a6"],
                            },
                            "legend": None,
                        },
                        "tooltip": [
                            {"field": "bitstring", "type": "nominal", "title": "Grouping"},
                            {"field": "count", "type": "quantitative", "title": "Count"},
                            {"field": "status", "type": "nominal", "title": "Exact check"},
                        ],
                    },
                },
                {
                    "mark": {
                        "type": "text",
                        "align": "left",
                        "dx": 6,
                        "color": "#ffffff",
                        "fontWeight": "bold",
                    },
                    "encoding": {
                        "y": {
                            "field": "bitstring",
                            "type": "nominal",
                            "sort": measurement_order,
                        },
                        "x": {"field": "zero", "type": "quantitative"},
                        "text": {"field": "optimum_note"},
                    },
                },
                {
                    "mark": {"type": "text", "align": "left", "dx": 5, "color": "#ffffff"},
                    "encoding": {
                        "y": {
                            "field": "bitstring",
                            "type": "nominal",
                            "sort": measurement_order,
                        },
                        "x": {"field": "count", "type": "quantitative"},
                        "text": {"field": "count", "type": "quantitative"},
                    },
                },
            ],
        },
        width="stretch",
    )
    st.caption(
        "Each bar is one answer returned by the registered ideal simulation. These are the ten "
        f"most frequent states, not all {view.registered_distinct_state_count} observed states. "
        "Exact-optimum states are labelled so the simulated measurements can be checked against "
        "the known answer. This is registered simulation evidence, not IBM hardware."
    )
    st.write(
        "Many different groupings appeared, but the measurement weight was uneven. The next "
        "comparison checks how much of it landed on the two known best groupings."
    )
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
    _evidence_identity(
        "GPT‑5.6 EXPLANATION",
        "◇",
        "Explains a validated packet; does not calculate or change the result.",
    )
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
        "Before revealing the answer, inspect the musical evidence and record which four variants "
        "you think belong together. Choosing one family automatically defines the other."
    )

    with st.expander("Look at the musical evidence"):
        st.write(
            "Look for pairs with strong combined similarity. Connected pairs are clues that two "
            "variants may belong to the same hidden family. This is synthetic teaching material, "
            "not authentic cultural material."
        )
        pairs = _display_evidence_pairs(view)
        st.dataframe(pairs, width="stretch", hide_index=True)
        st.caption(
            "An edge joins a pair when its combined synthetic similarity passes the fixed graph "
            "threshold. This is not authentic cultural data."
        )

    st.markdown("### Make and record your prediction")
    selected_names = st.multiselect(
        "Choose exactly four variants for one family",
        VARIANT_DISPLAY_NAMES,
        default=[
            VARIANT_DISPLAY_NAMES[index]
            for index in st.session_state.get("build_week_prediction_indices", ())
        ],
        help="The other four variants automatically form the complementary family.",
    )
    selected_indices = tuple(
        index for index, name in enumerate(VARIANT_DISPLAY_NAMES) if name in selected_names
    )
    if len(selected_indices) == 4:
        prediction = partition_from_indices(selected_indices)
        st.session_state["build_week_prediction_indices"] = selected_indices
        _render_partition("Your recorded prediction", prediction)
        st.caption("You can revise this split until Reveal. No score or answer is shown yet.")
    elif selected_names:
        st.session_state.pop("build_week_prediction_indices", None)
        st.warning(f"Choose exactly four variants. You currently selected {len(selected_names)}.")
    else:
        st.session_state.pop("build_week_prediction_indices", None)
        st.caption("You may skip the prediction and still reveal the governed evidence.")

    if st.button("Reveal all 256 answers", type="primary"):
        st.session_state["build_week_256_revealed"] = True
    if not st.session_state.get("build_week_256_revealed", False):
        st.caption("The answer stays hidden until you reveal it.")
        return

    st.subheader("What did every possible grouping score?")
    st.write(
        "Each of the eight variants can join either family, so there are "
        "2 × 2 × 2 × 2 × 2 × 2 × 2 × 2 = 256 possible groupings."
    )
    st.info(
        "Energy is this model's score for one possible grouping. Lower energy means a better "
        "answer. The outlined cells mark the exact best groupings."
    )
    _render_landscape(view)

    st.subheader("What is the exact answer?")
    _evidence_identity(
        "EXACT CLASSICAL REFERENCE",
        "✓",
        "Complete enumeration supplies the answer used to judge every quantum result.",
    )
    st.write("This answer is not a prediction — the computer tried every possibility.")
    exact = result.exact_result
    left, middle, right = st.columns(3)
    left.metric("Minimum energy", f"{float(exact['minimum_energy']):.6f}")
    middle.metric("Canonical split", str(exact["canonical_complement_class"]))
    right.metric("Assignments checked", str(exact["evaluated_assignments"]))
    st.write(
        "`00001111` has one digit for each tune variant. A `0` places that variant in one "
        "family and a `1` places it in the other. `11110000` describes the same split with the "
        "family labels exchanged."
    )
    st.success(
        "Exhaustive enumeration is authoritative for this eight-variable fixture. The global "
        "bitwise complement denotes the same unlabeled partition."
    )
    exact_partition = partition_from_indices(
        tuple(
            index
            for index, bit in enumerate(str(exact["canonical_complement_class"]))
            if bit == "1"
        )
    )
    _render_partition("Exact split in named variants", exact_partition)
    st.caption(
        "The displayed names follow bit positions from left to right. Family labels are "
        "exchangeable and carry no inherent musical or cultural meaning."
    )
    recorded_indices = st.session_state.get("build_week_prediction_indices")
    if recorded_indices is None:
        st.info("You skipped the prediction step. The exact journey remains complete.")
    else:
        learner_partition = partition_from_indices(tuple(recorded_indices))
        _render_partition("Your prediction", learner_partition)
        if partitions_are_equivalent(
            learner_partition.bitstring, str(exact["canonical_complement_class"])
        ):
            st.success(
                "Your prediction found the exact split—even if its family labels are swapped."
            )
        else:
            entry = next(
                item
                for item in view.landscape.entries
                if item.assignment == learner_partition.bitstring
            )
            st.info(
                "Your split was a valid candidate rather than the exact minimum. Its governed "
                f"energy was {entry.display_energy:.6f}. Comparing predictions is part of the "
                "lesson."
            )
        st.caption(
            "Your family labels can be swapped, so we compare the split itself—not whether you "
            "called a group A or B."
        )

    st.subheader("How was the question turned into a model?")
    st.write(
        "To hand this question to a quantum method, it is rewritten in three steps. First, "
        "each tune variant becomes a 0-or-1 choice. Second, any complete set of eight choices — "
        "such as `00001111` — is one possible answer. Third, a score called energy says how "
        "good that answer is; lower is better. The quantum circuit is built from that scored "
        "problem."
    )
    with st.expander("Technical model and QUBO"):
        st.write(result.fixture_description)
        st.write(
            "Each tune receives a 0 or 1. The verified QUBO rewards a coherent, balanced split; "
            "0 and 1 are exchangeable family labels."
        )
        st.json({"parameters": result.parameters, "QUBO summary": result.qubo_summary})

    st.info(
        "Because the exact answer is known, every quantum result below can be checked rather "
        "than taken on trust."
    )
    _render_registered_comparison(view)

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
            st.markdown("**OPTIONAL LOCAL SIMULATION · computed on this machine**")
            try:
                summary = summarise_quick_qiskit(quantum)
            except (TypeError, ValueError) as exc:
                st.warning(f"The local run completed but its display summary was invalid: {exc}")
            else:
                first, second, third = st.columns(3)
                first.metric("Total shots", f"{summary.shots:,}")
                second.metric("Distinct states", str(summary.distinct_states))
                third.metric("Most frequent state", summary.most_frequent_state)
                st.write(
                    "The most frequent state was "
                    f"{'an' if summary.most_frequent_is_optimum else 'not an'} "
                    "exact optimum. Across both exact optima, "
                    f"{summary.optimum_count:,} measurements "
                    f"({summary.optimum_probability:.2%}) landed "
                    "on the known answer class."
                )
                rows = [item.chart_row() for item in summary.top_states]
                st.bar_chart(rows, x="bitstring", y="count")
                st.caption("This optional local ideal simulation is not registered IBM hardware.")
                st.warning(
                    "A best sampled optimum does not prove an optimal expectation, speedup, or "
                    "quantum advantage."
                )
            with st.expander("View technical run data"):
                st.json(quantum)
    else:
        st.info(
            "Qiskit is optional. The registered exact, simulated and recorded-hardware journey "
            "above remains complete without it."
        )
        with st.expander("Optional installation command"):
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

    _render_exit_check()

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
