# Statistical analysis plan

The primary estimator is the raw R2 energy mean over all 4,096 shots and `R=(E_uniform16-E_hardware)/(E_uniform16-E_min)`. The one-sided null is multinomial uniform over 16 states, alpha 0.05, frozen Monte Carlo seed 42 and 100,000 resamples. Positive signal requires `R>0` and `R` above the frozen null critical value. `R<0` is negative; otherwise signal is not detected. A 95% percentile multinomial-bootstrap interval (10,000 resamples, seed 42) quantifies uncertainty.

Secondary outputs are optimum mass, four-lowest mass, raw and normalized expected energy, energy/probability Spearman, TV distance from uniform, TV distance from ideal, and all 16 counts. Missing strings are zero. Secondary results never override the primary result and the most frequent state alone is never a success criterion.
