from __future__ import annotations

import builtins
from typing import Any

import pytest

from quantum_folk_lab.quantum_basics import EXPERIMENTS, list_experiments, require_qiskit


def test_basics_registry_contains_required_experiments() -> None:
    assert {experiment.name for experiment in list_experiments()} >= {
        "zero",
        "x",
        "hadamard",
        "double-hadamard",
        "z-zero",
        "z-after-h",
        "bell",
    }


def test_missing_qiskit_error_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name in {"qiskit", "qiskit_aer"}:
            raise ModuleNotFoundError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    with pytest.raises(RuntimeError, match="optional local Qiskit dependencies"):
        require_qiskit()


def test_experiment_descriptions_are_nonempty() -> None:
    for experiment in EXPERIMENTS.values():
        assert experiment.description
        assert experiment.expected_behaviour
        assert experiment.limitations
