# EXP-010D statistical analysis plan

## Primary analysis

Aggregate the four centre executions into one centre distribution and one centre R estimate,
giving 25 unique parameter cells. Compute Spearman rank correlation between ideal R and hardware
R using average ranks for ties. Use a one-sided permutation test with seed `20260720`, 100,000
permutations, and p-value `(1 + count(rho_permuted >= rho_observed)) / 100001`.

- `LANDSCAPE SUPPORTED`: rho >= 0.5 and p < 0.05.
- `WEAK OR INCONCLUSIVE`: rho > 0 but either condition fails.
- `LANDSCAPE NOT SUPPORTED`: rho <= 0.

Missing or malformed PUB results make the primary result inconclusive; no cell is omitted and no
observation is rerun. A 95% percentile confidence interval uses 10,000 paired-cell bootstrap
resamples with seed `20260720`. Ties retain average-rank handling in every recomputation.

## Secondary analyses

Report without overriding the primary result: centre rank and top-three status; centre R minus
outer-ring median R and whether it exceeds 0.10; best hardware cell and displacement; four centre
R values with mean, sample SD and range; four control R values with mean, sample SD and range;
four blockwise centre-minus-control differences; a 10,000-resample percentile bootstrap interval
for aggregate centre minus control using seed `20260720`; P(`1010`), most-likely state and
hardware-versus-ideal total-variation distance for every cell; and block-order drift evidence.

Raise a control-quality warning when `abs(mean control R) > 0.05`. Raise a repeatability warning
when centre sample SD exceeds `0.05`. Warnings never permit exclusion, replacement, or rerunning.

All metrics use the frozen bit order, energy evaluator and R definition. No post-hoc threshold,
grid change, optimisation claim, quantum-advantage claim, or speedup claim is permitted.
