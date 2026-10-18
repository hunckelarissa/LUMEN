"""CLI LUMEN: run, repl, version."""

import sys

from . import __version__

BANNER = """
  L U M E N  --  Metamorphic Programming Language
  A language that evolves with you.

  version: {version}
""".format(version=__version__)


def run_file(path: str) -> int:
    from .errors import LumenError
    from .interpreter import run_source

    try:
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
    except OSError as exc:
        print(f"Не удалось открыть файл: {path}\n{exc}", file=sys.stderr)
        return 2
    try:
        run_source(source)
    except LumenError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    """Точка входа CLI. Возвращает код завершения."""
    args = sys.argv[1:] if argv is None else list(argv)

    if not args:
        print(BANNER)
        print("Команды: run <file>, repl, version")
        return 0

    command = args[0]

    if command == "version":
        print("lumen " + __version__)
        return 0

    if command == "run":
        if len(args) < 2:
            print("Использование: lumen run <file>", file=sys.stderr)
            return 2
        return run_file(args[1])

    if command == "repl":
        from .repl import start_repl

        start_repl()
        return 0

    print(f"Неизвестная команда: {command}")
    print("Доступные команды: run, repl, version")
    return 2


if __name__ == "__main__":
    sys.exit(main())
