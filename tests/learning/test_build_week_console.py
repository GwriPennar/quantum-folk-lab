from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


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
    assert view.json_export().startswith(b"{")
