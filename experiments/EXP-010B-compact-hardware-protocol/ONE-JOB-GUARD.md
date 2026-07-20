# One-job guard

Hardware submission defaults off and requires both `--submit-hardware` and exact phrase `I AUTHORIZE ONE IBM QPU JOB`. Before any credential reader or Runtime factory can run, software verifies coefficient hashes, exact frozen angles, passed equivalence evidence, backend/layout gates, and absence of both an intent and a receipt.

Intent and receipt records use restrictive, durable exclusive creation: write, flush, file `fsync`, and best-effort directory sync. They are never overwritten, deleted, renamed, or automatically repaired. A pre-existing intent means submission was attempted and may have succeeded even if no receipt exists. It therefore blocks all later attempts until a human reconciles it against IBM job history. Any exception after intent creation preserves that ambiguous-outcome boundary and prohibits automatic retry.

The intent records the experiment and schema, unique attempt ID, UTC timestamp, inherited evidence, frozen angles, branch commit, backend snapshot, layout, transpiled circuit hashes, shots and PUB count. The receipt binds the returned job ID to that same attempt. Neither record contains credentials or external exception text. Tests use injected mocks only and never instantiate an IBM service.

Current status: `READY TO BEGIN READ-ONLY IBM PREFLIGHT`. Live backend selection, calibration inspection and final ISA-circuit freezing must precede any explicit authorization of the single QPU job.
