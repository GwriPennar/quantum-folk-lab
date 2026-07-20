"""Evidence-only presentation of the governed IBM hardware replication programme."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from quantum_folk_lab.hardware_replication_evidence import load_hardware_replication_evidence

CONTROL_WARNING = (
    "Control warning retained: the scrambled-phase controls showed a small systematic offset, "
    "so relative landscape structure is more reliable than the absolute score baseline."
)


def render_hardware_replication(repo_root: Path) -> None:
    """Render committed aggregates only; fail closed if their contracts differ."""

    try:
        evidence = load_hardware_replication_evidence(repo_root)
    except ValueError:
        st.error("Governed hardware evidence is unavailable or failed validation.")
        return

    exp010d = evidence.exp010d
    exp011 = evidence.exp011
    st.markdown("## Replicated IBM hardware landscape")
    st.write(
        "Two governed hardware runs tested whether the broader pattern of better and worse "
        "circuit settings could be reproduced."
    )

    st.markdown("### EXP-010D — Controlled hardware landscape")
    st.markdown(
        "**Question:** Did real hardware preserve which circuit settings should perform better?"
    )
    st.caption(
        f"{exp010d.backend} · {exp010d.unique_cells} unique cells · "
        f"{exp010d.pub_count} PUBs · {exp010d.shots_per_pub:,} shots per PUB"
    )
    first, second, third, fourth = st.columns(4)
    first.metric("Ideal/hardware rho", f"{exp010d.spearman_rho:.4f}")
    second.metric("Classification", exp010d.classification)
    third.metric("Centre rank", str(exp010d.centre_rank))
    fourth.metric("Centre most-likely state", exp010d.centre_most_likely_state)
    st.success(
        "The real device strongly preserved the ordering of the ideal parameter landscape "
        "across the preregistered 25-cell grid."
    )
    st.warning(CONTROL_WARNING)

    st.markdown("#### Did real hardware preserve the predicted landscape?")
    ideal_hardware_rows = [
        {
            "cell": point.cell_id,
            "Ideal value": point.ideal_r,
            "Hardware value": point.hardware_r,
        }
        for point in evidence.ideal_hardware_points
    ]
    st.vega_lite_chart(
        ideal_hardware_rows,
        {
            "height": 260,
            "mark": {"type": "point", "filled": True, "size": 80},
            "encoding": {
                "x": {
                    "field": "Ideal value",
                    "type": "quantitative",
                    "scale": {"zero": False},
                    "axis": {"title": "Ideal relative improvement (R)"},
                },
                "y": {
                    "field": "Hardware value",
                    "type": "quantitative",
                    "scale": {"zero": False},
                    "axis": {"title": "Measured hardware improvement (R)"},
                },
                "tooltip": [
                    {"field": "cell", "type": "nominal", "title": "Cell"},
                    {"field": "Ideal value", "type": "quantitative", "format": ".4f"},
                    {"field": "Hardware value", "type": "quantitative", "format": ".4f"},
                ],
            },
        },
        width="stretch",
    )
    st.caption(
        f"Across 25 governed cells, rho was {exp010d.spearman_rho:.4f}. Points following the "
        "same upward pattern mean theory and hardware broadly agreed about which settings were "
        "better. This is agreement in ordering, not evidence of speedup, scale or quantum "
        "advantage."
    )

    st.markdown("### EXP-011 — Independent dense replication")
    st.markdown("**Question:** Did a second, denser run reproduce the same landscape structure?")
    st.caption(
        f"{exp011.backend} · {exp011.unique_cells} unique cells · {exp011.pub_count} PUBs · "
        f"{exp011.shots_per_pub:,} shots per PUB"
    )
    first, second, third = st.columns(3)
    first.metric("Full-grid ideal/hardware rho", f"{exp011.spearman_rho:.4f}")
    second.metric("Embedded 25-cell rho", f"{exp011.embedded_25_rho:.4f}")
    third.metric("Cross-run rho", f"{exp011.cross_run_rho:.4f}")
    first, second, third = st.columns(3)
    first.metric(
        "Repeated-cell mean absolute difference", f"{exp011.cross_run_mean_absolute_difference:.4f}"
    )
    second.metric("Classification", exp011.classification)
    third.metric("Centre", f"{exp011.centre_rank}/81 · state {exp011.centre_most_likely_state}")
    st.caption("The centre was within the preregistered top-five check.")
    st.success(
        "The denser run reproduced the broad landscape and closely matched the earlier hardware "
        "run, supporting repeatability across different calibration windows."
    )
    st.warning(CONTROL_WARNING)

    st.markdown("#### Did the hardware pattern reproduce?")
    cross_run_rows = [
        {
            "cell": point.cell_id,
            "EXP-010D result": point.exp010d_r,
            "EXP-011 result": point.exp011_r,
        }
        for point in evidence.cross_run_points
    ]
    st.vega_lite_chart(
        cross_run_rows,
        {
            "height": 260,
            "mark": {"type": "point", "filled": True, "size": 80},
            "encoding": {
                "x": {
                    "field": "EXP-010D result",
                    "type": "quantitative",
                    "scale": {"zero": False},
                    "axis": {"title": "EXP-010D measured improvement (R)"},
                },
                "y": {
                    "field": "EXP-011 result",
                    "type": "quantitative",
                    "scale": {"zero": False},
                    "axis": {"title": "EXP-011 measured improvement (R)"},
                },
                "tooltip": [
                    {"field": "cell", "type": "nominal", "title": "Shared cell"},
                    {"field": "EXP-010D result", "type": "quantitative", "format": ".4f"},
                    {"field": "EXP-011 result", "type": "quantitative", "format": ".4f"},
                ],
            },
        },
        width="stretch",
    )
    st.caption(
        f"Across 25 shared governed cells, cross-run rho was {exp011.cross_run_rho:.4f}. The "
        "second hardware run closely reproduced the first. Replication strengthens confidence "
        "in this small experiment; it does not establish general performance."
    )

    st.markdown("### Comparison")
    st.dataframe(
        [
            {
                "Evidence": "EXP-010D",
                "Unique cells": exp010d.unique_cells,
                "Ideal/hardware rho": f"{exp010d.spearman_rho:.4f}",
                "Embedded 25-cell rho": "—",
                "Cross-run rho": "—",
                "Classification": exp010d.classification,
            },
            {
                "Evidence": "EXP-011",
                "Unique cells": exp011.unique_cells,
                "Ideal/hardware rho": f"{exp011.spearman_rho:.4f}",
                "Embedded 25-cell rho": f"{exp011.embedded_25_rho:.4f}",
                "Cross-run rho": f"{exp011.cross_run_rho:.4f}",
                "Classification": exp011.classification,
            },
        ],
        hide_index=True,
        width="stretch",
    )

    st.markdown("### Exact-first limitations")
    st.markdown(
        "- Exact classical enumeration remains authoritative.\n"
        "- These experiments test preservation of a small parameter-landscape structure.\n"
        "- The compact problem contains only 16 states.\n"
        "- The results do not demonstrate quantum advantage or speedup.\n"
        "- They do not establish generalisation to larger problems.\n"
        "- Hardware results do not prove musical quality or musical truth.\n"
        "- No IBM access is needed to inspect or run the Learning Console."
    )
    with st.expander("Authoritative public evidence"):
        st.markdown(
            "- `experiments/EXP-010D-hardware-parameter-landscape-run/RESULT-REPORT.md`\n"
            "- `experiments/EXP-010D-hardware-parameter-landscape-run/hardware-analysis.json`\n"
            "- `experiments/EXP-011-dense-hardware-landscape-run/RESULT-REPORT.md`\n"
            "- `experiments/EXP-011-dense-hardware-landscape-run/hardware-analysis.json`"
        )
