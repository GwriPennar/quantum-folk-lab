# Backend and layout selection rule

Live selection is deferred. A supplied snapshot is filtered, in order, for operational non-simulator hardware, at least four usable qubits, successful transpilation, two-qubit count <= 24, two-qubit depth <= 18, total depth <= 120, duration <= 150 microseconds, mean mapped two-qubit error <= 0.02, mean readout error <= 0.05, and no unavailable mapped qubits/couplers.

Survivors are sorted lexicographically by: two-qubit count, two-qubit depth, total depth, duration, mapped two-qubit error, mapped readout error, estimated usage, backend identifier, then layout tuple. These gates and tie-breakers are frozen before any live query. EXP-010B tests only synthetic fixture snapshots and names no real backend.
