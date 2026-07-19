# AlawArchwilio read-only audit

AlawArchwilio is pre-existing private, user-owned work. Its clean local `main` was inspected at
`b3b50aa0b6459375791a5842e4fc959dcb7aa4a0`. Configured origin is
`GwriPennar/folk-tune-finder.git`, not the supplied `GwriPennar/AlawArchwilio`; neither was changed.

The relevant database technology is Parquet: a 182,133-row, 37-column Press-derived corpus and a
separate 528-row, 16-column Alawon Cymru corpus. Relevant fields include stable local `ID`, source-
local `X`, title `T`, type `R`, meter `M`, key `K`, provenance/transcriber fields, and ABC `body`.
The Alawon Cymru schema additionally has `also_known_as` and `source`, but the eight candidates are
Press records. `X` is not globally unique. There is no authoritative family relationship table,
O'Neill printed/scan-page field, or verified rights field.

Route A fails for publication because stored ABC provenance and reuse rights are insufficient.
Route B passes for controlled computation: stable IDs identify candidates and exact normalized
fingerprints link them to external IrishMAN rows. Route C remains the redistribution posture: no
local or IrishMAN ABC is approved for publication. The repository and Parquets were not modified.
