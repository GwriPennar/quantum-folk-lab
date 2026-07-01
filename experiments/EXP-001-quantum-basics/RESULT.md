# EXP-001 Results

Recorded with local Qiskit/Aer simulation only. No IBM account, token, Runtime service, cloud backend, or QPU was used.

## Environment

- Python: 3.13.5
- Qiskit: 2.4.2
- Qiskit Aer: 0.17.2
- Simulator: local `AerSimulator`
- `seed_simulator`: 42
- `seed_transpiler`: 42

## Registered Circuit Results

| Experiment | Shots | Depth | Transpiled depth | Counts | Empirical probabilities | Decision |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `zero` | 1024 | 1 | 1 | `0: 1024` | `P(0)=1.0` | pass |
| `x` | 1024 | 2 | 2 | `1: 1024` | `P(1)=1.0` | pass |
| `hadamard` | 4096 | 2 | 2 | `0: 2022`, `1: 2074` | `P(0)=0.49365234375`, `P(1)=0.50634765625` | pass |
| `double-hadamard` | 1024 | 3 | 1 | `0: 1024` | `P(0)=1.0` | pass |
| `bell` | 4096 | 3 | 3 | `00: 2009`, `11: 2087` | `P(00)=0.490478515625`, `P(11)=0.509521484375` | pass |

The full registered run also includes `z-zero` and `z-after-h` in `results/basics-run-all-4096.json`.

## Interpretation

The `zero`, `x`, and `double-hadamard` circuits are deterministic in an ideal simulator. The Hadamard circuit creates equal amplitudes for `|0>` and `|1>`, so repeated measurement gives an approximately balanced distribution. The Bell circuit creates an entangled state with correlated outcomes: `00` and `11` appear, while `01` and `10` remain absent in ideal simulation.

The `z-zero` and `z-after-h` circuits show the phase lesson. Applying `Z` to `|0>` does not change direct measurement. Applying `Z` after `H` changes the relative phase of the `|1>` amplitude, but direct computational-basis measurement remains near 50/50 because phase becomes visible only through later interference.

## Reproducibility Commands

```bash
python -m quantum_folk_lab.cli basics-list
python -m quantum_folk_lab.cli basics-run --experiment zero --shots 1024
python -m quantum_folk_lab.cli basics-run --experiment x --shots 1024
python -m quantum_folk_lab.cli basics-run --experiment hadamard --shots 4096
python -m quantum_folk_lab.cli basics-run --experiment double-hadamard --shots 1024
python -m quantum_folk_lab.cli basics-run --experiment bell --shots 4096
python -m quantum_folk_lab.cli basics-run-all --shots 4096
```

## Limitations

These are ideal simulator results. They do not represent hardware noise, decoherence, queueing, readout error, calibration drift, or real backend topology. EXP-002 will introduce a small Max-Cut reference problem. EXP-005A remains planned future work for genuine local QAOA on the tune-family QUBO.
