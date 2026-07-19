# EXP-009A parser-gate failure

Gate attempt date: 2026-07-19

## Passed before parsing

- IrishMAN revision contract matched `30902e69ca45266207f8466e0d04e4bc742c5604`.
- `train.json` and `validation.json` matched their frozen SHA-256 hashes.
- All eight selected split/index references matched their canonical raw-record hashes.
- All eight records matched their declared normalized melody fingerprints.
- The deterministic exact-match tie-break selected the declared rows.

## Blocking failure

The frozen parser accepted `blackbird-1`, `blackbird-2`, and `bold-deserter-air`, then rejected
`bold-deserter-longdance` because it contains an inline key change. The failure message contained no
notation. A bounded follow-up inspection reported only setting IDs and markup counts; it did not
publish source content.

Inline key changes were predeclared as unsupported because the frozen diatonic representation does
not model key-dependent accidental meaning. Ignoring the change would silently simplify the record
beyond the contract and could change objective features. Amending the parser now would be post-data
redesign and requires a separately frozen successor experiment.

## Scientific consequence

No feature vector was accepted for the complete eight-record set, so no valid pairwise objective
exists under this contract. No 256-state exact result, QUBO, Ising result, or QAOA result may be
reported for EXP-009A.

NO-GO — OBJECTIVE OR DATA CONTRACT INVALID
