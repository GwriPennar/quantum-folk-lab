from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


def test_navigation_hierarchy_and_no_secret_display() -> None:
    app = Path("apps/learning_console/app.py").read_text(encoding="utf-8")
    assert '["Guided Experiment", "Foundations", "Glossary"]' in app
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
    assert app.sidebar.radio[0].value == "Guided Experiment"
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
    ):
        assert expected in rendered
    assert len(app.dataframe) >= 1


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
