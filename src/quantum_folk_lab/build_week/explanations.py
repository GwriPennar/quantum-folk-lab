"""Deterministic explanations at three materially different learner levels."""

from __future__ import annotations

from typing import cast

from .claims import validate_claims
from .models import LearnerLevel, ResultEnvelope


def deterministic_explanation(envelope: ResultEnvelope, level: LearnerLevel) -> str:
    canonical = str(envelope.exact_result["canonical_complement_class"])
    energy = float(cast(float, envelope.exact_result["minimum_energy"]))
    if level is LearnerLevel.FIRST_ENCOUNTER:
        text = (
            "We asked whether eight made-up tune variants could be separated into two groups "
            "using their melodic intervals, up-and-down contour, and rhythm. The computer checked "
            "every possible grouping. Its best unlabeled split is represented by "
            f"{canonical}, with energy {energy:.6f}. Reversing every 0 and 1 describes the same "
            "two groups, so neither label is special. Checking every option is practical here and "
            "is the authoritative answer. A later local quantum simulation can be compared with "
            "this answer, but it does not replace it. The fixture is synthetic and this does not "
            "discover real cultural tune families."
        )
    elif level is LearnerLevel.TECHNICAL_LEARNER:
        text = (
            "The fixed eight-tune fixture is converted into a weighted graph from interval, "
            "contour, and rhythm similarities. One binary variable assigns each tune to either "
            "side of an unlabeled partition. The QUBO penalises separating similar pairs, keeping "
            "dissimilar pairs together, and severe imbalance. Exhaustive enumeration validates "
            f"the minimum energy {energy:.6f}; {canonical} is the canonical representative of its "
            "complement class. Direct, QUBO, and Ising energies are checked before the envelope is "
            "issued. Exact enumeration is authoritative for 256 assignments. Optional p=1 local "
            "Qiskit sampling later measures how probability concentrates relative to this known "
            "reference, not whether the reference is correct."
        )
    else:
        text = (
            "The registered synthetic fixture preserves the EXP-005A variable order and uses "
            f"tau={envelope.parameters['tau']:.2f}, lambda={envelope.parameters['lambda']:.2f}. "
            "All 2^8 assignments are evaluated, with direct/QUBO and QUBO/Ising agreement enforced "
            "at their registered tolerances. The argmin is represented canonically by "
            f"{canonical}; its global bitwise complement is scientifically equivalent because "
            "partition labels are exchangeable. The exact minimum "
            f"({energy:.6f}) and family-recovery metric are deterministic validation evidence. "
            "A bounded ideal-simulator QAOA run can later report expectation and finite-shot "
            "statistics separately. An optimum sample cannot establish an optimum expectation, "
            "hardware performance, or generalisation beyond this fixture."
        )
    validate_claims(text)
    return text
