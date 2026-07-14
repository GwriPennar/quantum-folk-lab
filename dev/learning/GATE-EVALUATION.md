# Gate evaluation — public Foundations Learning Console

Branch: `public/learning-console-foundations-v1`  
Evaluated against `dev/learning/RELEASE-GATES.md`.

| ID | Gate | State | Evidence |
|----|------|-------|----------|
| G1 | Scope limited | **PASS** | Public trees only: `learn/`, `src/quantum_folk_lab/learning/`, `apps/learning_console/`, `dev/learning/`, `tests/learning/`. No `private/` copy. |
| G2 | Clean-clone runnable | **PASS** | `CONTENT_ROOT` resolves to repo `learn/`. Tests pass without reading `private/`. |
| G3 | No secrets/paths | **PASS** | `scripts/check_public_safety.py` passed. Lessons contain no absolute user paths. |
| G4 | No private artefacts | **PASS** | No progress JSON, screenshots, PDFs, or Playwright logs in the commit set. |
| G5 | No scientific leakage | **PASS** | No EXP-005A registered values in Markdown. No quantum-advantage claims in lesson body. |
| G6 | Content integrity | **PASS** | 5 lessons parse; registry validates; semantic mismatches = 0 (`tests/learning`). |
| G7 | Public tests | **PASS** | `pytest tests/learning/` and full public `tests/` (integration ignored) passed. |
| G8 | Main README untouched | **PASS** | Root `README.md` not modified. |
| G9 | PRs #10–#12 untouched | **PASS** | This work does not merge or modify those PRs. |
| G10 | Dependency honesty | **PASS** | Optional `[learning]` extra adds PyYAML + Streamlit; parse/export needs PyYAML only. |
| G11 | Docs present | **PASS** | Architecture, scope, Mermaid policy, contributing, release gates present. |
| G12 | Main README linkage | **PASS** | Decision: do not link from root README in this experimental release. Root README intentionally unchanged. The feature is discoverable through `learn/README.md`, `apps/learning_console/README.md` and the PR/release notes. |

## Publication decision

- **Ready-for-review** PR: allowed — all gates PASS (G12 decided: no root README link).
- Root `README.md` remains unchanged for this release.
- Local `.gitignore` `private/` entry remains unstaged and is not part of this release.
