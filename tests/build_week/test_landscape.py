from __future__ import annotations

import builtins
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from quantum_folk_lab.build_week.landscape import (
    build_exact_landscape,
    parse_registered_qaoa_evidence,
)
from quantum_folk_lab.build_week.quantum import quantum_capability
from quantum_folk_lab.tune_family import bits_from_bitstring, registered_fixture

REGISTERED_RESULT = Path("experiments/EXP-005A-tune-family-qaoa/results/tune-family-qaoa-p1.json")
REGISTERED_RESULT_SHA256 = "c3f2b346bc692e20a006df645ead8ced121f2c9197ca71f73e92241362737f1e"


def test_exact_landscape_is_complete_validated_and_deterministic() -> None:
    landscape = build_exact_landscape()
    repeated = build_exact_landscape()
    assignments = [entry.assignment for entry in landscape.entries]
    optima = [entry.assignment for entry in landscape.entries if entry.is_global_optimum]

    assert landscape == repeated
    assert landscape.fixture_identifier == "synthetic-two-family-v1-seed42"
    assert landscape.variable_count == 8
    assert len(landscape.entries) == 256
    assert len(set(assignments)) == 256
    assert all(len(assignment) == 8 for assignment in assignments)
    assert {entry.integer_index for entry in landscape.entries} == set(range(256))
    assert optima == ["00001111", "11110000"]
    assert landscape.global_optima == ("00001111", "11110000")
    assert landscape.canonical_representative == "00001111"
    assert landscape.raw_minimum_energy == pytest.approx(-1.7763568394002505e-15)
    assert landscape.display_minimum_energy == 0.0
    assert landscape.distinct_energy_levels == 60
    assert landscape.next_best_energy == pytest.approx(5.351984)
    assert landscape.optimum_to_next_gap == pytest.approx(5.351984)
    assert landscape.complement_symmetry_verified is True
    assert landscape.direct_qubo_verified_assignments == 256
    assert landscape.qubo_ising_verified_assignments == 256


def test_landscape_values_use_the_registered_qubo_energy() -> None:
    fixture = registered_fixture()
    landscape = build_exact_landscape()
    for entry in landscape.entries:
        assert entry.energy == pytest.approx(
            fixture.model.energy(bits_from_bitstring(entry.assignment))
        )
        assert entry.complement == f"{255 - entry.integer_index:08b}"
        assert entry.row_bits == entry.assignment[:4]
        assert entry.column_bits == entry.assignment[4:]
    markers = {entry.assignment: entry.marker for entry in landscape.entries if entry.marker}
    assert markers == {"00001111": "C", "11110000": "E"}


def test_registered_qaoa_read_model_matches_unchanged_tracked_evidence() -> None:
    normalized_source = REGISTERED_RESULT.read_text(encoding="utf-8").replace("\r\n", "\n")
    source_hash = hashlib.sha256(normalized_source.encode("utf-8")).hexdigest()
    assert source_hash == REGISTERED_RESULT_SHA256
    evidence = parse_registered_qaoa_evidence(
        json.loads(REGISTERED_RESULT.read_text(encoding="utf-8"))
    )

    assert evidence.experiment_identifier == "EXP-005A-tune-family-qaoa"
    assert evidence.depth == 1
    assert evidence.shots == 4096
    assert evidence.optimiser == "COBYLA"
    assert evidence.optimiser_max_iterations == 80
    assert evidence.initial_point_count == 4
    assert evidence.sampler_seed == evidence.estimator_seed == evidence.transpile_seed == 42
    assert evidence.canonical_count == 1063
    assert evidence.complement_count == 1112
    assert evidence.optimum_class_count == 2175
    assert evidence.optimum_class_probability == pytest.approx(2175 / 4096)
    assert evidence.canonical_probability == pytest.approx(1063 / 4096)
    assert evidence.complement_probability == pytest.approx(1112 / 4096)
    assert evidence.uniform_optimum_class_probability == pytest.approx(2 / 256)


def test_landscape_module_has_no_optional_runtime_imports() -> None:
    source = Path("src/quantum_folk_lab/build_week/landscape.py").read_text(encoding="utf-8")
    assert "qiskit" not in source.lower()
    assert "openai" not in source.lower()
    assert "streamlit" not in source.lower()


def test_exact_reveal_remains_available_without_qiskit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def without_qiskit(
        name: str,
        globals: dict[str, Any] | None = None,
        locals: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if name == "qiskit" or name.startswith("qiskit."):
            raise ModuleNotFoundError("qiskit intentionally unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", without_qiskit)
    capability = quantum_capability()

    assert capability.available is False
    assert len(build_exact_landscape().entries) == 256
