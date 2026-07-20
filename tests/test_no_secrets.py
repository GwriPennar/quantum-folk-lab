from pathlib import Path

from scripts.check_public_safety import ALLOWED_BINARY_QPY, ROOT, main


def test_public_safety_scan() -> None:
    assert main() == 0


def test_binary_qpy_exceptions_are_exact_and_present() -> None:
    assert set(ALLOWED_BINARY_QPY) == {
        Path("experiments/EXP-010C-read-only-ibm-preflight/qaoa.qpy"),
        Path("experiments/EXP-010C-read-only-ibm-preflight/control.qpy"),
    }
    assert all((ROOT / path).is_file() for path in ALLOWED_BINARY_QPY)
