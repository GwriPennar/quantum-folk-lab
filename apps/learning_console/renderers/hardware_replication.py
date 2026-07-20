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
    st.markdown("## IBM Hardware Replication")
    st.write(
        "After validating the problem exactly and testing it locally, Quantum Folk Lab ran the "
        "same controlled four-qubit landscape experiment on IBM hardware. A second, denser run "
        "then tested whether the observed structure was reproducible rather than a one-off "
        "calibration result."
    )

    st.markdown("### EXP-010D — Controlled hardware landscape")
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

    st.markdown("### EXP-011 — Dense independent replication")
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
