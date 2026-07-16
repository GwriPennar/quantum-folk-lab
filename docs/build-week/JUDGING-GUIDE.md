# Quantum Folk Lab — Build Week judging guide

## What this is

Quantum Folk Lab is an Education product that walks a learner through one fixed, copyright-safe
synthetic music question: can interval, contour, and rhythm similarities recover two unlabeled
tune families? The product exposes the evidence, verified binary model, authoritative exhaustive
solution, optional local-Qiskit comparison, explanations, and reproducibility record.

The public Foundations console existed before Build Week at `281ba40`. The governing plan landed
at `3950a1f`. The deterministic core (#16) and Guided Experiment (#17) are Build Week work.

## Fastest deterministic run

Requires Python 3.11 or later. From the repository root:

```powershell
python -m pip install -e .
qfl build-week-exact
qfl build-week-exact --format json --output qfl-result.json
```

Expected canonical complement class: `00001111`; all 256 assignments are checked.

## Full Learning Console

```powershell
python -m pip install -e ".[learning]"
streamlit run apps/learning_console/app.py
```

Open the displayed local URL. Guided Experiment is the first route. Move through evidence, model,
exact result, optional comparison, explanation, export, and limitations.

## Optional capabilities

For a bounded p=1, 256-shot local ideal-simulator run:

```powershell
python -m pip install -e ".[learning,quantum]"
```

For optional grounded explanations:

```powershell
python -m pip install -e ".[learning,ai]"
```

Configure the standard OpenAI SDK credential environment variable. The model defaults to
`gpt-5.6-sol`; `QFL_OPENAI_MODEL` may override it. The deterministic explanation is used when the
SDK, credential, network, response schema, grounding, or claim validation is unavailable.

## Fixture, limitations, and troubleshooting

`synthetic-two-family-v1-seed42` is deterministic generated sample data, not culturally authentic
or copyrighted material. Exact enumeration is ground truth. The optional Qiskit run is local ideal
simulation, not hardware evidence. Finite-shot sampling, an optimum sample, and an expectation are
different measurements. No quantum advantage, speedup, scale, or real-family discovery is claimed.

- No Qiskit: the exact journey remains complete; install `.[quantum]` only for the comparison.
- No OpenAI access: the deterministic three-level explanation remains complete.
- App import failure: install `.[learning]` in the active environment.
- Validate the release: run `python scripts/verify_build_week_release.py`.

The repository is MIT licensed. Codex implemented and tested the staged product under Gwri's
scientific and product decisions. GPT-5.6 Sol is used only for an optional validated explanation;
it never computes or changes scientific values.
