from quantum_folk_lab.exp011_analysis import average_ranks, classify, spearman


def test_average_tie_ranks_and_spearman() -> None:
    assert average_ranks([1, 2, 2, 4]) == [1, 2.5, 2.5, 4]
    assert abs(spearman([1, 2, 3], [10, 20, 30]) - 1) < 1e-12


def test_frozen_classification_thresholds() -> None:
    assert classify(0.8, 0.009) == "STRONGLY REPLICATED"
    assert classify(0.5, 0.049) == "REPLICATED"
    assert classify(0.49, 0.01) == "WEAK OR INCONCLUSIVE"
    assert classify(0.0, 0.5) == "NOT REPLICATED"
