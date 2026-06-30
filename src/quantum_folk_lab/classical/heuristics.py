from __future__ import annotations

from quantum_folk_lab.qubo.model import QUBOModel


def greedy_bit_flip(model: QUBOModel) -> tuple[int, ...]:
    bits = [0] * len(model.variables)
    improved = True
    while improved:
        improved = False
        for i in range(len(bits)):
            candidate = bits.copy()
            candidate[i] = 1 - candidate[i]
            if model.energy(candidate) < model.energy(bits):
                bits = candidate
                improved = True
    return tuple(bits)
