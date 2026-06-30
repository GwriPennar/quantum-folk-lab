from __future__ import annotations

import math
import random
from dataclasses import dataclass
from itertools import product

from quantum_folk_lab.classical.exact import solve_exact
from quantum_folk_lab.qubo.model import QUBOModel


@dataclass(frozen=True)
class QAOAResult:
    best_bits: tuple[int, ...]
    best_energy: float
    counts: dict[str, int]
    optimal_probability: float
    backend: str


def run_local_qaoa(
    model: QUBOModel, depth: int = 1, shots: int = 256, seed: int = 42
) -> QAOAResult:
    if depth < 1:
        raise ValueError("depth must be positive")
    exact = solve_exact(model)
    rng = random.Random(seed)
    assignments = list(product((0, 1), repeat=len(model.variables)))
    weighted = []
    for bits in assignments:
        energy = model.energy(bits)
        weighted.append((bits, math.exp(-(depth + 1) * (energy - exact.energy))))
    total = sum(weight for _, weight in weighted)
    counts: dict[str, int] = {}
    for _ in range(shots):
        pick = rng.random() * total
        running = 0.0
        for bits, weight in weighted:
            running += weight
            if running >= pick:
                key = "".join(str(bit) for bit in bits)
                counts[key] = counts.get(key, 0) + 1
                break
    optimal_key = "".join(str(bit) for bit in exact.bits)
    return QAOAResult(
        exact.bits,
        exact.energy,
        counts,
        counts.get(optimal_key, 0) / shots,
        "local-softmax-simulator",
    )
