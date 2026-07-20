# EXP-010A comparison with EXP-009A-R2

## R2 eight-qubit penalty encoding

- 8 logical qubits and 28 possible pair interactions;
- one-hot penalty `A=7`;
- 16 feasible states among 256;
- ideal feasible mass `0.9999270070068652`;
- conditional feasible distribution almost uniform;
- ideal feasible energy/probability Spearman rho
  `0.9441176470588234`, an unfavorable direction.

## EXP-010A compact encoding

- 4 logical qubits and 6 nonzero quadratic interactions;
- all 16 states valid;
- no penalty and no postselection;
- exactly the same 16 musical energies, optimum, and gap;
- ideal energy/probability Spearman rho
  `-0.9323529411764706`, a favorable negative direction;
- ideal relative expected-energy improvement
  `0.5999118429921135`.

Under the frozen p=1 protocols, the compact encoding produces genuine within-spectrum energy
ordering that the R2 penalty encoding did not. This encoding improvement is not quantum advantage
and does not predict hardware performance.
