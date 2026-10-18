import pytest

from lumen.errors import LumenSyntaxError, LumenTransformError
from lumen.interpreter import run_source
from lumen.lexer import Lexer
from lumen.parser import Parser
from tests.support import run


def test_strict_is_the_default():
    with pytest.raises(LumenTransformError):
        run_source('"hello" as Number')


def test_soft_keeps_value_and_warns(capsys):
    assert run('dissonance soft\nprint("hello" as Number)\nend') == "hello"
    captured = capsys.readouterr()
    assert "[dissonance]" in captured.err
    assert "String" in captured.err


def test_creative_uses_fallback():
    code = '''
dissonance creative
  print("hello" as Number)
  print([1, 2] as Number)
  print(1 as Map)
end
'''
    assert run(code) == "0\n0\n{value: 1}"


def test_nested_mode_restores_outer():
    code = '''
dissonance creative
  dissonance strict
    print(1 as String)
  end
  print("x" as Number)
end
'''
    assert run(code) == "1\n0"


def test_unknown_mode_is_syntax_error():
    with pytest.raises(LumenSyntaxError):
        Parser(Lexer("dissonance loud\nend").tokenize(), "dissonance loud\nend").parse()


def test_successful_cast_is_silent(capsys):
    assert run('dissonance soft\nprint("42" as Number)\nend') == "42"
    assert capsys.readouterr().err == ""
