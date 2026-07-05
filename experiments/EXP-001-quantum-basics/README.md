# EXP-001 Quantum Basics

Status: complete

EXP-001 is a local, noise-free Qiskit/Aer reference experiment. It validates circuit construction, computational-basis measurement, X/H/Z gates, superposition, finite-shot sampling, and Bell-state entanglement before the project moves into Max-Cut or music-inspired QUBO work.

No IBM account, token, Runtime service, cloud backend, or QPU is used.

## Validation Goals

- Represent a qubit as amplitudes over `|0>` and `|1>`.
- Connect amplitudes to measurement probabilities.
- Inspect small Qiskit circuits before and after transpilation.
- Compare deterministic basis-state outcomes with probabilistic superposition outcomes.
- See why `H` creates superposition and why `H` followed by `H` returns to the starting basis state.
- Understand that `Z` changes phase, which may not alter direct computational-basis measurement probabilities.
- Build and sample a Bell state whose results are correlated, not merely two independent 50/50 bits.

## Circuits

| Name | Circuit | Expected ideal behaviour |
| --- | --- | --- |
| `zero` | measure `|0>` | all shots return `0` |
| `x` | `X` then measure | all shots return `1` |
| `hadamard` | `H` then measure | `0` and `1` appear near 50/50 |
| `double-hadamard` | `H`, `H`, measure | all shots return `0` |
| `z-zero` | `Z` on `|0>`, measure | all shots return `0` |
| `z-after-h` | `H`, `Z`, measure | still near 50/50; phase is hidden without interference |
| `bell` | `H(0)`, `CX(0,1)`, measure both | only `00` and `11`, near balanced |

## Reproducibility

PowerShell:

```powershell
py -3.13 -m venv .venv-qiskit
.\.venv-qiskit\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,quantum]"
qfl doctor
qfl basics-list
qfl basics-run --experiment zero --shots 1024
qfl basics-run --experiment x --shots 1024
qfl basics-run --experiment hadamard --shots 4096
qfl basics-run --experiment double-hadamard --shots 1024
qfl basics-run --experiment bell --shots 4096
qfl basics-run-all --shots 4096
```

Equivalent module form:

```bash
python -m quantum_folk_lab.cli basics-run-all --shots 4096
```

## Interpretation

The simulator is ideal and noise-free. Deterministic circuits should produce a single basis-state result. Superposition circuits produce probabilities, so finite-shot counts vary slightly even with a fixed simulator seed. The Bell state validates correlation: measuring one qubit determines the other in the same shot, so `01` and `10` are absent in the ideal result.

## Results

See `RESULT.md` and the JSON files under `results/`.
