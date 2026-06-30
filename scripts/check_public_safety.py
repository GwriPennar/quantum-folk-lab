from __future__ import annotations

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
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "quantum-folk-lab-bootstrap",
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
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() == ".pdf":
            failures.append(f"forbidden file: {path.relative_to(ROOT)}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"binary or non-utf8 file: {path.relative_to(ROOT)}")
            continue
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{name}: {path.relative_to(ROOT)}")
    if failures:
        print("Public safety scan failed:")
        print("\n".join(failures))
        return 1
    print("Public safety scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
