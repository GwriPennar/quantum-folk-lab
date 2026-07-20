# EXP-010C read-only IBM preflight

The preflight failed closed before backend discovery because the existing environment had no saved default `ibm_quantum_platform` account available to `QiskitRuntimeService()`.

No token, saved-account dictionary, credential file, CRN, environment variable, backend, primitive, session, batch, intent, receipt, or job was inspected or created. No IBM workload was submitted.

Decision: `BLOCKED — IBM PREFLIGHT COULD NOT BE COMPLETED SAFELY`.
