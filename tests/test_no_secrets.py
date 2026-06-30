from scripts.check_public_safety import main


def test_public_safety_scan() -> None:
    assert main() == 0
