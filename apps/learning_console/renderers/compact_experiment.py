"""Scrollable, evidence-only renderer for EXP-010A."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import streamlit as st

EXPERIMENT_ROOT = (
    Path(__file__).resolve().parents[3] / "experiments" / "EXP-010A-compact-family-encoding"
)


@st.cache_data
def _load_json(name: str) -> dict[str, Any]:
    """Load deterministic committed evidence; never compute or contact a service."""
    return cast(
        dict[str, Any],
        json.loads((EXPERIMENT_ROOT / name).read_text(encoding="utf-8")),
    )


def render_compact_experiment() -> None:
    """Render one natural progression from accessible context to technical evidence."""
    exact = _load_json("compact-exact-result.json")
    qaoa = _load_json("qaoa-result.json")

    st.header("EXP-010A")
    st.subheader("Choosing one setting from four folk-tune families")
    st.markdown(
        "**Real public tune data · 4 binary choices · 16 combinations**  \n"
        "**Exact classical result · Ideal simulator evidence · No real QPU result**"
    )

    st.markdown("## Why this experiment exists")
    st.write(
        "An earlier eight-qubit formulation spent half its variables enforcing one-hot choices. "
        "EXP-010A asks whether the same verified musical objective can be represented directly "
        "with one meaningful bit per tune family."
    )

    st.markdown("## The problem in plain language")
    st.write(
        "For each of four tune families, choose one of two pre-verified settings. The objective "
        "scores how well the four choices work together. With only sixteen combinations, every "
        "possibility can be checked exactly."
    )

    st.markdown("## Choices and bit meanings")
    choices = [
        {"bit": "y0", "family": "Blackbird", "0 maps to": "R2 pair 10", "1 maps to": "R2 pair 01"},
        {
            "bit": "y1",
            "family": "Bold Deserter",
            "0 maps to": "R2 pair 10",
            "1 maps to": "R2 pair 01",
        },
        {
            "bit": "y2",
            "family": "Catherine Tyrrell",
            "0 maps to": "R2 pair 10",
            "1 maps to": "R2 pair 01",
        },
        {
            "bit": "y3",
            "family": "The Merry Old Woman",
            "0 maps to": "R2 pair 10",
            "1 maps to": "R2 pair 01",
        },
    ]
    st.dataframe(choices, width="stretch", hide_index=True)
    st.caption("Every four-bit string is valid. No penalty, repair, or postselection is used.")

    st.markdown("## Data entering the algorithm")
    st.write(
        "The experiment reads only committed aggregate evidence derived from four public tune "
        "families. It does not reopen the source corpus or include raw notation in this package."
    )
    with st.expander("Committed input contract"):
        st.markdown((EXPERIMENT_ROOT / "ENCODING-CONTRACT.md").read_text(encoding="utf-8"))

    st.markdown("## Step-by-step process")
    st.markdown(
        "1. Substitute one compact bit for each two-variable one-hot pair.\n"
        "2. Verify all sixteen compact energies against the earlier scientific objective.\n"
        "3. Enumerate all sixteen states to establish the authoritative optimum.\n"
        "4. Run the frozen local p=1 QAOA protocol as a bounded heuristic comparison.\n"
        "5. Compare the sampled distribution with exact energy ordering and a uniform baseline."
    )

    st.markdown("## Exact classical result")
    optimum = exact["optimum_bitstrings"][0]
    left, middle, right = st.columns(3)
    left.metric("Exact optimum", optimum)
    middle.metric("Mapped R2 state", "01100110")
    right.metric("States checked", "16 / 16")
    st.success(
        f"Exact enumeration is authoritative. The minimum energy is {exact['minimum_energy']:.15f}."
    )

    st.markdown("## Quantum result")
    metrics = qaoa["ideal_metrics"]
    first, second, third = st.columns(3)
    first.metric(
        "Ideal relative improvement", f"{metrics['relative_expected_energy_improvement']:.2%}"
    )
    second.metric("Ideal optimum mass", f"{metrics['optimum_mass']:.2%}")
    third.metric("Four-lowest mass", f"{metrics['four_lowest_mass']:.2%}")
    st.info(
        "This is a frozen local ideal-simulator comparison, not IBM hardware and not evidence "
        "of quantum advantage. No Qiskit computation runs while this tab renders."
    )

    st.markdown("## Technical evidence")
    with st.expander("Encoding equivalence and earlier R2 comparison"):
        st.markdown((EXPERIMENT_ROOT / "R2-COMPARISON.md").read_text(encoding="utf-8"))
    with st.expander("Frozen QAOA report"):
        st.markdown((EXPERIMENT_ROOT / "QAOA-REPORT.md").read_text(encoding="utf-8"))
    with st.expander("Machine-readable exact and QAOA summaries"):
        st.json(
            {
                "exact": {
                    "optimum": optimum,
                    "minimum": exact["minimum_energy"],
                    "gap": exact["gap_to_next_non_optimal"],
                },
                "qaoa": metrics,
                "hardware readiness": qaoa["hardware_readiness_gate"],
            }
        )

    st.markdown("## Limitations and current stage")
    st.markdown(
        "- Four families and sixteen combinations are intentionally small.\n"
        "- Aggregate evidence is data-informed but does not establish musical or cultural truth.\n"
        "- The quantum comparison is local ideal simulation only.\n"
        "- Exact enumeration remains the scientific authority.\n"
        "- No quantum advantage or hardware-performance claim is made."
    )
