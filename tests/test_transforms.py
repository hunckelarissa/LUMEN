import pytest

from lumen.errors import LumenTransformError
from lumen.types import lumen_transform


def test_string_number():
    assert lumen_transform("42", "Number") == 42
    assert lumen_transform("3.14", "Number") == 3.14
    with pytest.raises(LumenTransformError):
        lumen_transform("hello", "Number")


def test_number_string_and_bool():
    assert lumen_transform(42, "String") == "42"
    assert lumen_transform(3.14, "String") == "3.14"
    assert lumen_transform(True, "Number") == 1
    assert lumen_transform(False, "Number") == 0
    assert lumen_transform(0, "Boolean") is False
    assert lumen_transform(42, "Boolean") is True


def test_null_and_containers():
    assert lumen_transform(None, "Number") == 0
    assert lumen_transform(None, "Boolean") is False
    assert lumen_transform(None, "String") == "null"
    assert lumen_transform([1, 2, 3], "String") == "[1, 2, 3]"
    assert lumen_transform({"name": "Lara"}, "String") == "{name: Lara}"
