# Public experimental Learning Console — Foundations edition

This app renders portable lessons from [`learn/`](../../learn/README.md).

## Run

From the repository root:

```bash
pip install -e ".[learning]"
# optional live Aer demos:
pip install -e ".[quantum]"
streamlit run apps/learning_console/app.py
```

## Scope

- Foundations reading lessons only
- Glossary from `learn/glossary.yaml`
- Optional Qiskit/Aer Hadamard demo when `[quantum]` is installed

## Out of scope

- Private Learning Console under `private/`
- EXP-005A researcher provenance UI
- Progress persistence files
- Screenshot / evaluation packs

See [`dev/learning/PUBLIC-RELEASE-SCOPE.md`](../../dev/learning/PUBLIC-RELEASE-SCOPE.md).
