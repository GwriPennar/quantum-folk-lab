# EXP-009A feature contract

Frozen: 2026-07-19, before reading the selected raw ABC bodies or calculating results.

## Input verification

Read only the eight EXP-008B-selected rows from an explicitly supplied external IrishMAN cache.
Before feature extraction verify dataset revision, split/index, file SHA-256, canonical raw-record
SHA-256, normalized melody fingerprint, and deterministic tie-break selection. Raw ABC remains in
memory and must never be printed, logged, embedded in exceptions, or committed.

## Parser contract

Reject empty bodies, lyrics (`W:`/`w:`), multi-voice notation (`V:` or `[V:`), unmatched quoted
text, unmatched grace/decorations, and fewer than eight parsed note events. Ignore header lines,
comments, quoted chord/annotation text, decorations, grace-note groups, rests, barlines, slurs,
ties, tuplets, broken-rhythm markers, and repeat/ending symbols. Repeats and alternate endings are
not unfolded. Inline key changes are rejected. Accidentals and key signatures do not affect the
diatonic feature representation. These limitations must be reported; no silent repair is allowed.

Map note letters and octave marks to an ordinal diatonic axis and derive adjacent directed diatonic
intervals transiently. Ordered notes and intervals are never exported.

## Frozen features

Publish exactly these nine aggregates, all clipped or naturally bounded to `[0,1]`:

1. `event_count_scaled = min(note_event_count, 256) / 256`;
2. `range_scaled = min(diatonic_range, 28) / 28`;
3. `ascending_proportion`;
4. `descending_proportion`;
5. `repeated_proportion`;
6. `step_proportion` for absolute interval 1;
7. `skip_proportion` for absolute interval 2 or 3;
8. `leap_proportion` for absolute interval at least 4;
9. `contour_change_rate`, the proportion of adjacent nonzero motion directions that change sign,
   or 0 when fewer than two nonzero motions exist.

Proportions 3–8 divide by the total adjacent-interval count. No data-dependent normalization is
permitted.

## Distance

`d[i,j] = (1/9) Σ_k (feature[i,k] - feature[j,k])^2`.

Distance is deterministic, symmetric, nonnegative, and bounded by 1. Publish features and distances
to 12 decimal places while retaining full binary floating-point values for verification.

These coarse aggregates are suitable for a research objective but omit rhythm, chromatic detail,
ornament realization, repeat unfolding, phrasing, cultural context, and provenance. They do not
prove musical identity, ancestry, authenticity, or reuse rights.
