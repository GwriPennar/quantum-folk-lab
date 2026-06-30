from __future__ import annotations

import platform
import sys


def environment_report() -> dict[str, str]:
    report = {"python": sys.version.split()[0], "platform": platform.platform()}
    for package in ("qiskit", "qiskit_aer", "qiskit_ibm_runtime"):
        try:
            module = __import__(package)
            report[package] = getattr(module, "__version__", "installed")
        except ModuleNotFoundError:
            report[package] = "not installed"
    return report
