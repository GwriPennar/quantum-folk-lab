from quantum_folk_lab.domain.synthetic import generate_benchmark
from quantum_folk_lab.similarity.combined import combined_similarity, interval_similarity


def test_transposition_invariance() -> None:
    melodies = generate_benchmark()
    assert interval_similarity(melodies[0], melodies[1]) == 1.0


def test_similarity_bounds_and_symmetry() -> None:
    a, b = generate_benchmark()[0:2]
    assert combined_similarity(a, a) == 1.0
    assert combined_similarity(a, b) == combined_similarity(b, a)
    assert 0.0 <= combined_similarity(a, b) <= 1.0
