"""EXP-009A-R2 parser with a closed K/M/Q inline metadata policy."""

from __future__ import annotations

import re
from dataclasses import dataclass

from quantum_folk_lab.real_data_quantum import FEATURE_NAMES, FeatureParseError

_HEADER_RE = re.compile(r"^[A-Za-z]:")
_FIELD_START_RE = re.compile(r"\[(?P<tag>[A-Za-z]):")
_NOTE_RE = re.compile(
    r"(?:\^{1,2}|_{1,2}|=)?(?P<note>[A-Ga-g])(?P<oct>[,']*)"
    r"(?:\d+(?:/\d*)?|/+)?"
)
_PERMITTED_TAGS = ("K", "M", "Q")


@dataclass(frozen=True)
class ParsedFeaturesR2:
    """Aggregate-only parse result with separate non-sensitive field counts."""

    features: dict[str, float]
    inline_field_counts: dict[str, int]


def _strip_closed_metadata(music: str) -> tuple[str, dict[str, int]]:
    """Remove only well-formed K/M/Q fields, without exposing their contents."""

    counts = dict.fromkeys(_PERMITTED_TAGS, 0)
    pieces: list[str] = []
    cursor = 0
    while match := _FIELD_START_RE.search(music, cursor):
        pieces.append(music[cursor : match.start()])
        closing = music.find("]", match.end())
        if closing < 0:
            raise FeatureParseError("Selected record has a malformed inline field.")
        content = music[match.end() : closing]
        if "[" in content:
            raise FeatureParseError("Selected record has a nested inline field.")
        tag = match.group("tag")
        if tag == "V":
            raise FeatureParseError("Selected record contains multiple voices.")
        if tag not in counts:
            raise FeatureParseError("Selected record contains an unsupported inline field.")
        counts[tag] += 1
        cursor = closing + 1
    pieces.append(music[cursor:])
    return "".join(pieces), counts


def extract_coarse_features_r2(abc: str) -> ParsedFeaturesR2:
    """Extract inherited aggregates after closed-whitelist metadata removal."""

    if not abc.strip():
        raise FeatureParseError("Selected record has an empty ABC body.")
    lines = abc.splitlines()
    stripped_lines = [line.strip() for line in lines]
    if any(line.startswith(("W:", "w:")) for line in stripped_lines):
        raise FeatureParseError("Selected record contains lyrics.")
    if any(line.startswith("V:") for line in stripped_lines):
        raise FeatureParseError("Selected record contains multiple voices.")
    if any(line.startswith(("m:", "U:")) for line in stripped_lines):
        raise FeatureParseError("Selected record contains macros or user-defined symbols.")
    if abc.count('"') % 2:
        raise FeatureParseError("Selected record has unmatched quoted text.")
    if abc.count("{") != abc.count("}") or abc.count("!") % 2:
        raise FeatureParseError("Selected record has unmatched ornament markup.")

    music_lines = [line.split("%", 1)[0] for line in lines if not _HEADER_RE.match(line.strip())]
    music, counts = _strip_closed_metadata("\n".join(music_lines))
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
    return ParsedFeaturesR2(values, counts)
