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
| G12 | Human product decision | **NEEDS HUMAN DECISION** | Whether/when to link this Learning Console from the main README. Deliberately out of scope here. |

## Publication decision

- Automatic **ready-for-review** PR: **blocked** by G12 (product decision on README visibility).
- **Draft / experimental** PR: allowed, with G12 called out and main README left unchanged.
- Local `.gitignore` `private/` entry remains unstaged and is not part of this release.
