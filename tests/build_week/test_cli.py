from __future__ import annotations

import sys

import pytest

from quantum_folk_lab import cli


def test_build_week_cli_summary(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["qfl", "build-week-exact"])
    cli.main()
    output = capsys.readouterr().out
    assert "synthetic-two-family-v1-seed42" in output
    assert "Authority: exact enumeration" in output


def test_build_week_cli_validation_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["qfl", "build-week-exact"])
    monkeypatch.setattr(cli, "run_guided_exact", lambda: (_ for _ in ()).throw(ValueError("bad")))
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    assert "validation failed" in capsys.readouterr().err
