# One-job guard

Hardware submission defaults off and requires both `--submit-hardware` and exact phrase `I AUTHORIZE ONE IBM QPU JOB`. Before any credential reader or Runtime factory can run, software verifies coefficient hashes, exact frozen angles, passed equivalence evidence, backend/layout gates, and absence of a receipt. It writes a durable intent before the single submit call and writes the job ID receipt immediately afterward. Exceptions are redacted and never retried. Tests use injected mocks only and never instantiate an IBM service.
