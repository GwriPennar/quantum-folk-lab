from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from quantum_folk_lab.learning.registry import load_registry


def test_navigation_hierarchy_and_no_secret_display() -> None:
    app = Path("apps/learning_console/app.py").read_text(encoding="utf-8")
    assert '["Experiments", "Foundations", "Glossary"]' in app
    assert "Start here · Guided experiment" in app
    assert "Real folk data & IBM results" in app
    assert "Experiment archive" not in app
    assert "st.sidebar.radio" not in app
    assert "st.sidebar.selectbox" not in app
    assert 'st.selectbox("Lesson"' not in app
    renderer = Path("apps/learning_console/renderers/guided_experiment.py").read_text(
        encoding="utf-8"
    )
    assert "OPENAI_" + "API" + "_KEY" not in renderer
    assert "Can you spot the hidden split?" in renderer


def test_service_loads_without_streamlit_qiskit_or_openai_imports() -> None:
    path = Path("apps/learning_console/services/build_week_service.py")
    spec = importlib.util.spec_from_file_location("build_week_service_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    view = module.load_guided_experiment()
    assert view.result.exact_result["canonical_complement_class"] == "00001111"
    assert len(view.landscape.entries) == 256
    assert view.registered_qaoa.optimum_class_count == 2175
    assert view.json_export().startswith(b"{")


def test_guided_experiment_256_reveal_journey_requires_no_openai_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_" + "API" + "_KEY", raising=False)
    app = AppTest.from_file("apps/learning_console/app.py")
    app.run(timeout=30)
    assert not app.exception
    assert len(app.sidebar) == 0
    labels = [tab.label for tab in app.tabs]
    assert [labels[index] for index in (0, 3, 9)] == [
        "Experiments",
        "Foundations",
        "Glossary",
    ]
    assert labels[1:3] == [
        "Start here · Guided experiment",
        "Real folk data & IBM results",
    ]
    assert app.tabs[1].label.startswith("Start here")
    assert any(
        element.value == "The answer stays hidden until you reveal it." for element in app.caption
    )
    assert not any(
        element.value == "What did every possible grouping score?" for element in app.subheader
    )
    assert not any(metric.label == "Minimum energy" for metric in app.metric)
    assert not any(expander.label == "Technical model and QUBO" for expander in app.expander)
    reveal = next(button for button in app.button if button.label == "Reveal all 256 answers")

    reveal.click().run(timeout=30)

    assert not app.exception
    rendered = "\n".join(
        str(element.value)
        for collection in (
            app.header,
            app.subheader,
            app.markdown,
            app.info,
            app.success,
            app.caption,
            app.metric,
        )
        for element in collection
    )
    for expected in (
        "What did every possible grouping score?",
        "What is the exact answer?",
        "How did the quantum method do?",
        "How was the question turned into a model?",
        "Can AI explain the result safely?",
        "256",
        "00001111",
        "11110000",
        "Canonical representative",
        "Registered evidence",
        "53.10%",
        "0.78125%",
        "The AI can explain the experiment. It cannot rewrite the evidence.",
        "Local ideal simulation",
        "Not quantum hardware",
        "No quantum advantage claimed",
        "Eight tune variants. Two hidden families. 256 possible groupings.",
        "You just checked every possible answer",
        "This answer is not a prediction",
        "found one of the best answers far more often than random guessing",
        "every quantum result below can be checked rather than taken on trust",
        "GPT-5.6 may explain the validated result",
    ):
        assert expected in rendered
    assert len(app.dataframe) >= 1
    assert any(expander.label == "Technical model and QUBO" for expander in app.expander)


def test_foundation_tabs_follow_registry_and_render_without_execution() -> None:
    app = AppTest.from_file("apps/learning_console/app.py")
    app.run(timeout=30)
    assert not app.exception
    labels = [tab.label for tab in app.tabs]
    assert labels[4:9] == [
        "Bits & qubits",
        "Gates",
        "Hadamard",
        "Entanglement",
        "Optimisation",
    ]
    assert any(text.value == "Glossary" for text in app.header)
    assert any(widget.label == "Search glossary" for widget in app.text_input)
    assert "build_week_quantum" not in app.session_state.filtered_state
    rendered = "\n".join(str(item.value) for item in (*app.markdown, *app.caption))
    for expected in (
        "Use these short lessons when an experiment mentions an unfamiliar quantum idea",
        "Seen a term such as QAOA, shot or QUBO in an experiment",
    ):
        assert expected in rendered
    objectives = {
        load_registry().load_document(entry.id).metadata.learning_objectives[0]
        for entry in load_registry().foundations_entries()
    }
    assert all(objective in rendered for objective in objectives)
    disclosure_labels = {
        "Show the notation",
        "Why measurement matters",
        "Why phase matters",
        "Why correlation is not communication",
        "Why exact-first matters",
    }
    assert not disclosure_labels.intersection(expander.label for expander in app.expander)
    assert not any(
        caption.value == "Optional detail — keep plain language first." for caption in app.caption
    )


def test_optional_qiskit_stays_button_gated() -> None:
    renderer = Path("apps/learning_console/renderers/guided_experiment.py").read_text(
        encoding="utf-8"
    )
    assert 'st.button("Run bounded local Qiskit (p=1, 256 shots)")' in renderer
    assert "execute_quick_qiskit()" in renderer
    app = Path("apps/learning_console/app.py").read_text(encoding="utf-8")
    assert "execute_quick_qiskit" not in app


def test_compact_experiment_presents_four_frozen_evidence_layers() -> None:
    app = AppTest.from_file("apps/learning_console/app.py")
    app.run(timeout=30)
    assert not app.exception
    rendered = "\n".join(
        str(element.value)
        for collection in (
            app.header,
            app.subheader,
            app.markdown,
            app.info,
            app.success,
            app.caption,
        )
        for element in collection
    )
    for expected in (
        "First: what is the exact answer?",
        "Ideal quantum simulation",
        "First IBM hardware validation",
        "Frozen uniform control",
        "ibm_fez",
        "4,096 QAOA shots",
        "one tiny controlled validation",
        "not quantum advantage",
        "a speedup",
        "Exact enumeration remains the scientific authority",
        "Choose one of two settings from each of four public folk-tune families",
        "Can one choice from each folk-tune family work well together?",
        "Which combination is best when every possibility is checked?",
        "The best-scoring selection is `1010`",
        "EXP-010A · compact real-data formulation",
        "Does the ideal quantum circuit concentrate on the better choices?",
        "Did the correct answer remain visible on real hardware?",
        "Replicated IBM hardware landscape",
        "Did real hardware preserve which circuit settings should perform better?",
        "Did a second, denser run reproduce the same pattern?",
    ):
        assert expected in rendered
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Exact optimum"] == "1010"
    assert metrics["Hardware improvement (R)"] == "0.514933"
    assert metrics["P(1010)"] == "24.17%"
    assert metrics["Most likely state"] == "1010"
    assert metrics["Control R"] == "-0.021309"
    assert metrics["QAOA minus control"] == "0.536242"

    source = Path("apps/learning_console/renderers/compact_experiment.py").read_text(
        encoding="utf-8"
    )
    exact_position = source.index('st.markdown("## First: what is the exact answer?")')
    replication_position = source.index("render_hardware_replication(")
    model_position = source.index('st.markdown("## How the four-bit model works")')
    assert exact_position < replication_position < model_position
    assert any(expander.label == "How the four-bit model works" for expander in app.expander)
    assert 'with st.expander("How the four-bit model works"):' in source


def test_human_question_opening_and_top_level_explainers_render() -> None:
    app = AppTest.from_file("apps/learning_console/app.py")
    app.run(timeout=30)
    assert not app.exception
    rendered = "\n".join(
        str(item.value)
        for item in (*app.title, *app.header, *app.subheader, *app.markdown, *app.caption)
    )
    for expected in (
        "Quantum Folk Lab",
        "Can patterns in folk tunes help us test a quantum method?",
        "Folk tunes give us small, understandable choices with patterns we can score",
        "Start with a made-up example",
        "The exact answer is always computed first",
        "No quantum-advantage claim is made",
        "First learn the method with eight synthetic tune variants",
    ):
        assert expected in rendered
    source = Path("apps/learning_console/app.py").read_text(encoding="utf-8")
    for removed in (
        "1 · Reveal the exact answer",
        "2 · Compare the quantum method",
        "3 · See what happened on real hardware",
        "Start with _Start here",
    ):
        assert removed not in source


def test_stale_hardware_panel_wording_is_absent() -> None:
    paths = (
        Path("README.md"),
        Path("docs/build-week/JUDGING-GUIDE.md"),
        Path("docs/build-week/DEMO-SCRIPT.md"),
        Path("docs/build-week/SUBMISSION-CHECKLIST.md"),
    )
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for stale in (
        "does not yet contain a dedicated exp-010d/011 result panel",
        "does not yet have a dedicated exp-010d/011 panel",
        "do not imply a dedicated hardware panel exists",
        "do not claim or capture a dedicated exp-010d/011 app panel",
    ):
        assert stale not in text


def test_readme_landing_uses_learner_facing_evidence_language() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    for expected in (
        "See the exact answer first",
        "## Why folk tunes?",
        "## What will I learn?",
        "## The learning journey",
        "## Try it in a few minutes",
        "## What data is included?",
        "## Four layers of evidence",
        "## Built with Codex and GPT-5.6",
        "## Reproduce and test the release",
        "## Honest limits",
        "## Repository map",
        "a rank-correlation measure showing whether two result landscapes have a similar ordering",
    ):
        assert expected in readme
    assert "## Four proof points" not in readme
    assert "audio playback or music generation" in readme


def test_renderer_keeps_registered_and_quick_run_claims_separate() -> None:
    renderer = Path("apps/learning_console/renderers/guided_experiment.py").read_text(
        encoding="utf-8"
    )
    assert "total registered sample mass across both complement-equivalent" in renderer
    assert "smaller submission-safe contract" in renderer
    assert "registered 4,096-shot evidence shown above" in renderer
    for rejected in (
        "finds the true answer about half the time",
        "current quick run achieved 53.1%",
        "quantum solved it better",
        "proves quantum advantage",
        "ran on quantum hardware",
        "GPT-5.6 discovered the solution",
    ):
        assert rejected not in renderer.lower()
