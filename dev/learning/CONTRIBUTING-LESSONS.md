# Contributing lessons

1. Add or edit a Markdown file under `learn/lessons/` with YAML front matter.
2. Register it in `learn/registry.yaml` with a unique `id`, `route`, and `order`.
3. Use only registered visual / interaction directive IDs (see `quantum_folk_lab.learning.directives`).
4. Declare `semantic.required_markers` that appear literally in the lesson body.
5. Run `pytest tests/learning/ -q`.
6. Keep prose free of absolute paths, secrets, and quantum-advantage claims.

Do not duplicate registered scientific result values in Markdown when a public registered artefact can be loaded instead.
