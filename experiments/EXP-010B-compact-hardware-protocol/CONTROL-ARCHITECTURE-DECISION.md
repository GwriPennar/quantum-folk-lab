# Control architecture decision

| Option | PUBs | Shots/PUB | Diagnosis | Decision |
|---|---:|---:|---|---|
| QAOA plus analytic uniform null | 1 | 4096 | signal only | insufficient measurement diagnosis |
| QAOA plus zero-angle uniform control | 2 | 4096 | signal, null, gross measurement/implementation failure | selected |
| QAOA plus identity control | 2 | 4096 | narrow measurement check | weaker null comparison |
| Eight-qubit legacy control | >=2 | 4096 | unrelated positive control | rejected |

The selected eventual single job contains two PUBs: the frozen compact circuit and a same-width zero-angle uniform control. It adds one shallow circuit without changing the primary hypothesis or routing depth of the primary circuit.
