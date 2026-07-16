"""Structured scientific-claim policy for explanations and exports."""

from __future__ import annotations

import re

_FORBIDDEN = {
    "quantum advantage": re.compile(r"\bquantum advantage\b", re.IGNORECASE),
    "speedup": re.compile(r"\b(?:quantum )?speed-?up\b", re.IGNORECASE),
    "production": re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE),
    "scalability": re.compile(r"\bscalable|scalability\b", re.IGNORECASE),
    "cultural authenticity": re.compile(
        r"\b(?:authentic|true) (?:Welsh |folk )?(?:families|tradition)\b", re.IGNORECASE
    ),
    "fallback as qaoa": re.compile(r"classical fallback (?:is|as) (?:genuine )?qaoa", re.I),
    "historical as live": re.compile(r"registered .*?(?:live|computed now)", re.I),
    "unique complement": re.compile(r"(?:only|unique) correct (?:assignment|bitstring)", re.I),
    "sample equals expectation": re.compile(
        r"sampled an optimum.{0,50}(?:expected result|expectation) is optimal", re.I
    ),
}


def claim_violations(text: str) -> tuple[str, ...]:
    return tuple(name for name, pattern in _FORBIDDEN.items() if pattern.search(text))


def validate_claims(text: str) -> None:
    violations = claim_violations(text)
    if violations:
        raise ValueError("prohibited scientific claims: " + ", ".join(violations))
