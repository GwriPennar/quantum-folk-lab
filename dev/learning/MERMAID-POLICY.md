# QFL Mermaid diagram policy (Foundations hybrid migration)

This phase supports a **deliberately restricted** diagram subset — not full Mermaid compatibility.

## Supported syntax

- `flowchart LR` — simple left-to-right flows
- `flowchart TB` — simple top-to-bottom flows
- Labelled nodes: `A["Label text"]`
- Directed edges: `A --> B`
- Small concept sequences (typically 2–8 nodes)

## Unsupported syntax (fail clearly)

- Sequence diagrams, class diagrams, Gantt, pie charts
- Subgraphs, styling directives, click handlers
- `classDef`, `style`, `linkStyle`
- Embedded HTML or `<br/>` in labels (use plain text)
- `flowchart` directions other than LR/TB

## Renderers (priority order)

1. **deterministic-python** — default for LR/TB flowcharts with `Node["label"]` pattern
2. **mmdc** — optional via `npx @mermaid-js/mermaid-cli` when installed
3. **safe-fallback** — text-only SVG when security validation fails

## Source-hash validation

Each diagram source is SHA-256 hashed. The manifest at `diagrams/mermaid-manifest.json` records `source_sha256`, renderer, and `stale` flag.

## Accessibility

Generated SVG includes `<title>` and `role="img"` with `aria-label` from the lesson context.

## Security restrictions

SVG output must not contain:

- `<script>` tags
- External `href` / `xlink:href` to http(s) URLs
- Unrestricted file references

Violations trigger **safe-fallback** rendering.

## Authoring guidance

Keep diagrams small and readable. Prefer LR for process flows and TB for before/after stacks. Complex circuits belong in Python visuals, not Mermaid.
