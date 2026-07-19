"""EXP-009A-R1 parser with a frozen inline-key metadata policy."""

from __future__ import annotations

import re
from dataclasses import dataclass

from quantum_folk_lab.real_data_quantum import FEATURE_NAMES, FeatureParseError

_HEADER_RE = re.compile(r"^[A-Za-z]:")
_NOTE_RE = re.compile(
    r"(?:\^{1,2}|_{1,2}|=)?(?P<note>[A-Ga-g])(?P<oct>[,']*)"
    r"(?:\d+(?:/\d*)?|/+)?"
)
_INLINE_FIELD_RE = re.compile(r"\[(?P<field>[A-Za-z]):(?P<content>[^\]]*)\]")


@dataclass(frozen=True)
class ParsedFeatures:
    """Public aggregate parser result without notation or event sequences."""

    features: dict[str, float]
    inline_key_field_count: int


def _strip_inline_fields(music: str) -> tuple[str, int]:
    """Strip frozen non-note metadata and reject unsupported inline fields."""

    if re.search(r"\[[A-Za-z]:[^\]]*$", music):
        raise FeatureParseError("Selected record has a malformed inline field.")

    key_count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal key_count
        field = match.group("field")
        if field == "K":
            key_count += 1
            return ""
        if field == "V":
            raise FeatureParseError("Selected record contains multiple voices.")
        raise FeatureParseError("Selected record contains an unsupported inline field.")

    return _INLINE_FIELD_RE.sub(replace, music), key_count


def extract_coarse_features_r1(abc: str) -> ParsedFeatures:
    """Extract nine frozen aggregates after removing inline key metadata."""

    if not abc.strip():
        raise FeatureParseError("Selected record has an empty ABC body.")
    lines = abc.splitlines()
    if any(line.startswith(("W:", "w:")) for line in lines):
        raise FeatureParseError("Selected record contains lyrics.")
    if any(line.startswith("V:") for line in lines):
        raise FeatureParseError("Selected record contains multiple voices.")
    if abc.count('"') % 2:
        raise FeatureParseError("Selected record has unmatched quoted text.")
    if abc.count("{") != abc.count("}") or abc.count("!") % 2:
        raise FeatureParseError("Selected record has unmatched ornament markup.")

    music_lines = [line.split("%", 1)[0] for line in lines if not _HEADER_RE.match(line.strip())]
    music, inline_key_field_count = _strip_inline_fields("\n".join(music_lines))
    music = re.sub(r'"[^"]*"|![^!]*!|\{[^}]*\}', "", music)

    pitches: list[int] = []
    for match in _NOTE_RE.finditer(music):
        letter = match.group("note")
        octave = int(letter.islower())
        octave += match.group("oct").count("'")
        octave -= match.group("oct").count(",")
        pitches.append("CDEFGAB".index(letter.upper()) + 7 * octave)
    if len(pitches) < 8:
        raise FeatureParseError("Selected record has fewer than eight parsed note events.")

    intervals = [b - a for a, b in zip(pitches, pitches[1:], strict=False)]
    count = len(intervals)
    directions = [1 if value > 0 else -1 for value in intervals if value]
    changes = sum(a != b for a, b in zip(directions, directions[1:], strict=False))
    values = {
        "event_count_scaled": min(len(pitches), 256) / 256,
        "range_scaled": min(max(pitches) - min(pitches), 28) / 28,
        "ascending_proportion": sum(value > 0 for value in intervals) / count,
        "descending_proportion": sum(value < 0 for value in intervals) / count,
        "repeated_proportion": sum(value == 0 for value in intervals) / count,
        "step_proportion": sum(abs(value) == 1 for value in intervals) / count,
        "skip_proportion": sum(2 <= abs(value) <= 3 for value in intervals) / count,
        "leap_proportion": sum(abs(value) >= 4 for value in intervals) / count,
        "contour_change_rate": changes / (len(directions) - 1) if len(directions) > 1 else 0.0,
    }
    if tuple(values) != FEATURE_NAMES or not all(0 <= value <= 1 for value in values.values()):
        raise AssertionError("Feature contract invariant failed.")
    return ParsedFeatures(values, inline_key_field_count)
