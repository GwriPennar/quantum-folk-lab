Exit code: 0
Wall time: 1.4 seconds
Output:
# EXP-010C IBM hardware result

The single authorized IBM Runtime job `d9eq7faneu4c739oohf0` completed on `ibm_fez`. It returned the frozen QAOA PUB followed by the frozen uniform-control PUB, each with 4,096 shots. No second job was submitted and no automatic retry occurred.

## Validation

- Frozen evidence commit: `ca7a6755568bd19792513941403c4052bd9ad23f`
- Physical layout: `[20, 21, 23, 22]`; transpiler seed: `44`
- QAOA QPY SHA-256: `7f7a811c5175496127db698a50e02d1d950180519cc33dfaf7ec9f577f0c1e0b`
- Control QPY SHA-256: `1cdf53e347c15f8b469f7ab2b8fe094f61dce65316f488b7aee1724f0f56bda8`
- Bit order: Qiskit returned classical strings as `c3..c0`; each string was explicitly reversed to frozen logical order `x0..x3` before energy evaluation.

## Primary result

| PUB | Mean energy | Energy SE | R | Bootstrap 95% R interval | P(1010) | Most likely logical state |
|---|---:|---:|---:|---:|---:|---|
| Hardware QAOA | 0.041761239718 | 0.000109531239 | 0.514933137707 | [0.503183709927, 0.526602031846] | 0.241699 | `1010` |
| Uniform control | 0.051388105938 | 0.000142884585 | -0.021308509045 | [-0.036808363911, -0.005446518393] | 0.054932 | `0000` |

`R_QAOA - R_control = 0.536241646752`. Frozen comparisons: ideal simulator `R = 0.5902006485219975`, synthetic stress `R = 0.40598082920880263`, and uniform-null threshold `R = 0.013243523204876345`.

## Interpretation

Hardware QAOA beats the frozen uniform control and clears the frozen one-sided null threshold. The optimum `1010` remains the most likely QAOA state. Relative to ideal simulation, hardware noise weakens concentration; the complete state table in `hardware-counts.json` records whether the ranking changed. Under the predeclared primary procedure, the narrow hardware-validation hypothesis is supported.

This is a controlled hardware validation of a tiny frozen experiment. It is not evidence of quantum advantage, speedup, superiority over exact classical search, general hardware performance, or commercial usefulness.
