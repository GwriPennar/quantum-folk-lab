# EXP-005A Current Qiskit Local QAOA Plan

Status: planned only. Do not treat this document as implementation evidence.

## Purpose

Replace or clearly separate the current deterministic pseudo-sampling path from a genuine local Qiskit QAOA experiment while preserving the existing non-Qiskit installation path. The eventual implementation must run locally only, require no IBM account, submit no hardware jobs, and continue to use the exact solver as the source of truth.

## Current-State Findings

Repository state inspected before writing this plan:

- `git status -sb`: clean `main` tracking `origin/main`.
- `git pull --ff-only`: already up to date.
- `git log -3 --oneline`: `9aab80a Initialize public quantum folk research project`.
- `python --version`: `Python 3.13.5`.
- `py -0p`: only `Python 3.13` was registered locally.

Current code behavior:

- `src/quantum_folk_lab/quantum/qaoa_local.py` contains no Qiskit circuit, primitive, sampler, ansatz, optimizer, transpiler, or simulator backend call.
- `run_local_qaoa()` enumerates every bitstring, evaluates exact QUBO energy, converts energies to softmax-like weights, and pseudo-samples with `random.Random(seed)`.
- The returned `best_bits` and `best_energy` are copied from the exact solver, not discovered by quantum optimization.
- The backend label is `local-softmax-simulator`, which is accurate, but the function and CLI names still imply QAOA too strongly.
- `src/quantum_folk_lab/qubo/qiskit_adapter.py` only checks that Qiskit can be imported and returns a simple coefficient dictionary. It is not a Qiskit converter.
- `qfl doctor` currently reports `qiskit`, `qiskit_aer`, and `qiskit_ibm_runtime` as not installed.
- `qfl compare --seed 42` currently reports exact recovery of `00001111` with family recovery `1.0`; the pseudo-sampling path reports the same exact best solution with `optimal_probability` around `0.50390625` for the default seed and shots.
- `tests/test_qaoa_smoke.py` checks only that the pseudo-sampler returns counts and that QPU execution requires confirmation.
- `README.md` says the initial QAOA runner is a tiny local simulator path and mentions deterministic pseudo-sampling, which is good, but the experiment table marks EXP-005 as complete and labels it “QAOA simulator,” which is too strong for the current implementation.
- `experiments/EXP-005-qaoa-simulator/README.md` is generic and marked complete; it should be revised to distinguish the existing classical fallback from genuine Qiskit QAOA.
- `EXP-001` and `EXP-002` are planned and generic; they do not yet demonstrate Qiskit circuits or a Max-Cut reference.
- CI installs only `.[dev]`; it does not install optional quantum dependencies or run quantum-specific tests.
- IBM setup documentation is appropriately simulator-first and says hardware execution requires explicit confirmation, but it does not yet explain the local Qiskit-only EXP-005A path.

Current commands that run without optional quantum dependencies:

```bash
python -m quantum_folk_lab.cli doctor
python -m quantum_folk_lab.cli generate-synthetic --seed 42
python -m quantum_folk_lab.cli solve-exact --seed 42
python -m quantum_folk_lab.cli solve-qaoa --seed 42
python -m quantum_folk_lab.cli compare --seed 42
pytest
ruff check .
ruff format --check .
mypy
python scripts/check_public_safety.py
```

Claims to correct during implementation:

- Do not call the current fallback QAOA.
- Rename user-facing labels to “classical fallback sampler” or equivalent.
- Mark EXP-005 as “fallback complete / Qiskit QAOA planned” until genuine Qiskit execution lands.
- Keep all wording cautious: no quantum advantage, no hardware implication, no automatic superiority claim.

## Current Qiskit API Review

Official and package sources checked for planning:

- IBM Quantum Qiskit installation guide: <https://docs.quantum.ibm.com/guides/install-qiskit>
- Qiskit `StatevectorSampler` API: <https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.StatevectorSampler>
- Qiskit `QAOAAnsatz` API: <https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.QAOAAnsatz>
- Qiskit Algorithms `QAOA` API: <https://qiskit-community.github.io/qiskit-algorithms/stubs/qiskit_algorithms.QAOA.html>
- Qiskit Optimization `MinimumEigenOptimizer` API: <https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.algorithms.MinimumEigenOptimizer.html>

