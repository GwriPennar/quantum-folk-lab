# Quantum Folk Lab — Build Week judging guide

**Learn quantum computing through folk music—check the exact answer first, then compare simulation
and real hardware.**

## Education problem and audience

Quantum demonstrations can be opaque, abstract, and easy to overstate. Quantum Folk Lab is for
learners, educators, and technically curious musicians who want to inspect known classical truth,
compare bounded quantum heuristics, and understand honest hardware evidence through meaningful
folk-music-derived optimisation settings.

The guided fixture is deterministic synthetic teaching data. A separate governed programme covers
licence-checked real-data formulation and IBM hardware. The application does not play audio, and
not every guided example uses historical notation.

## One-command judge experience

Requires Python 3.11 or later:

```powershell
python -m pip install -e ".[learning]"
streamlit run apps/learning_console/app.py
```

Open the displayed URL. In **Experiments**, follow **Start here · Guided experiment** and click
**Reveal all 256 answers**. Then inspect **Foundations** and **Glossary**. The exact path works without Qiskit,
IBM credentials, an OpenAI API key, or network access.

## Three strongest proof points

1. **Inspectable truth:** all 256 synthetic-fixture assignments are evaluated; exact enumeration
   precedes interpretation of registered or live heuristic samples.
2. **Governed hardware structure:** EXP-010D returned 32/32 PUBs and rho `0.96`, classified
   **LANDSCAPE SUPPORTED**, with centre rank 1 and the control warning retained.
3. **Independent dense replication:** EXP-011 returned 88/88 PUBs; full rho was
   `0.9046747967479675`, embedded-25 rho `0.9315384615384615`, and cross-run rho
   `0.9776923076923076`, classified **STRONGLY REPLICATED**, with centre rank `4/81` and the
   control warning retained.

Public reports:

- [`experiments/EXP-010D-hardware-parameter-landscape-run/RESULT-REPORT.md`](../../experiments/EXP-010D-hardware-parameter-landscape-run/RESULT-REPORT.md)
- [`experiments/EXP-011-dense-hardware-landscape-run/RESULT-REPORT.md`](../../experiments/EXP-011-dense-hardware-landscape-run/RESULT-REPORT.md)

The merged Learning Console includes a governed, read-only EXP-010D/EXP-011 hardware replication
panel. Its two scatter plots and headline statistics load directly from the public evidence above;
no IBM access is performed while the app renders.

## Judging criteria

| Criterion | Evidence |
| --- | --- |
| Education | progressive Guided experiment, exact 256 Reveal, portable Foundations and Glossary |
| Technological Implementation | deterministic contracts, QUBO/Ising verification, bounded Qiskit, fail-closed IBM intent/receipt and tests |
| Design | tabbed learner path, capability gating, accessible exact landscape and reproducibility exports |
| Potential Impact | teaches scientific restraint while connecting quantum optimisation with culturally meaningful subject matter |
| Quality of the Idea | exact-first evidence hierarchy, negative truth gates, one-job/no-retry governance, and independent replication |

## Codex and GPT-5.6

Codex accelerated implementation, testing, visual verification, CI diagnosis, safe experiment
packaging, retrieval, and reproducibility checks. Gwri selected the research direction, froze each
protocol, explicitly authorized every hardware job, accepted warnings, interpreted results, and
approved merges. Codex did not autonomously authorize QPU use or decide scientific claims.

GPT-5.6 is an optional explanation layer. Deterministic code supplies all scientific values; model
input is filtered and output is schema-, grounding-, number-, and claim-checked. Invalid or
unavailable output fails closed to the complete deterministic explanation.

## Correct interpretation and limitations

The hardware results show preservation and independent replication of a small frozen parameter-
landscape structure. Exact classical evaluation remains authoritative. The evidence does not show
quantum advantage, speedup, scale, generalisation, musical truth, real-family discovery, or
commercial superiority. Preflight-estimated QPU time is not reported as charged usage. The
control-quality warning remains part of both landscape interpretations.

Troubleshooting:

- No Qiskit: the deterministic app and tracked evidence remain complete.
- No OpenAI access: the deterministic explanation remains complete.
- App import failure: install `.[learning]` in the active environment.
- Validate the release: `python scripts/verify_build_week_release.py`.
