from __future__ import annotations

from .model import QUBOModel


def require_qiskit() -> None:
    try:
        import qiskit  # type: ignore[import-not-found]  # noqa: F401
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install the optional quantum extra to use Qiskit adapters.") from exc


def describe_ising_terms(model: QUBOModel) -> dict[str, object]:
    return {
        "variables": model.variables,
        "linear": model.linear,
        "quadratic": model.quadratic,
        "offset": model.offset,
    }
