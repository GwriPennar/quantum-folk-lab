# EXP-009A-R2 local detectability protocol

Frozen: 2026-07-19, after the local-QAOA result was preserved and before detectability execution.

- 10,000 multinomial alternative resamples from the frozen ideal p=1 distribution;
- 10,000 multinomial null resamples from the uniform distribution over all 256 states;
- 4096 shots per resample;
- NumPy random seed 42 with one deterministic generator;
- significance level 0.05;
- alternative uncertainty reported as 2.5%, 50%, and 97.5% empirical quantiles plus standard
  deviation.

Predeclared favorable directions and null critical thresholds:

- feasible-subspace mass: higher than the null 95th percentile;
- optimum-class mass: higher than the null 95th percentile;
- four-lowest-feasible-state mass: higher than the null 95th percentile;
- expected energy: lower than the null 5th percentile;
- feasible-state probability versus exact-energy Spearman ρ: lower than the null 5th percentile,
  because useful energy ranking assigns more probability to lower-energy states.

Estimated power is the fraction of alternative resamples crossing the applicable null threshold.
A metric is labelled detectable only when estimated power is at least 0.80. Detectability does not
make a metric scientifically primary, does not establish useful energy ranking, and does not
authorize hardware access.
