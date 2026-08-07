"""CLI-заглушка LUMEN.

Команды (целевой интерфейс v0.1.0, см. ROADMAP.md, этап 1e):
    lumen run <file>   — интерпретация файла (не реализовано)
    lumen repl         — интерактивный режим (не реализовано)
    lumen version      — вывод версии

Сейчас реализована только `version`; остальные команды выводят
честное сообщение о статусе и завершаются с кодом 2.
"""

import sys

from . import __version__

BANNER = r"""
  L U M E N  --  Metamorphic Programming Language
  A language that evolves with you.

  version: {version} (documentation stage)
""".format(version=__version__)

NOT_IMPLEMENTED = (
    "Интерпретатор ещё не реализован: проект на стадии проектирования.\n"
    "Спецификация: docs/lumen_spec.md, план реализации: docs/lumen_todo.md."
)


def main(argv=None):
    """Точка входа CLI. Возвращает код завершения."""
    args = sys.argv[1:] if argv is None else argv

    if not args:
        print(BANNER)
        print(NOT_IMPLEMENTED)
        return 0

    command = args[0]

    if command == "version":
        print("lumen " + __version__)
        return 0

    if command in ("run", "repl"):
        print(BANNER)
        print("Команда '{0}' пока не реализована.".format(command))
        print(NOT_IMPLEMENTED)
        return 2

    print("Неизвестная команда: {0}".format(command))
    print("Доступные команды: run, repl, version")
    return 2


if __name__ == "__main__":
    sys.exit(main())
