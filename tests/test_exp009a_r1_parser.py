import pytest

from quantum_folk_lab.real_data_quantum import FeatureParseError
from quantum_folk_lab.real_data_quantum_r1 import extract_coarse_features_r1

BASE = "X:91\nM:4/4\nK:D\nD E F G | A B c d |"


def test_inline_key_metadata_does_not_change_features() -> None:
    baseline = extract_coarse_features_r1(BASE)
    revised = extract_coarse_features_r1("X:91\nK:D\nD E F G [K:G] | A B c d |")
    assert revised.features == baseline.features
    assert revised.inline_key_field_count == 1


@pytest.mark.parametrize(
    "body",
    [
        "[K:G]D E F G | A B c d |",
        "D E F G |[K:G] A B c d |",
        "D E F G | A B c d |[K:G]",
    ],
)
def test_inline_key_at_start_middle_and_end(body: str) -> None:
    result = extract_coarse_features_r1(f"X:92\nK:D\n{body}")
    assert result.features == extract_coarse_features_r1(BASE).features
    assert result.inline_key_field_count == 1


def test_multiple_inline_keys_are_counted_and_content_never_becomes_notes() -> None:
    result = extract_coarse_features_r1("X:93\nK:D\nD E [K:ABCDEFG] F G | A [K:CDEF] B c d |")
    assert result.features == extract_coarse_features_r1(BASE).features
    assert result.inline_key_field_count == 2


@pytest.mark.parametrize("field", ["[K:G", "[V:alto]", "[Q:120]"])
def test_unsupported_or_malformed_inline_fields_fail_closed_without_notation(field: str) -> None:
    marker = "SECRETNOTATION"
    with pytest.raises(FeatureParseError) as error:
        extract_coarse_features_r1(f"X:94\nK:D\nD E F G {field}{marker} A B c d")
    assert marker not in str(error.value)


def test_explicit_accidentals_remain_diatonically_ignored() -> None:
    plain = extract_coarse_features_r1("X:95\nK:D\nD E F G | A B c d |")
    altered = extract_coarse_features_r1("X:95\nK:D\n^D _E =F G | A B c d |")
    assert altered.features == plain.features


def test_note_letters_and_octave_marks_around_removed_field_are_preserved() -> None:
    plain = extract_coarse_features_r1("X:96\nK:D\nD, E F G | A B c' d' |")
    revised = extract_coarse_features_r1("X:96\nK:D\nD,[K:G] E F G | A B[K:C] c' d' |")
    assert revised.features == plain.features
    assert revised.inline_key_field_count == 2


@pytest.mark.parametrize(
    "abc",
    [
        "",
        "X:97\nK:D\nD E F G | A B c d |\nw:words",
        "X:97\nV:1\nK:D\nD E F G | A B c d |",
        'X:97\nK:D\n"unterminated D E F G A B c d',
        "X:97\nK:D\n{unterminated D E F G A B c d",
        "X:97\nK:D\nD E F",
    ],
)
def test_existing_fail_closed_guards_remain(abc: str) -> None:
    with pytest.raises(FeatureParseError):
        extract_coarse_features_r1(abc)
