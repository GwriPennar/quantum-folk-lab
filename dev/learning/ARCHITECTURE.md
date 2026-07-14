# Public Learning Console — architecture

## Hybrid boundary (Recommendation B)

| Portable Markdown owns | Python owns |
|------------------------|-------------|
| Titles, order, routes | Streamlit rendering adapters |
| Explanatory prose | Optional Qiskit/Aer demos |
| Mermaid diagram sources | Interaction widgets |
| Glossary definitions | Export tooling |
| Semantic markers | Validation |

## Layout

```text
learn/                         # content (source of truth)
src/quantum_folk_lab/learning/ # parser, registry, export
apps/learning_console/         # Streamlit renderer
dev/learning/                  # contributor + release docs
tests/learning/                # public-safe tests
```

## Non-goals for this release

- Publishing the private Streamlit tree
- EXP-005A researcher provenance UI
- Progress persistence files
- Full Mermaid CLI dependency
