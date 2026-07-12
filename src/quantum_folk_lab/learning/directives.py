"""Directive parsing and registry of allowed Foundations IDs."""

from __future__ import annotations

import re
from typing import Any

from quantum_folk_lab.learning.models import (
    DisclosureDirective,
    GlossaryDirective,
    InteractionDirective,
    RegisteredDataDirective,
    VisualDirective,
)

DIRECTIVE_PATTERN = re.compile(
    r"^:::(visual|interaction|registered-data|disclosure|glossary)\s*\n(.*?)\n:::\s*$",
    re.MULTILINE | re.DOTALL,
)

REGISTERED_VISUALS = frozenset(
    {
        "bit-vs-qubit",
        "hadamard-probability-split",
        "z-phase-reveal",
        "double-h-interference",
        "bell-correlation",
        "circuit-thumbnail",
        "x-gate-visual",
    }
)

REGISTERED_INTERACTIONS = frozenset(
    {
        "quantum-prediction",
        "x-gate-input",
        "detail-disclosure",
    }
)

REGISTERED_DATA = frozenset()


def _parse_kv_block(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in body.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"directive line missing key: value — {line!r}")
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip()
    return out


def parse_directive_block(kind: str, body: str, line: int) -> Any:
    kv = _parse_kv_block(body)
    if kind == "visual":
        visual_id = kv.get("id")
        if not visual_id:
            raise ValueError("visual directive requires id")
        if visual_id not in REGISTERED_VISUALS:
            raise ValueError(f"unknown visual id: {visual_id}")
        return VisualDirective(visual_id=visual_id, line=line)
    if kind == "interaction":
        interaction_id = kv.get("id")
        if not interaction_id:
            raise ValueError("interaction directive requires id")
        if interaction_id not in REGISTERED_INTERACTIONS:
            raise ValueError(f"unknown interaction id: {interaction_id}")
        params = {k: v for k, v in kv.items() if k != "id"}
        return InteractionDirective(interaction_id=interaction_id, params=params, line=line)
    if kind == "registered-data":
        data_id = kv.get("id")
        if not data_id or data_id not in REGISTERED_DATA:
            raise ValueError(f"unknown registered-data id: {data_id}")
        return RegisteredDataDirective(
            data_id=data_id,
            source=kv.get("source", ""),
            view=kv.get("view", ""),
            line=line,
        )
    if kind == "disclosure":
        disclosure_id = kv.get("id")
        if not disclosure_id:
            raise ValueError("disclosure directive requires id")
        return DisclosureDirective(
            disclosure_id=disclosure_id,
            label=kv.get("label", "Show more"),
            level=kv.get("level", "intermediate"),
            line=line,
        )
    if kind == "glossary":
        return GlossaryDirective(scope=kv.get("scope", "foundations"), line=line)
    raise ValueError(f"unknown directive kind: {kind}")
