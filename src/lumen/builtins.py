"""Встроенные функции LUMEN."""

from .errors import LumenCallError, LumenTypeError
from .types import (
    LumenBuiltin,
    is_number,
    join_print,
    lumen_to_str,
    lumen_transform,
    lumen_truthy,
    lumen_type_name,
)


def _arity(name, count, min_args, max_args=None):
    if count < min_args or (max_args is not None and count > max_args):
        if max_args is None or min_args == max_args:
            expect = str(min_args)
        else:
            expect = f"{min_args}..{max_args}"
        raise LumenCallError(f"{name}() expects {expect} argument(s), got {count}")


def _require_type(value, allowed, what):
    name = lumen_type_name(value)
    if name not in allowed:
        kinds = ", ".join(allowed)
        raise LumenTypeError(f"{what} requires {kinds}, got {name}")


def make_builtins() -> dict:
    def lumen_print(interp, args):
        print(join_print([lumen_to_str(arg) for arg in args]))
        return None

    def lumen_len(interp, args):
        _arity("len", len(args), 1)
        value = args[0]
        _require_type(value, {"String", "List", "Map"}, "len()")
        return len(value)

    def lumen_type(interp, args):
        _arity("type", len(args), 1)
        return lumen_type_name(args[0])

    def lumen_str(interp, args):
        _arity("str", len(args), 1)
        return lumen_transform(args[0], "String")

    def lumen_num(interp, args):
        _arity("num", len(args), 1)
        return lumen_transform(args[0], "Number")

    def lumen_bool(interp, args):
        _arity("bool", len(args), 1)
        return lumen_transform(args[0], "Boolean")

    def lumen_append(interp, args):
        _arity("append", len(args), 2)
        _require_type(args[0], {"List"}, "append()")
        return args[0] + [args[1]]

    def lumen_keys(interp, args):
        _arity("keys", len(args), 1)
        _require_type(args[0], {"Map"}, "keys()")
        return list(args[0].keys())

    def lumen_values(interp, args):
        _arity("values", len(args), 1)
        _require_type(args[0], {"Map"}, "values()")
        return list(args[0].values())

    def lumen_has(interp, args):
        _arity("has", len(args), 2)
        _require_type(args[0], {"Map"}, "has()")
        return args[1] in args[0]

    def lumen_range(interp, args):
        _arity("range", len(args), 1, 2)
        for arg in args:
            if not is_number(arg):
                raise LumenTypeError("range() requires Number arguments")
        if len(args) == 1:
            return list(range(int(args[0])))
        return list(range(int(args[0]), int(args[1])))

    def lumen_input(interp, args):
        _arity("input", len(args), 0, 1)
        prompt = lumen_to_str(args[0]) if args else ""
        return input(prompt)

    def lumen_exit(interp, args):
        _arity("exit", len(args), 0, 1)
        code = 0 if not args else args[0]
        if not is_number(code):
            raise LumenTypeError("exit() requires Number")
        raise SystemExit(int(code))

    def lumen_map(interp, args):
        _arity("map", len(args), 2)
        _require_type(args[0], {"List"}, "map()")
        return [interp.call_value(args[1], [item], None) for item in args[0]]

    def lumen_filter(interp, args):
        _arity("filter", len(args), 2)
        _require_type(args[0], {"List"}, "filter()")
        return [item for item in args[0] if lumen_truthy(interp.call_value(args[1], [item], None))]

    def lumen_sort(interp, args):
        _arity("sort", len(args), 1)
        _require_type(args[0], {"List"}, "sort()")
        try:
            return sorted(args[0])
        except TypeError as exc:
            raise LumenTypeError("sort() requires a list of mutually comparable values") from exc

    def lumen_split(interp, args):
        _arity("split", len(args), 2)
        _require_type(args[0], {"String"}, "split()")
        _require_type(args[1], {"String"}, "split()")
        return args[0].split(args[1])

    def lumen_join(interp, args):
        _arity("join", len(args), 2)
        _require_type(args[0], {"List"}, "join()")
        _require_type(args[1], {"String"}, "join()")
        return args[1].join(lumen_to_str(item) for item in args[0])

    def lumen_replace(interp, args):
        _arity("replace", len(args), 3)
        _require_type(args[0], {"String"}, "replace()")
        _require_type(args[1], {"String"}, "replace()")
        _require_type(args[2], {"String"}, "replace()")
        return args[0].replace(args[1], args[2])

    specs = {
        "print": (lumen_print, 0, None),
        "println": (lumen_print, 0, None),
        "len": (lumen_len, 1, 1),
        "type": (lumen_type, 1, 1),
        "str": (lumen_str, 1, 1),
        "num": (lumen_num, 1, 1),
        "bool": (lumen_bool, 1, 1),
        "append": (lumen_append, 2, 2),
        "keys": (lumen_keys, 1, 1),
        "values": (lumen_values, 1, 1),
        "has": (lumen_has, 2, 2),
        "range": (lumen_range, 1, 2),
        "map": (lumen_map, 2, 2),
        "filter": (lumen_filter, 2, 2),
        "sort": (lumen_sort, 1, 1),
        "split": (lumen_split, 2, 2),
        "join": (lumen_join, 2, 2),
        "replace": (lumen_replace, 3, 3),
        "input": (lumen_input, 0, 1),
        "exit": (lumen_exit, 0, 1),
    }
    # Арность проверяется внутри функций: у print верхняя граница не ограничена.
    return {
        name: LumenBuiltin(name, fn, min_args, max_args if max_args is not None else 10**6)
        for name, (fn, min_args, max_args) in specs.items()
    }
