"""Значения LUMEN, имена типов и трансформации."""

from .errors import LumenTransformError, LumenTypeError


class LumenFunction:
    def __init__(self, name, params, body, closure_env, when_clauses=None):
        self.name = name
        self.params = params
        self.body = body
        self.closure_env = closure_env
        self.when_clauses = when_clauses or []


class RuntimeWhen:
    def __init__(self, type_name, params, body, closure_env):
        self.type_name = type_name
        self.params = params
        self.body = body
        self.closure_env = closure_env


class LumenBuiltin:
    def __init__(self, name, fn, min_args=0, max_args=None):
        self.name = name
        self.fn = fn
        self.min_args = min_args
        self.max_args = max_args if max_args is not None else min_args


class LumenContext:
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def lumen_type_name(value) -> str:
    if isinstance(value, bool):
        return "Boolean"
    if is_number(value):
        return "Number"
    if isinstance(value, str):
        return "String"
    if isinstance(value, list):
        return "List"
    if isinstance(value, dict):
        return "Map"
    if isinstance(value, LumenFunction):
        return "Function"
    if isinstance(value, LumenBuiltin):
        return "Function"
    # Morph импортируется лениво, чтобы не зациклить модули.
    from .morph import BoundMethod, LumenMorph

    if isinstance(value, (LumenMorph, BoundMethod)):
        return "Morph" if isinstance(value, LumenMorph) else "Function"
    if isinstance(value, LumenContext):
        return "Context"
    if value is None:
        return "Null"
    return "Unknown"


def format_number(value) -> str:
    if isinstance(value, float):
        if value.is_integer() and value not in (float("inf"), float("-inf")):
            return str(int(value))
        return format(value, ".15g")
    return str(value)


def lumen_to_str(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return value
    if is_number(value):
        return format_number(value)
    if isinstance(value, list):
        return "[" + ", ".join(lumen_to_str(item) for item in value) + "]"
    if isinstance(value, dict):
        parts = [f"{key}: {lumen_to_str(item)}" for key, item in value.items()]
        return "{" + ", ".join(parts) + "}"
    if isinstance(value, LumenFunction):
        label = value.name or "<lambda>"
        return f"<function {label}>"
    if isinstance(value, LumenBuiltin):
        return f"<builtin {value.name}>"
    from .morph import BoundMethod, LumenMorph

    if isinstance(value, LumenMorph):
        return f"<morph {value.name}>"
    if isinstance(value, BoundMethod):
        return f"<method {value.name}>"
    if isinstance(value, LumenContext):
        return f"<context {value.name}>"
    return str(value)


def _parse_number_text(text: str):
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return None


def try_as_number(value):
    """Вернуть число или None, если неявное приведение невозможно."""
    if isinstance(value, bool):
        return 1 if value else 0
    if is_number(value):
        return value
    if isinstance(value, str):
        return _parse_number_text(value)
    if value is None:
        return 0
    return None


def lumen_transform(value, target_type: str):
    src = lumen_type_name(value)
    if src == target_type:
        return value

    if src == "String" and target_type == "Number":
        parsed = _parse_number_text(value)
        if parsed is None:
            raise LumenTransformError(f'cannot transform String "{value}" to Number')
        return parsed

    if src == "Number" and target_type == "String":
        return format_number(value)

    if src == "Boolean" and target_type == "Number":
        return 1 if value else 0

    if src == "Number" and target_type == "Boolean":
        return value != 0

    if value is None and target_type == "Number":
        return 0

    if value is None and target_type == "Boolean":
        return False

    if value is None and target_type == "String":
        return "null"

    if src == "Boolean" and target_type == "String":
        return "true" if value else "false"

    if src == "List" and target_type == "String":
        return lumen_to_str(value)

    if src == "Map" and target_type == "String":
        return lumen_to_str(value)

    raise LumenTransformError(f"cannot transform {src} to {target_type}")


def lumen_add(left, right, *, strict: bool = False):
    """Сложение по §3.2.2. strict=True — внутри transform."""
    if isinstance(left, list):
        return left + [right]
    if isinstance(left, dict) and isinstance(right, dict):
        merged = dict(left)
        merged.update(right)
        return merged

    if strict:
        if is_number(left) and is_number(right):
            return left + right
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        raise LumenTypeError(
            f"cannot add {lumen_type_name(left)} and {lumen_type_name(right)} inside morph"
        )

    if is_number(left):
        if isinstance(right, str):
            parsed = _parse_number_text(right)
            if parsed is None:
                return lumen_to_str(left) + right
            return left + parsed
        if isinstance(right, bool) or is_number(right) or right is None:
            return left + try_as_number(right)
        raise LumenTypeError(
            f"cannot add {lumen_type_name(left)} and {lumen_type_name(right)}"
        )

    if isinstance(left, str):
        if is_number(right):
            parsed = _parse_number_text(left)
            if parsed is not None:
                return parsed + right
        return left + lumen_to_str(right)

    raise LumenTypeError(
        f"cannot add {lumen_type_name(left)} and {lumen_type_name(right)}"
    )


def history_record_key(record) -> tuple:
    """Точное совпадение шага истории: имя, статус и сообщение об ошибке."""
    return (record.get("step"), record.get("status"), record.get("message"))


def histories_equal(left, right) -> bool:
    if len(left) != len(right):
        return False
    return all(history_record_key(a) == history_record_key(b) for a, b in zip(left, right))


def lumen_equal(left, right) -> bool:
    from .morph import LumenMorph

    if isinstance(left, (LumenFunction, LumenBuiltin)) or isinstance(right, (LumenFunction, LumenBuiltin)):
        return False
    if isinstance(left, LumenMorph) or isinstance(right, LumenMorph):
        return False
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if is_number(left) and is_number(right):
        return left == right
    if isinstance(left, str) and isinstance(right, str):
        return left == right
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(lumen_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return False
        return all(lumen_equal(left[key], right[key]) for key in left)
    if left is None and right is None:
        return True
    return False


def lumen_truthy(value) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if is_number(value):
        return value != 0
    if isinstance(value, str):
        return len(value) > 0
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return True


def creative_cast(value, target_type: str):
    """Запасной переход, когда обычная таблица `as` не срабатывает."""
    if target_type == "Number":
        return 0
    if target_type == "Boolean":
        return lumen_truthy(value)
    if target_type == "String":
        return lumen_to_str(value)
    if target_type == "List":
        return [value]
    if target_type == "Map":
        return {"value": value}
    raise LumenTransformError(
        f"cannot transform {lumen_type_name(value)} to {target_type}"
    )


def join_print(parts: list[str]) -> str:
    """Склеить аргументы print: пробел, но не второй на уже существующей границе."""
    if not parts:
        return ""
    out = parts[0]
    for part in parts[1:]:
        if out.endswith((" ", "\t")) or part.startswith((" ", "\t")):
            out += part
        else:
            out += " " + part
    return out
