"""Public-safe tests for the Foundations Learning Console extraction."""

from __future__ import annotations

from pathlib import Path

import pytest

from quantum_folk_lab.learning.export import export_registry_bundle
from quantum_folk_lab.learning.glossary import load_glossary
from quantum_folk_lab.learning.paths import CONTENT_ROOT, REGISTRY_PATH
from quantum_folk_lab.learning.registry import clear_registry_cache, load_registry
from quantum_folk_lab.learning.semantic_state import semantic_marker_html, validate_semantic_text
from quantum_folk_lab.learning.validation import validate_lesson_document, validate_registry


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_registry_cache()


def test_content_root_is_public_learn() -> None:
    assert CONTENT_ROOT.name == "learn"
    assert "private" not in CONTENT_ROOT.parts
    assert REGISTRY_PATH.is_file()


def test_five_foundations_lessons_parse() -> None:
    registry = load_registry()
    assert len(registry.entries) == 5
    assert not validate_registry(registry)
    for entry in registry.entries:
        doc = registry.load_document(entry.id)
        errors = validate_lesson_document(doc, registry)
        assert not errors, errors


def test_semantic_parity_zero() -> None:
    registry = load_registry()
    mismatches = 0
    for entry in registry.entries:
        doc = registry.load_document(entry.id)
        text = doc.all_markdown_text() + semantic_marker_html(doc)
        errors = validate_semantic_text(text, doc)
        if errors:
            mismatches += 1
    assert mismatches == 0


def test_no_private_or_path_leaks_in_lessons() -> None:
    registry = load_registry()
    for entry in registry.entries:
        doc = registry.load_document(entry.id)
        text = doc.all_markdown_text()
        assert "C:\\Users" not in text
        assert "/Users/" not in text
        assert "private/" not in text
        assert "quantum advantage" not in text.lower()
        assert ".guided_progress" not in text


def test_glossary_terms_present() -> None:
    terms = {t.term.lower() for t in load_glossary()}
    for required in (
        "bit",
        "qubit",
        "measurement",
        "gate",
        "qaoa",
        "qubo",
        "energy",
        "noise",
        "superposition",
        "spearman rho",
        "pub",
        "hardware backend",
        "hadamard",
    ):
        assert required in terms


def test_static_export(tmp_path: Path) -> None:
    registry = load_registry()
    counts = export_registry_bundle(registry, tmp_path)
    assert counts["markdown"] == 5
    assert counts["html"] == 5


def test_learning_package_does_not_import_streamlit() -> None:
    import quantum_folk_lab.learning.parser as parser_mod

    source = Path(parser_mod.__file__).read_text(encoding="utf-8")
    assert "streamlit" not in source.lower()
