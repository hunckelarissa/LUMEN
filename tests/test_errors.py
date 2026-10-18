import pytest

from lumen.errors import (
    LumenArithmeticError,
    LumenCallError,
    LumenDispatchError,
    LumenNameError,
    LumenTransformError,
)
from lumen.interpreter import run_source


def test_transform_message():
    with pytest.raises(LumenTransformError) as caught:
        run_source('"hello" as Number')
    assert 'cannot transform String "hello" to Number' in caught.value.message


def test_name_call_dispatch_arithmetic():
    with pytest.raises(LumenNameError):
        run_source("foo")
    with pytest.raises(LumenArithmeticError):
        run_source("1 / 0")
    with pytest.raises(LumenCallError):
        run_source("def f(x)\nreturn x\nend\nf(1, 2)")
    with pytest.raises(LumenDispatchError) as caught:
        run_source('def show(v)\nwhen Number then return v\nend\nshow("x")')
    assert "String" in caught.value.message
