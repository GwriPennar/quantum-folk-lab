# Release gates — public Foundations Learning Console

Gate states: `PASS` | `FAIL` | `NOT APPLICABLE` | `NEEDS HUMAN DECISION`

Automatic PR readiness requires every gate to be `PASS` or justified `NOT APPLICABLE`.
Any `FAIL` or `NEEDS HUMAN DECISION` stops publication.

| ID | Gate | Criterion |
|----|------|-----------|
| G1 | Scope limited | Only Foundations public areas; no wholesale `private/` copy |
| G2 | Clean-clone runnable | Package and app resolve content under `learn/` without `private/` |
| G3 | No secrets/paths | Public safety scan passes; no absolute user paths, tokens, emails |
| G4 | No private artefacts | No progress JSON, screenshots, PDFs, Playwright logs committed |
| G5 | No scientific leakage | No duplicated EXP-005A registered values; no quantum-advantage claims |
| G6 | Content integrity | Five lessons parse; registry validates; semantic mismatches = 0 |
| G7 | Public tests | `pytest tests/learning/` and existing public tests pass |
| G8 | Main README untouched | Diff does not modify root `README.md` |
| G9 | PRs #10–#12 untouched | Those PRs remain open/unmerged by this work |
| G10 | Dependency honesty | Optional extras declared; Streamlit/Qiskit not required for parse/export |
| G11 | Docs present | `PUBLIC-RELEASE-SCOPE`, architecture, Mermaid policy, contributing docs |
| G12 | Main README linkage | Human decision on whether to attach the Learning Console to the main README |

Until a human records a decision, G12 is `NEEDS HUMAN DECISION` and blocks ready-for-review publication.
Once decided, record **PASS** with the decision text (link or do-not-link). “Featured in README” readiness requires an explicit link decision; do-not-link is a valid PASS for an experimental release that keeps the root README unchanged.
