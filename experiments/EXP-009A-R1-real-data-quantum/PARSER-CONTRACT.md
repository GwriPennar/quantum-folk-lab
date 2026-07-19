# EXP-009A-R1 parser contract

Frozen: 2026-07-19, before successor access to the eight selected real-data records.

EXP-009A-R1 is a successor motivated by EXP-009A's valid fail-closed rejection of an inline key
field. It is not a blind preregistration. EXP-009A remains historically unchanged.

## Representation boundary

The representation is diatonic. It uses parsed written note letters, octave marks, and aggregate
event and contour measurements. It does not model sounding chromatic pitch, semitone intervals,
harmonic function, modulation, mode changes, or accidental interpretation under a key signature.

## Frozen inline-field policy

1. Header `K:` lines are metadata and are excluded from the note-event stream.
2. A well-formed inline `[K:...]` field is non-note metadata and is removed completely before note
   tokenisation.
3. Text inside `[K:...]` is never interpreted as note events.
4. Written note letters and octave marks before and after a removed field remain unchanged.
5. Explicit accidentals remain ignored exactly as in EXP-009A's diatonic representation.
6. Inline key fields do not alter the nine frozen feature definitions.
7. The number of inline key fields is counted per setting and may be reported; field content must
   never be printed, logged, or committed.
8. Malformed or unterminated inline fields fail closed without including notation in the error.
9. Multi-voice `[V:...]`, lyrics, empty records, unmatched markup, and insufficient note counts
   remain rejected.
10. Every other inline field must have a predeclared non-note policy or fail closed. No unknown
    inline field is silently stripped.

The policy is general. It contains no tune-, setting-, source-, row-, or collection-specific
exception.

## Safety invariants

Parsing returns only the nine aggregate features and the inline-key-field count. Raw ABC, inline
field content, ordered notes, and interval sequences are transient and must not appear in output,
exceptions, logs, or committed evidence.

