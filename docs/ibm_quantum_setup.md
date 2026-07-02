# IBM Quantum Setup

EXP-001 and EXP-002 do not use IBM Quantum services. They run real Qiskit circuits on local simulators and requires no IBM account, no token, no Runtime service, no secrets, and no QPU job.

For EXP-001 and EXP-002 install only local simulator dependencies:

```bash
python -m pip install -e ".[dev,quantum]"
```

The optional IBM path remains future work. If hardware support is added later, it must require explicit confirmation, show circuit resources and requested shots before submission, avoid tests and CI, and redact account or job metadata from committed results.

Never commit IBM tokens, account files, `.env` files, backend credentials, or job dumps.
