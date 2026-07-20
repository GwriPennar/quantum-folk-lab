from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_NAMES = {".env"}
PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "token": re.compile(r"(gh[pousr]_|ibm[_-]?quantum[_-]?token|api[_-]?key)", re.IGNORECASE),
    "windows_user_path": re.compile(r"C:" + r"\\Users\\"),
    "private_project": re.compile(
        "|".join(
            ["Folk" + "_Tune" + "_Finder", "Morris " + "Edward", "response " + "ID", "certificate"]
        ),
        re.IGNORECASE,
    ),
}
SKIP_DIRS = {
    ".git",
    ".venv",
    ".venv-qiskit",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "quantum-folk-lab-bootstrap",
}
ALLOWED_BINARY_QPY = {
    Path(
        "experiments/EXP-010C-read-only-ibm-preflight/qaoa.qpy"
    ): "7f7a811c5175496127db698a50e02d1d950180519cc33dfaf7ec9f577f0c1e0b",
    Path(
        "experiments/EXP-010C-read-only-ibm-preflight/control.qpy"
    ): "1cdf53e347c15f8b469f7ab2b8fe094f61dce65316f488b7aee1724f0f56bda8",
}


def main() -> int:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == "check_public_safety.py":
            continue
        if path.is_dir():
            continue
        relative = path.relative_to(ROOT)
        if relative in ALLOWED_BINARY_QPY:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != ALLOWED_BINARY_QPY[relative]:
                failures.append(f"QPY hash mismatch: {relative}")
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() == ".pdf":
            failures.append(f"forbidden file: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"binary or non-utf8 file: {relative}")
            continue
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{name}: {relative}")
    if failures:
        print("Public safety scan failed:")
        print("\n".join(failures))
        return 1
    print("Public safety scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
