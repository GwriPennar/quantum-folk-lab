# Deterministic selection method

Candidate ABC is read from the pre-existing AlawArchwilio Parquet and IrishMAN from an explicitly
supplied, hash-verified external cache. Bodies remain in memory and are never logged or committed.

The matcher removes ABC headers, comments, chord text, decorations, grace groups, and inline fields;
derives adjacent diatonic intervals; and SHA-256 hashes that transposition-invariant representation.
Hashed interval 2–4-gram frequency cosine supplies a sensitivity score without exporting an ordered
sequence. Selection requires exact fingerprint equality and cosine `1.0`; approximate matches are
not accepted silently.

Tie-break: exact matches only, `train` before `validation`, then lowest zero-based row index. The raw
record hash uses UTF-8 JSON with sorted keys, no optional whitespace, and preserved non-ASCII text.
Hashes identify inspected records but establish no copyright status.

This fingerprint ignores accidentals, rhythm, ornaments, and cultural context and can collide.
Family labels therefore remain provisional and require human source/musical review.
