# Bit-order contract

Compact strings are displayed in logical-variable order `q0 q1 q2 q3`. Measurements map `qi -> ci`. Qiskit count keys print `c3 c2 c1 c0`, so ingestion removes spaces and reverses each four-bit key exactly once. All sixteen displayed strings are retained; missing strings receive count zero.
