from __future__ import annotations


def require_confirmation(confirm_qpu: bool) -> None:
    if not confirm_qpu:
        raise PermissionError("IBM QPU execution requires --confirm-qpu.")


def import_runtime() -> object:
    try:
        import qiskit_ibm_runtime  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install the optional ibm extra to use IBM Runtime.") from exc
    return qiskit_ibm_runtime
