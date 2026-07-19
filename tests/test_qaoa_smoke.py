from quantum_folk_lab.domain.synthetic import generate_benchmark
from quantum_folk_lab.graph.build import build_similarity_graph
from quantum_folk_lab.quantum.ibm_runtime import require_confirmation
from quantum_folk_lab.quantum.qaoa_local import run_local_qaoa
from quantum_folk_lab.qubo.two_family import build_two_family_qubo


def test_qaoa_local_smoke() -> None:
    model = build_two_family_qubo(build_similarity_graph(generate_benchmark()))
    result = run_local_qaoa(model, shots=32)
    assert result.backend == "local-softmax-simulator"
    assert result.counts


def test_qpu_requires_confirmation() -> None:
    try:
        require_confirmation(submit_hardware=False, confirmation="")
    except PermissionError:
        return
    raise AssertionError("QPU execution should require confirmation")