Package metadata checked with `pip index versions` and PyPI JSON on 2026-06-30:

- `qiskit==2.4.2`, `requires_python >=3.10`; classifiers include Python 3.13 and 3.14.
- `qiskit-aer==0.17.2`, `requires_python >=3.7`; a dry-run found a `cp313` Windows wheel.
- `qiskit-algorithms==0.4.0`, `requires_python >=3.9`; classifiers include Python 3.13.
- `qiskit-optimization==0.7.0`, `requires_python >=3.9`; classifiers include Python 3.13.

Dry-run resolution on the local Python 3.13 interpreter succeeded for:

```bash
python -m pip install --dry-run "qiskit==2.4.2" "qiskit-aer==0.17.2" "qiskit-algorithms==0.4.0"
```

`qiskit-optimization==0.7.0` also resolved, but it pulls in `docplex` and `networkx`; that is more machinery than the repository needs for the first genuine local QAOA path.

## API Route Evaluation

### Route A: `qiskit_algorithms.QAOA` with a Current Local Sampler

Pros:

- Smallest conceptual step from “QAOA” as an algorithm to a runnable local implementation.
- Uses a maintained package intended for algorithms.
- Keeps optimizer, sampler, and result interpretation explicit enough for a learning repository.
- Avoids introducing `qiskit-optimization` and `docplex` for an eight-variable hand-built QUBO.

Cons:

- Need to convert the project QUBO into a supported operator form cleanly.
- Need to confirm the exact sampler class expected by `qiskit_algorithms.QAOA` in the installed package version.

### Route B: `qiskit_optimization.MinimumEigenOptimizer`

Pros:

- Purpose-built route for quadratic programs and minimum-eigen solvers.
- May reduce custom conversion code once the `QuadraticProgram` is built.

Cons:

- Adds `qiskit-optimization`, `docplex`, and extra abstraction before the repository needs them.
- Hides too much of the QUBO-to-Ising/QAOA path for the current educational goal.
- More CI/package surface for a first quantum optional test.

### Route C: Direct `QAOAAnsatz` with Current Primitives

Pros:

- Most transparent educational route: construct cost operator, build ansatz, run local sampler, inspect bitstrings.
- Avoids `qiskit_optimization` and its heavier dependencies.
- Makes circuit width/depth and parameter handling visible.

Cons:

- Requires writing a small optimization loop and careful bit-order tests.
- Slightly more project code than using `qiskit_algorithms.QAOA` directly.

## Chosen Primary Route

Use Route C first: a direct `QAOAAnsatz` implementation with current Qiskit primitives and local simulation. Keep Route A as a secondary comparison path if `qiskit_algorithms.QAOA` integrates cleanly after package installation.

Reasoning:

- The repository’s purpose is educational transparency, not hiding the optimization behind a convenience wrapper.
- The QUBO is already provider-independent and tiny, so a direct conversion to an Ising cost operator is manageable and testable.
- The direct route makes it easier to report circuit depth, width, sampler counts, bit ordering, objective value, and exact-solver comparison.
- It avoids `qiskit-optimization` for EXP-005A, reducing dependency and CI risk.

The implementation should still document why `MinimumEigenOptimizer` is deferred and may be useful later for larger or more standard quadratic-program workflows.

## Proposed Virtual-Environment Setup

Prefer a dedicated quantum environment, separate from the existing validated dev environment.

Recommended Python version: Python 3.12 for first CI-grade reproducibility, because it is broadly supported across Qiskit, Aer, SciPy, and compiled wheels. Python 3.13 can be tested locally because dry-run resolution succeeded, but it should not be the only documented path until CI proves it.

PowerShell with Python 3.12 installed:

```powershell
py -3.12 -m venv .venv-qiskit
.\.venv-qiskit\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,quantum]"
python -m quantum_folk_lab.cli doctor
```

Fallback on this machine if Python 3.12 is unavailable:

```powershell
py -3.13 -m venv .venv-qiskit
.\.venv-qiskit\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,quantum]"
```

Do not install IBM Runtime for EXP-005A. Do not configure IBM credentials.

## Dependency Changes

Update optional quantum dependencies to a tested, current set. Proposed initial pins or lower-bounds after implementation verification:

