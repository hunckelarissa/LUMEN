"""Окружение имён: связный список таблиц."""

from typing import Any, Optional

from .errors import LumenNameError


class Environment:
    def __init__(self, parent: Optional["Environment"] = None):
        self.bindings: dict[str, Any] = {}
        self.parent = parent

    def get(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise LumenNameError(f"undefined variable '{name}'")

    def set(self, name: str, value: Any) -> None:
        if name in self.bindings:
            self.bindings[name] = value
            return
        if self.parent is not None and self.parent.has(name):
            self.parent.set(name, value)
            return
        self.bindings[name] = value

    def define(self, name: str, value: Any) -> None:
        self.bindings[name] = value

    def has(self, name: str) -> bool:
        if name in self.bindings:
            return True
        if self.parent is not None:
            return self.parent.has(name)
        return False
