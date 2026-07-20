"""Frozen EXP-010D layout validation and result-decoding semantics."""

from __future__ import annotations

FROZEN_INITIAL_LAYOUT = (20, 21, 23, 22)
FROZEN_PHYSICAL_SET = frozenset(FROZEN_INITIAL_LAYOUT)


def validate_layout(initial_index_layout: list[int], used_physical_qubits: set[int]) -> None:
    """Fail closed unless placement and physical-qubit scope are frozen."""
    if tuple(initial_index_layout) != FROZEN_INITIAL_LAYOUT:
        raise RuntimeError("initial placement differs from frozen placement")
    if used_physical_qubits != FROZEN_PHYSICAL_SET:
        raise RuntimeError("transpiled circuit uses a different physical-qubit set")


def decode_qiskit_key(
    qiskit_key: str,
    logical_to_physical: list[int],
    physical_to_classical: dict[int, int],
) -> str:
    """Reconstruct q0..q3 from Qiskit's displayed c3..c0 result key."""
    displayed = qiskit_key.replace(" ", "")
    if len(displayed) != 4 or set(displayed) - {"0", "1"}:
        raise ValueError("expected exactly four measured bits")
    if len(logical_to_physical) != 4:
        raise ValueError("expected four logical-to-physical entries")
    classical = {index: displayed[3 - index] for index in range(4)}
    try:
        return "".join(
            classical[physical_to_classical[physical]] for physical in logical_to_physical
        )
    except KeyError as error:
        raise ValueError("measurement mapping is incomplete") from error
