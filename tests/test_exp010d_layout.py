import json
from pathlib import Path

import pytest

from quantum_folk_lab.exp010d_layout import decode_qiskit_key, validate_layout

FINAL_LOGICAL_TO_PHYSICAL = [23, 20, 22, 21]
PHYSICAL_TO_CLASSICAL = {23: 0, 20: 1, 22: 2, 21: 3}


@pytest.mark.parametrize("value", range(16))
def test_all_basis_states_reconstruct_logical_qubo_order(value: int) -> None:
    logical = f"{value:04b}"
    classical = ["0"] * 4
    for logical_index, physical in enumerate(FINAL_LOGICAL_TO_PHYSICAL):
        classical[PHYSICAL_TO_CLASSICAL[physical]] = logical[logical_index]
    qiskit_key = "".join(reversed(classical))
    assert (
        decode_qiskit_key(qiskit_key, FINAL_LOGICAL_TO_PHYSICAL, PHYSICAL_TO_CLASSICAL) == logical
    )


def test_initial_placement_and_physical_set_are_distinct_from_final_permutation() -> None:
    validate_layout([20, 21, 23, 22], {20, 21, 22, 23})
    with pytest.raises(RuntimeError, match="initial placement"):
        validate_layout([23, 20, 22, 21], {20, 21, 22, 23})
    with pytest.raises(RuntimeError, match="physical-qubit set"):
        validate_layout([20, 21, 23, 22], {20, 21, 22, 23, 24})


def test_generated_layout_contract_is_fail_closed() -> None:
    record = json.loads(
        Path("experiments/EXP-010D-hardware-parameter-landscape/layout-contract.json").read_text(
            encoding="utf-8"
        )
    )
    assert record["required_initial_layout"] == [20, 21, 23, 22]
    assert record["required_physical_set"] == [20, 21, 22, 23]
    assert record["all_basis_states_required"] == 16
    assert record["post_hoc_reinterpretation_allowed"] is False
