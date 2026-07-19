# EXP-009A-R2 parser contract

Frozen: 2026-07-19, before R2 access to the eight selected real-data records.

EXP-009A-R2 is motivated by the complete non-disclosing structural inventory produced by R1. It
is not a blind preregistration. The EXP-009A and EXP-009A-R1 NO-GO outcomes remain unchanged.

## Representation boundary

The inherited representation uses written note letters, octave marks, event count, diatonic range,
directional interval proportions, step/skip/leap proportions, and contour-change rate. It does not
model sounding chromatic pitch, key-signature interpretation, meter, note duration, rhythmic
weighting, tempo, harmonic function, modulation, or playback timing.

## Closed metadata policy

Normal header information fields remain excluded from the music-note stream. Only these
well-formed inline fields may be removed before note tokenisation:

- `[K:...]`, because the representation does not model key-dependent chromatic meaning;
- `[M:...]`, because the representation does not model meter or durations;
- `[Q:...]`, because the representation does not model tempo.

The whitelist is closed. It must not be reused automatically for a rhythm-aware, duration-aware,
chromatic, or playback experiment.

## Required invariants

1. K, M, and Q contents never reach the note tokenizer or generate note events.
2. Written note letters and octave marks surrounding removed fields remain unchanged.
3. Removal does not alter the nine inherited features except by preventing metadata text from
   being misread as notes.
4. K, M, and Q fields are counted separately for every setting. Counts and tags may be reported;
   contents must never be printed, logged, exported, or committed.
5. Malformed, nested, or unterminated inline fields fail closed.
6. Every inline tag other than exactly K, M, or Q fails closed. Inline V remains rejected.
7. Lyrics, macros, user-defined symbols, empty records, unmatched markup, and insufficient note
   counts remain rejected.
8. No tune-, row-, family-, title-, source-, or collection-specific exception is permitted.
9. The parser must never silently repair notation.

Parsing returns only nine aggregate features and separate K/M/Q counts. Raw ABC, metadata content,
ordered notes, and ordered intervals remain transient and non-disclosable.
