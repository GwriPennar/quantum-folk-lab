from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from quantum_folk_lab.qubo.model import QUBOModel


@dataclass(frozen=True)
class SolverResult:
    bits: tuple[int, ...]
    energy: float
    evaluated: int


def solve_exact(
    model: QUBOModel, fix_first_zero: bool = True, max_variables: int = 20
) -> SolverResult:
    n = len(model.variables)
    if n > max_variables:
        raise ValueError(f"exact search limited to {max_variables} variables")
    prefix = (0,) if fix_first_zero and n else ()
    best_bits: tuple[int, ...] | None = None
    best_energy = float("inf")
    evaluated = 0
    for suffix in product((0, 1), repeat=n - len(prefix)):
        bits = prefix + suffix
        energy = model.energy(bits)
        evaluated += 1
        if energy < best_energy:
            best_bits, best_energy = bits, energy
    if best_bits is None:
        raise RuntimeError("no assignments evaluated")
    return SolverResult(best_bits, best_energy, evaluated)