```toml
quantum = [
  "qiskit>=2.4,<3",
  "qiskit-aer>=0.17,<0.18",
  "qiskit-algorithms>=0.4,<0.5",
]
```

Possible additional dependency:

- `scipy` may be required explicitly if using `scipy.optimize.minimize` for the direct ansatz loop. Qiskit already depends on SciPy, but the project should declare it directly if project code imports it.

Do not add `qiskit-optimization` for EXP-005A unless implementation reveals that the direct route becomes less clear than expected.

## Files to Change in the Eventual Implementation

Expected code files:

- `src/quantum_folk_lab/quantum/qaoa_local.py`: split current pseudo-sampler into an explicitly named classical fallback and add a genuine Qiskit runner or route to a new module.
- `src/quantum_folk_lab/quantum/qaoa_qiskit.py`: new module for Qiskit-only local QAOA, imported lazily.
- `src/quantum_folk_lab/qubo/qiskit_adapter.py`: add QUBO-to-Ising/SparsePauliOp conversion and bit-order helpers.
- `src/quantum_folk_lab/cli.py`: expose clear commands or flags such as `solve-qaoa --backend qiskit-local` and `solve-fallback-sampler` or `solve-qaoa --backend classical-fallback` with honest labels.
- `src/quantum_folk_lab/utils/reproducibility.py`: report `qiskit`, `qiskit_aer`, and `qiskit_algorithms` versions.
- `src/quantum_folk_lab/evaluation/reporting.py`: centralize result schema if output grows.

Expected tests:

- Keep existing non-quantum tests working without Qiskit.
- Rename or adjust the current QAOA smoke test so it tests the classical fallback honestly.
- Add `tests/test_qiskit_qaoa_smoke.py` marked with `pytest.mark.quantum` and skipped when optional quantum dependencies are unavailable.
- Add bit-order and energy-consistency tests for QUBO-to-Ising conversion.

Expected docs:

- `README.md`
- `experiments/EXP-005-qaoa-simulator/README.md`
- `docs/mathematical_model.md`
- `docs/architecture.md`
- `docs/ibm_quantum_setup.md`
- This plan may be moved or linked from EXP-005 when implementation starts.

Expected CI:

- `.github/workflows/ci.yml`: keep the current lightweight job unchanged or nearly unchanged.
- Add a separate optional quantum job, possibly manual or path-triggered first, installing `.[dev,quantum]` and running only `pytest -m quantum` plus a tiny smoke command.

## Result Schema

The genuine Qiskit result should be separate from exact and fallback results. Proposed JSON shape:

```json
{
  "exact": {
    "bits": [0, 0, 0, 0, 1, 1, 1, 1],
    "energy": 0.0,
    "family_recovery": 1.0,
    "evaluated": 128
  },
  "classical_fallback_sampler": {
    "enabled": true,
    "backend": "classical-softmax-fallback",
    "best_bits": [0, 0, 0, 0, 1, 1, 1, 1],
    "best_energy": 0.0,
    "optimal_probability": 0.5,
    "shots": 256,
    "seed": 42
  },
  "qiskit_qaoa": {
    "enabled": true,
    "backend": "qiskit-local-statevector" ,
    "packages": {
      "qiskit": "2.4.2",
      "qiskit_aer": "0.17.2",
      "qiskit_algorithms": "0.4.0"
    },
    "depth_p": 1,
    "shots": 1024,
    "seed": 42,
    "optimizer": "COBYLA or scipy-minimize",
    "parameters": {
      "gamma": [0.0],
      "beta": [0.0]
    },
    "best_bits": [0, 0, 0, 0, 1, 1, 1, 1],
    "best_energy": 0.0,
    "family_recovery": 1.0,
    "optimal_probability": 0.0,
    "counts": {
      "00001111": 0
    },
    "circuit": {
      "width": 8,
      "depth": 0,
      "two_qubit_gates": 0
    }
  }
}
```

The exact field values above are illustrative; implementation must fill them from actual execution.

## Test Strategy

Non-quantum default tests:

- Continue to run without Qiskit installed.
- Verify deterministic synthetic generation, similarity, QUBO energy, exact solver, family recovery, fallback sampler, and public safety.
- Verify importing Qiskit modules fails with a helpful optional-dependency message when not installed.

Quantum-specific tests:

