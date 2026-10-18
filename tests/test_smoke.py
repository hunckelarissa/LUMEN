"""Smoke-тесты заглушки CLI. Полная структура тестов появится на этапе 1 (ROADMAP.md)."""

import os
import sys

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"),
)

from lumen import __version__
from lumen.cli import main


def test_version_format():
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


def test_cli_version(capsys):
    assert main(["version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_cli_banner(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "L U M E N" in out


def test_cli_run_hello(capsys):
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "examples",
        "hello.lumen",
    )
    assert main(["run", path]) == 0
    assert capsys.readouterr().out.strip() == "Hello, World!"


def test_cli_unknown_command(capsys):
    assert main(["frobnicate"]) == 2
    assert "Неизвестная команда" in capsys.readouterr().out
