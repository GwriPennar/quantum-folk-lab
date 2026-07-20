# EXP-010B protocol

Protocol-only readiness study inherited from EXP-010A squash `461375818af7f512557003e1348054b5539a150d`.

No IBM service, credential, backend query, Runtime session, or hardware submission is permitted in EXP-010B. The frozen circuit uses 4 Hadamards, the normalized Ising phase separator, 4 mixer rotations, and measurements. Angles are not retuned. Local evidence uses 4,096 shots and seed 42.

The primary metric is `R=(E_uniform16-E_observed)/(E_uniform16-E_min)`. Missing states have zero counts. The one-sided uniform-null test uses alpha 0.05 and the precomputed 95th-percentile threshold. Secondary metrics cannot override the primary conclusion.
