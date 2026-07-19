import itertools

import pytest

from quantum_folk_lab.real_data_quantum import (
    FeatureParseError,
    build_binary_model,
    direct_energy,
    enumerate_exact,
    extract_coarse_features,
    feature_distance,
    ising_energy,
    qubo_energy,
)

SYNTHETIC = [
    f"X:{index}\nM:4/4\nK:C\nC D E G | G E D C |"
    if index % 2 == 0
    else f"X:{index}\nM:4/4\nK:G\nG A B d | e d B G |"
    for index in range(8)
]


def test_feature_contract_is_bounded_and_nonempty() -> None:
    features = extract_coarse_features(SYNTHETIC[0])
    assert len(features) == 9
    assert all(0 <= value <= 1 for value in features.values())


def test_parser_rejects_lyrics_multivoice_inline_key_and_short_input() -> None:
    invalid = [
        "X:1\nK:C\nCDEFGABC\nw:words",
        "X:1\nV:1\nK:C\nCDEFGABC",
        "X:1\nK:C\nCDEF[K:G]GABC",
        "X:1\nK:C\nCDE",
    ]
    for abc in invalid:
        with pytest.raises(FeatureParseError):
            extract_coarse_features(abc)


def test_distance_is_symmetric_bounded_and_zero_on_identity() -> None:
    left = extract_coarse_features(SYNTHETIC[0])
    right = extract_coarse_features(SYNTHETIC[1])
    assert feature_distance(left, left) == 0
    assert feature_distance(left, right) == feature_distance(right, left)
    assert 0 <= feature_distance(left, right) <= 1


def test_direct_qubo_and_ising_agree_for_all_states() -> None:
    features = [extract_coarse_features(abc) for abc in SYNTHETIC]
    families = [0, 0, 1, 1, 2, 2, 3, 3]
    model = build_binary_model(features, families)
    for bits in itertools.product((0, 1), repeat=8):
        direct = direct_energy(bits, features, families)
        assert qubo_energy(bits, model) == pytest.approx(direct, abs=1e-10)
        assert ising_energy(bits, model) == pytest.approx(direct, abs=1e-10)


def test_exact_result_is_feasible_and_penalty_bound_holds() -> None:
    features = [extract_coarse_features(abc) for abc in SYNTHETIC]
    result = enumerate_exact(features, [0, 0, 1, 1, 2, 2, 3, 3])
    assert result["all_optima_feasible"] is True
    assert result["minimum_infeasible_energy"] >= 7
    assert result["maximum_agreement_error"] <= 1e-10
