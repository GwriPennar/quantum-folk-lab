# Circuit contract

Logical qubits `q0..q3` are Blackbird, Bold Deserter, Catherine Tyrrell, and The Merry Old Woman. Apply `H` to each. With normalized coefficients `h'=h/range`, `J'=J/range`, apply `RZ(2*gamma*h'_i)` for each of four nonzero linear terms and `RZZ(2*gamma*J'ij)` for each of six nonzero interactions. Qiskit defines these gates as `exp(-i theta Z/2)` and `exp(-i theta ZZ/2)`. The omitted constant is one irrelevant global phase. Apply `RX(2*beta)` to every qubit, then measure `qi` into `ci`.

Frozen values: gamma `3.3177975191929154`, beta `2.476505299986026`, range `0.031425180740004`, QUBO hash `96cfa65ca023ef7dc7449ce4b8ef132f0cbd2bbfc035f357d19f55431b3bb86e`, Ising hash `635c8f05ccc4878e7f9fffad62ddd302e0a29aed4ee5837acefbc9be308a3fd5`.

Pre-transpile logical counts: H 4, RZ 4, RZZ 6, RX 4, measure 4. No postselection.