- Mark with `pytest.mark.quantum`.
- Skip cleanly if Qiskit optional dependencies are missing.
- Use the existing eight-variable benchmark unless runtime proves too slow; if too slow, use a four-variable fixture only for smoke testing while keeping the eight-variable benchmark as the registered success configuration.
- Test QUBO-to-Ising conversion by checking energies for every bitstring against `QUBOModel.energy()` up to a tolerance.
- Run a tiny Qiskit local sampler test with fixed seed and shallow `p=1`.
- Assert at least one registered configuration recovers an optimal partition on the eight-variable benchmark.
- Assert no IBM Runtime package or credentials are required.

## Exact Validation Commands

Default non-quantum validation:

```bash
python -m pip install -e ".[dev]"
python -m quantum_folk_lab.cli doctor
python -m quantum_folk_lab.cli compare --seed 42
ruff check .
ruff format --check .
mypy
pytest
python scripts/check_public_safety.py
```

Quantum environment validation:

```bash
python -m pip install -e ".[dev,quantum]"
python -m quantum_folk_lab.cli doctor
python -m quantum_folk_lab.cli solve-exact --seed 42
python -m quantum_folk_lab.cli solve-qaoa --backend classical-fallback --seed 42
python -m quantum_folk_lab.cli solve-qaoa --backend qiskit-local --seed 42 --depth 1 --shots 1024
pytest -m quantum
python scripts/check_public_safety.py
```

CI validation after implementation:

```bash
pytest -m "not quantum"
pytest -m quantum
```

## Documentation Corrections

- README should describe three separate paths: exact classical, classical fallback sampler, and genuine local Qiskit QAOA.
- Rename “local simulator QAOA” language where it refers to the current fallback.
- EXP-005 should state that genuine Qiskit QAOA is complete only after a real Qiskit circuit and sampler run.
- The CLI help should say which backends require optional quantum dependencies.
- IBM setup should remain separate and clearly say EXP-005A requires no IBM account, no token, and no QPU access.
- Any approximation ratio should be framed carefully because the current objective is minimization and the optimum can be numerically near zero; normalized optimality gap may be clearer.

## CI Strategy for Optional Quantum Dependencies

Keep the default CI job small and dependency-light:

- Install `.[dev]`.
- Run lint, format check, mypy, non-quantum pytest, and safety scan.

Add a separate quantum job after local verification:

- Install `.[dev,quantum]` on Python 3.12 first.
- Run `pytest -m quantum`.
- Run exactly one CLI Qiskit smoke command with small shots and fixed seed.
- Do not install `qiskit-ibm-runtime`.
- Do not read any IBM environment variables.
- Do not run on every docs-only change if CI time becomes an issue.

## Rollback Approach

- Preserve the existing classical fallback under a new honest name, so rollback does not remove a working local demo.
- Keep Qiskit imports lazy and optional.
- Add the genuine Qiskit code in a separate module so it can be disabled by CLI backend selection if dependencies fail.
- If the quantum job proves flaky, keep the code but mark the CI quantum job manual or nightly until stabilized.
- Revert only the Qiskit-specific module, optional dependency changes, CLI backend wiring, and docs updates if needed; exact solver and QUBO core should remain untouched.

## Stop Conditions

Stop implementation and ask for human input if any of these occur:

- Installing optional quantum dependencies requires unsupported Python or fails without a clear compatible interpreter.
- Current Qiskit APIs differ materially from the planned route.
- Qiskit execution attempts to require IBM Runtime credentials or a cloud backend.
- The eight-variable benchmark cannot recover an optimum under any reasonable shallow local configuration and the docs would need a changed success claim.
- Bit ordering between Qiskit results and project variables cannot be proven with exhaustive tests.
- Any command would publish credentials, local account metadata, private paths, or hardware job identifiers.
- A code change would require deleting the CI workflow or weakening the public safety boundary.

## Privacy and Credential Checks

- Use synthetic data only.
- Do not add IBM tokens, API keys, `.env` files, backend account identifiers, job IDs, or local account metadata.
- Do not run IBM Runtime, list cloud backends, or submit QPU jobs for EXP-005A.
- Keep generated results under ignored local results paths unless they are tiny, synthetic, reviewed, and intentionally committed.
- Run `python scripts/check_public_safety.py` before any commit.
- Run `git status -sb` and review staged files explicitly before any future commit.
