"""Lesson validation against registry and directive contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

from quantum_folk_lab.learning.directives import (
    REGISTERED_DATA,
    REGISTERED_INTERACTIONS,
    REGISTERED_VISUALS,
)
from quantum_folk_lab.learning.glossary import validate_glossary_references
from quantum_folk_lab.learning.models import (
    InteractionDirective,
    LessonDocument,
    MermaidBlock,
    RegisteredDataDirective,
    VisualDirective,
)
from quantum_folk_lab.learning.registry import LessonRegistry

ABSOLUTE_PATH = re.compile(r"[A-Za-z]:\\Users|/Users/")


def validate_registry(registry: LessonRegistry) -> list[str]:
    errors: list[str] = []
    ids = [e.id for e in registry.entries]
    routes = [e.route for e in registry.entries]
    if len(ids) != len(set(ids)):
        errors.append("duplicate lesson ids in registry")
    if len(routes) != len(set(routes)):
        errors.append("duplicate routes in registry")

    section_orders: dict[str, list[int]] = {}
    for entry in registry.entries:
        section_orders.setdefault(entry.section or "default", []).append(entry.order)
    for section, orders in section_orders.items():
        if len(orders) != len(set(orders)):
            errors.append(f"duplicate order within section {section!r}")

    id_set = set(ids)
    for entry in registry.entries:
        doc = registry.load_document(entry.id)
        for prereq in doc.metadata.prerequisites:
            if prereq not in id_set:
                errors.append(f"{entry.id}: invalid prerequisite {prereq}")
        if doc.metadata.next_lesson and doc.metadata.next_lesson not in id_set:
            errors.append(f"{entry.id}: invalid next_lesson {doc.metadata.next_lesson}")
    return errors


def validate_lesson_document(doc: LessonDocument, registry: LessonRegistry) -> list[str]:
    errors: list[str] = []
    entry = registry.by_id(doc.metadata.id)
    if entry.route != doc.metadata.route:
        errors.append("metadata route disagrees with registry")
    if entry.path and ABSOLUTE_PATH.search(entry.path):
        errors.append("absolute path in registry entry")

    declared_visuals = set(doc.metadata.visuals)
    declared_interactions = set(doc.metadata.interactions)
    used_visuals: set[str] = set()
    used_interactions: set[str] = set()

    for block in doc.blocks:
        if isinstance(block, VisualDirective):
            used_visuals.add(block.visual_id)
            if block.visual_id not in REGISTERED_VISUALS:
                errors.append(f"unregistered visual: {block.visual_id}")
        if isinstance(block, InteractionDirective):
            used_interactions.add(block.interaction_id)
            if block.interaction_id not in REGISTERED_INTERACTIONS:
                errors.append(f"unregistered interaction: {block.interaction_id}")
        if isinstance(block, RegisteredDataDirective):
            if block.data_id not in REGISTERED_DATA:
                errors.append(f"unregistered data id: {block.data_id}")
        if isinstance(block, MermaidBlock):
            if "<script" in block.source.lower():
                errors.append("mermaid block contains script tag")
            if "subgraph" in block.source.lower() or "classDef" in block.source.lower():
                errors.append(f"unsupported mermaid syntax in {doc.metadata.id}")

    missing_visuals = declared_visuals - used_visuals
    if missing_visuals:
        errors.append(f"visuals declared but not used: {sorted(missing_visuals)}")
    missing_interactions = declared_interactions - used_interactions
    if missing_interactions:
        errors.append(f"interactions declared but not used: {sorted(missing_interactions)}")

    errors.extend(validate_glossary_references(doc.metadata.glossary_terms))

    contract = doc.metadata.semantic
    text = doc.all_markdown_text()
    for marker in contract.required_markers:
        if marker not in text:
            errors.append(f"missing required marker: {marker}")

    if ABSOLUTE_PATH.search(text):
        errors.append("absolute local path in lesson prose")

    return errors


def validate_schema_file(schema_path: Path) -> bool:
    return schema_path.is_file() and schema_path.suffix == ".json"


def load_schema(schema_path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(schema_path.read_text(encoding="utf-8")))
