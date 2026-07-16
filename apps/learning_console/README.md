# Public Learning Console — Guided Experiment and Foundations

This app renders portable lessons from [`learn/`](../../learn/README.md).

## Run

From the repository root:

```bash
pip install -e ".[learning]"
# optional bounded local Qiskit comparison:
pip install -e ".[quantum]"
# optional grounded GPT-5.6 explanation:
pip install -e ".[ai]"
streamlit run apps/learning_console/app.py
```

## Scope

- Build Week Guided Experiment: evidence, verified exact result, explanations, and export
- Optional p=1, 256-shot local ideal-simulator Qiskit comparison
- Optional grounded GPT-5.6 Sol explanation with deterministic fallback
- Foundations reading lessons
- Glossary from `learn/glossary.yaml`

The Guided Experiment is complete without Qiskit, network access, or an API key. Exact
enumeration is authoritative. The synthetic fixture supports no claim of quantum advantage or
authentic cultural-family discovery.

## Out of scope

- Private Learning Console under `private/`
- Changing or presenting registered EXP-005A evidence as a current run
- Progress persistence files
- Screenshot / evaluation packs

See [`dev/learning/PUBLIC-RELEASE-SCOPE.md`](../../dev/learning/PUBLIC-RELEASE-SCOPE.md).
