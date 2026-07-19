# EXP-009A-R1 successor gate failure

## Completed verification

- IrishMAN revision: verified against the pinned EXP-008B manifest.
- Train and validation file SHA-256 values: verified.
- All eight canonical raw-record SHA-256 values: verified.
- All eight normalized melody fingerprints: verified.
- Deterministic first-row tie-breaking for all eight settings: verified.
- Frozen synthetic parser proof: passed before real-data access.

## Non-disclosing structural result

The diagnostic reports field tags and counts only. It does not report notation or field content.

| Setting | Inline `K:` count | Other inline metadata tags |
|---|---:|---|
| `blackbird-1` | 0 | none |
| `blackbird-2` | 0 | none |
| `bold-deserter-air` | 0 | none |
| `bold-deserter-longdance` | 1 | `M:`, `Q:` |
| `catherine-tyrrell-1` | 0 | none |
| `catherine-tyrrell-2` | 0 | none |
| `merry-old-woman-1` | 1 | `M:` |
| `merry-old-woman-2` | 1 | `M:` |

## Decision

The successor contract predeclares inline `K:` as removable non-note metadata. It requires every
other inline field to have a predeclared policy or fail closed. No `M:` or `Q:` policy was frozen,
so the observed records cannot be processed under EXP-009A-R1 without a post-observation contract
change. No tune-specific exception was introduced.

Feature extraction stopped before a complete eight-record feature set existed. Exact enumeration
and local QAOA were therefore prohibited and were not run.

Outcome: `NO-GO — SUCCESSOR PARSER OR OBJECTIVE INVALID`.
