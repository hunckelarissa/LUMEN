"""Интерактивный режим LUMEN."""

from . import __version__
from .errors import LumenError, LumenSyntaxError
from .interpreter import Interpreter, run_source
from .types import lumen_to_str


def start_repl() -> None:
    print(f"LUMEN {__version__} REPL")
    print("Введите 'exit' для выхода.\n")
    interp = Interpreter()
    buffer = ""
    while True:
        prompt = "lumen> " if not buffer else "... "
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            return
        if not buffer and line.strip() in ("exit", "quit"):
            return
        if not buffer and not line.strip():
            continue
        buffer += line + "\n"
        try:
            _interp, result = run_source(buffer, interp)
        except LumenSyntaxError as exc:
            if getattr(exc, "incomplete", False):
                continue
            print(exc)
            buffer = ""
            continue
        except LumenError as exc:
            print(exc)
            buffer = ""
            continue
        except Exception as exc:
            print(f"[InternalError] {exc}")
            buffer = ""
            continue
        if result is not None:
            print("=>", lumen_to_str(result))
        buffer = ""
