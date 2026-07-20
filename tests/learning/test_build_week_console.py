from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


def test_navigation_hierarchy_and_no_secret_display() -> None:
    app = Path("apps/learning_console/app.py").read_text(encoding="utf-8")
    assert '["Experiments", "Foundations", "Glossary"]' in app
    assert "Start here · Guided Experiment" in app
    assert "Real folk data + IBM hardware · EXP-010A" in app
    assert "st.sidebar.radio" not in app
    assert "st.sidebar.selectbox" not in app
    assert 'st.selectbox("Lesson"' not in app
    renderer = Path("apps/learning_console/renderers/guided_experiment.py").read_text(
        encoding="utf-8"
    )
    assert "OPENAI_" + "API" + "_KEY" not in renderer
    assert "Guided Experiment" in renderer


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
        "Start here · Guided Experiment",
        "Real folk data + IBM hardware · EXP-010A",
    ]
    assert app.tabs[1].label.startswith("Start here")
    assert any(element.value == "5 · The 256 Reveal" for element in app.subheader)
    reveal = next(button for button in app.button if button.label == "Reveal all 256 assignments")

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
        "Part A · Complete exact answer space",
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
        "Eight synthetic tune variants hide two families",
        "Every one of the 256 possible answers, checked exactly",
        "This answer is not a prediction",
        "found the true answer far more often than random guessing",
        "GPT-5.6 may explain the validated result",
    ):
        assert expected in rendered
    assert len(app.dataframe) >= 1


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
        "Exact classical result",
        "Ideal quantum simulation",
        "First IBM hardware validation",
        "Frozen uniform control",
        "ibm_fez",
        "4,096 QAOA shots",
        "one tiny controlled validation",
        "not quantum advantage",
        "a speedup",
        "Exact enumeration remains the scientific authority",
        "Four real folk-tune families, two settings each",
        "Did the compact problem’s correct state remain visible on real hardware?",
        "Replicated IBM hardware landscape",
        "Did real hardware preserve which circuit settings should perform better?",
        "Did a second, denser run reproduce the same landscape structure?",
    ):
        assert expected in rendered
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Exact optimum"] == "1010"
    assert metrics["Hardware QAOA R"] == "0.514933"
    assert metrics["P(1010)"] == "24.17%"
    assert metrics["Most likely state"] == "1010"
    assert metrics["Control R"] == "-0.021309"
    assert metrics["QAOA minus control"] == "0.536242"


def test_compact_introduction_and_trust_statement_render() -> None:
    app = AppTest.from_file("apps/learning_console/app.py")
    app.run(timeout=30)
    assert not app.exception
    rendered = "\n".join(str(item.value) for item in (*app.markdown, *app.caption))
    for expected in (
        "Learn quantum computing by checking the exact answer first",
        "Reveal the exact answer",
        "Compare the quantum method",
        "See what happened on real hardware",
        "Exact classical evaluation remains authoritative throughout",
        "No quantum-advantage claim is made",
    ):
        assert expected in rendered


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
