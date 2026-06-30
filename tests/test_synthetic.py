from quantum_folk_lab.domain.synthetic import generate_benchmark


def test_generation_is_deterministic() -> None:
    assert generate_benchmark(42) == generate_benchmark(42)
    assert len(generate_benchmark(42)) == 8
