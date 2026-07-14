# Public release scope — Foundations Learning Console

## Included

- Five Foundations lessons under `learn/lessons/`
- `learn/glossary.yaml` and `learn/registry.yaml`
- `src/quantum_folk_lab/learning/` parser/registry/export package
- Minimal Streamlit app in `apps/learning_console/`
- Public-safe tests in `tests/learning/`
- Contributor docs in `dev/learning/`

## Explicitly excluded

- Entire `private/` tree
- `.guided_progress.json` and progress backups
- Screenshots, contact sheets, PDFs, Playwright logs
- Absolute local paths, PIDs, usernames, backup locations
- Private prompts / operational transcripts
- EXP-005A private case-study / provenance Markdown
- EXP-001 private guided lab Markdown (public EXP-001 experiment code remains elsewhere)
- Main README changes (deferred)

## Scientific claims policy

- Simulator-first
- No implied quantum advantage
- No implied real-corpus tune-family inference
- EXP-005A registered artefacts are not modified by this release
