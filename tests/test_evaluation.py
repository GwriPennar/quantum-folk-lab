from quantum_folk_lab.evaluation.metrics import family_recovery


def test_family_recovery_is_label_invariant() -> None:
    assert family_recovery((0, 0, 1, 1), (1, 1, 0, 0)) == 1.0
