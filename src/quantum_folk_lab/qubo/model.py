from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class QUBOModel:
    variables: tuple[str, ...]
    linear: dict[str, float] = field(default_factory=dict)
    quadratic: dict[tuple[str, str], float] = field(default_factory=dict)
    offset: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)

    def energy(self, bits: tuple[int, ...] | list[int]) -> float:
        if len(bits) != len(self.variables):
            raise ValueError("bitstring length does not match variables")
        values = dict(zip(self.variables, bits, strict=True))
        energy = self.offset
        energy += sum(coeff * values[name] for name, coeff in self.linear.items())
        energy += sum(coeff * values[a] * values[b] for (a, b), coeff in self.quadratic.items())
        return energy

    def dense_matrix(self) -> list[list[float]]:
        size = len(self.variables)
        index = {name: i for i, name in enumerate(self.variables)}
        matrix = [[0.0 for _ in range(size)] for _ in range(size)]
        for name, coeff in self.linear.items():
            matrix[index[name]][index[name]] += coeff
        for (a, b), coeff in self.quadratic.items():
            matrix[index[a]][index[b]] += coeff
        return matrix
