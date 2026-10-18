"""Иерархия ошибок LUMEN и сигналы управления."""


class LumenError(Exception):
    def __init__(self, message, line=None, col=None, source_line=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col
        self.source_line = source_line

    def error_name(self):
        name = type(self).__name__
        if name.startswith("Lumen") and name != "LumenError":
            return name[len("Lumen"):]
        return name

    def __str__(self):
        parts = [f"[{self.error_name()}] {self.message}"]
        if self.line:
            if self.col:
                parts.append(f"  в строке {self.line}, колонке {self.col}")
            else:
                parts.append(f"  в строке {self.line}")
        if self.source_line is not None:
            parts.append(f"  > {self.source_line}")
        return "\n".join(parts)


class LumenSyntaxError(LumenError):
    pass


class LumenNameError(LumenError):
    pass


class LumenTypeError(LumenError):
    pass


class LumenTransformError(LumenError):
    pass


class LumenArithmeticError(LumenError):
    pass


class LumenIndexError(LumenError):
    pass


class LumenCallError(LumenError):
    pass


class LumenDispatchError(LumenError):
    pass


class LumenContextError(LumenError):
    pass


class LumenMorphError(LumenError):
    pass


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass
