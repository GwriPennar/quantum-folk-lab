"""Public-safe tests for the Foundations Learning Console extraction."""

from __future__ import annotations

from pathlib import Path

import pytest

from quantum_folk_lab.learning.export import export_registry_bundle
from quantum_folk_lab.learning.glossary import load_glossary
from quantum_folk_lab.learning.models import DisclosureDirective
from quantum_folk_lab.learning.parser import parse_lesson_markdown
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
    exported = (tmp_path / "markdown" / "guided-foundations-bits_qubits.md").read_text(
        encoding="utf-8"
    )
    assert "<summary>Show the notation</summary>" in exported
    assert "relative phase affects later interference" in exported


def test_learning_package_does_not_import_streamlit() -> None:
    import quantum_folk_lab.learning.parser as parser_mod

    source = Path(parser_mod.__file__).read_text(encoding="utf-8")
    assert "streamlit" not in source.lower()


def test_five_disclosures_have_non_empty_bodies() -> None:
    registry = load_registry()
    disclosures = [
        block
        for entry in registry.entries
        for block in registry.load_document(entry.id).blocks
        if isinstance(block, DisclosureDirective)
    ]
    assert len(disclosures) == 5
    assert all(item.body.strip() for item in disclosures)


def test_empty_disclosure_parses_but_remains_fail_closed() -> None:
    source = Path("learn/lessons/bits-and-qubits.md").read_text(encoding="utf-8")
    body = (
        "body: A qubit state can be written as `α|0⟩ + β|1⟩`, where `|α|² + |β|² = 1`. "
        "The squared magnitudes give measurement probabilities; relative phase affects later "
        "interference.\n"
    )
    source = source.replace(
        body,
        "",
    )
    document = parse_lesson_markdown(source, Path("empty-disclosure.md"))
    disclosure = next(block for block in document.blocks if isinstance(block, DisclosureDirective))
    assert disclosure.body == ""


def test_malformed_disclosure_fails_closed() -> None:
    source = Path("learn/lessons/bits-and-qubits.md").read_text(encoding="utf-8")
    source = source.replace("label: Show the notation", "malformed line")
    with pytest.raises(ValueError, match="missing key"):
        parse_lesson_markdown(source, Path("malformed-disclosure.md"))
