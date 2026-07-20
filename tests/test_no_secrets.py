from pathlib import Path

from scripts.check_public_safety import ALLOWED_BINARY_QPY, ROOT, main, text_safety_failures


def test_public_safety_scan() -> None:
    assert main() == 0


def test_binary_qpy_exceptions_are_exact_and_present() -> None:
    assert set(ALLOWED_BINARY_QPY) == {
        Path("experiments/EXP-010C-read-only-ibm-preflight/qaoa.qpy"),
        Path("experiments/EXP-010C-read-only-ibm-preflight/control.qpy"),
    }
    assert all((ROOT / path).is_file() for path in ALLOWED_BINARY_QPY)


def test_standard_credential_variable_placeholder_is_safe() -> None:
    assert text_safety_failures('OPENAI_API_KEY="<your-openai-api-key>"') == []


def test_key_like_openai_secret_value_is_rejected() -> None:
    fake_key = "sk-" + "not-a-real-secret-value-123456789"
    assert "token" in text_safety_failures(f'OPENAI_API_KEY="{fake_key}"')
