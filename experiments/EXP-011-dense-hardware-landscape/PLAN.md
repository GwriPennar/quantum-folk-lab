# EXP-011 dense hardware landscape replication

EXP-011 is a predeclared 9×9 replication and resolution study of the governed four-qubit EXP-010D circuit. Exact classical evaluation remains authoritative. No quantum advantage, speedup, generalisation, or commercial superiority is claimed.

The frozen workload contains 88 PUBs at 4,096 shots: 80 non-centre cells once, four centre executions, and four zero-angle controls. One IBM job and zero retries are permitted only after a passing merged preflight and the exact authorization phrase.

Primary analysis uses average-rank Spearman correlation across 81 aggregated cells, 100,000 one-sided permutations and a 10,000 paired-cell percentile bootstrap, all with seed 20260720. Thresholds are: strongly replicated rho >= 0.80 and p < 0.01; replicated rho >= 0.50 and p < 0.05; weak or inconclusive rho > 0 otherwise; not replicated rho <= 0. The declared repeatability, control, cross-run, subset, TV-distance and drift analyses are secondary and cannot replace the primary result.
