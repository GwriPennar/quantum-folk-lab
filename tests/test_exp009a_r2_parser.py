import pytest

from quantum_folk_lab.real_data_quantum import FeatureParseError
from quantum_folk_lab.real_data_quantum_r2 import extract_coarse_features_r2

BASE = "X:301\nM:3/4\nK:F\nF, G, A, C | D E f a' |"


@pytest.mark.parametrize("tag", ["K", "M", "Q"])
@pytest.mark.parametrize("position", ["start", "middle", "end"])
def test_permitted_fields_at_every_position_preserve_features(tag: str, position: str) -> None:
    field = f"[{tag}:ABCDEFG quoted-like note text]"
    bodies = {
        "start": f"{field}F, G, A, C | D E f a' |",
        "middle": f"F, G, A, C |{field} D E f a' |",
        "end": f"F, G, A, C | D E f a' |{field}",
    }
    result = extract_coarse_features_r2(f"X:302\nK:F\n{bodies[position]}")
    assert result.features == extract_coarse_features_r2(BASE).features
    assert result.inline_field_counts[tag] == 1


def test_adjacent_and_repeated_fields_have_separate_accurate_counts() -> None:
    abc = (
        "X:303\nK:F\n[K:G][M:6/8][Q:quoted tempo CDE][K:D][M:2/4][Q:fast ABC]"
        "F, G, A, C | D E f a' |"
    )
    result = extract_coarse_features_r2(abc)
    assert result.features == extract_coarse_features_r2(BASE).features
    assert result.inline_field_counts == {"K": 2, "M": 2, "Q": 2}


def test_note_like_and_quoted_tempo_content_never_generates_events() -> None:
    baseline = extract_coarse_features_r2(BASE)
    revised = extract_coarse_features_r2(
        'X:304\nK:F\nF, G,[K:ABCDEFG][M:CDE][Q:"Allegro ABCDEFG"] A, C | D E f a\' |'
    )
    assert revised.features == baseline.features


def test_surrounding_case_and_octave_marks_remain_intact() -> None:
    plain = extract_coarse_features_r2("X:305\nK:F\nF,, G, A C | d e' f' a'' |")
    revised = extract_coarse_features_r2(
        "X:305\nK:F\nF,,[K:G] G,[M:2/4] A C | d[Q:slow] e' f' a'' |"
    )
    assert revised.features == plain.features


@pytest.mark.parametrize("tag", ["K", "M", "Q"])
def test_malformed_and_nested_permitted_fields_fail_closed(tag: str) -> None:
    invalid = [
        f"[{tag}:unterminated",
        f"[{tag}:outer[K:C]]",
    ]
    for field in invalid:
        with pytest.raises(FeatureParseError):
            extract_coarse_features_r2(f"X:306\nK:F\nF, G, A, C {field} D E f a'")


@pytest.mark.parametrize("tag", ["L", "P", "I", "N", "U", "V"])
def test_unknown_and_voice_inline_fields_fail_closed(tag: str) -> None:
    marker = "NONDISCLOSABLE"
    with pytest.raises(FeatureParseError) as error:
        extract_coarse_features_r2(f"X:307\nK:F\nF, G, A, C [{tag}:{marker}] D E f a'")
    assert marker not in str(error.value)


@pytest.mark.parametrize(
    "line",
    ["w:lyrics", "W:lyrics", "V:second", "m:macro", "U:symbol"],
)
def test_lyrics_voice_macros_and_user_symbols_remain_rejected(line: str) -> None:
    with pytest.raises(FeatureParseError):
        extract_coarse_features_r2(f"X:308\nK:F\n{line}\nF, G, A, C | D E f a' |")


def test_exceptions_never_reveal_metadata_content_or_notation() -> None:
    marker = "PRIVATESEQUENCE"
    with pytest.raises(FeatureParseError) as error:
        extract_coarse_features_r2(f"X:309\nK:F\nF, G, A, C [P:{marker}] D E f a'")
    assert marker not in str(error.value)
    assert "F, G, A" not in str(error.value)
