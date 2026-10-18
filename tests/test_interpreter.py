import os
import subprocess
import sys

import pytest

from lumen.errors import (
    LumenArithmeticError,
    LumenCallError,
    LumenDispatchError,
    LumenNameError,
    LumenTransformError,
)
from lumen.interpreter import run_source
from tests.support import run

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLDEN = os.path.join(os.path.dirname(__file__), "golden")


def test_print_and_assign():
    assert run('print("hello")') == "hello"
    assert run("x = 42\nprint(x)") == "42"


def test_implicit_add():
    assert run('print("42" + 1)') == "43"
    assert run('print(42 + "!")') == "42!"
    assert run('print("" + 2)') == "2"


def test_if_and_loops():
    assert run('if true\nprint("yes")\nend') == "yes"
    assert run('if false\nprint("no")\nelse\nprint("yes")\nend') == "yes"
    assert run("for i in range(3)\nprint(i)\nend") == "0\n1\n2"
    assert run("n = 0\nwhile n < 3\nprint(n)\nn = n + 1\nend") == "0\n1\n2"


def test_function_and_lambda():
    assert run("def f(x)\nreturn x * 2\nend\nprint(f(5))") == "10"
    assert run("double = do |x| x * 2 end\nprint(double(5))") == "10"


def test_when_and_evolution():
    code = '''
def show(v)
  when Number then print("number: ", v)
  when String then print("string: ", v)
  when List then print("list of ", len(v), " items")
end
show(10)
show("hello")
show([1, 2, 3])
def show(v)
  when Boolean then print("bool: ", v)
end
show(true)
'''
    assert run(code) == "number: 10\nstring: hello\nlist of 3 items\nbool: true"


def test_living_map():
    code = '''
user = {name: "Lara"}
user.age = 30
print(user.name)
print(user.age)
remove age from user
print(user.age)
'''
    assert run(code) == "Lara\n30\nnull"


def test_break_continue_and_builtins():
    assert run("for i in range(5)\nif i == 3\nbreak\nend\nprint(i)\nend") == "0\n1\n2"
    assert run("for i in range(4)\nif i % 2 == 0\ncontinue\nend\nprint(i)\nend") == "1\n3"
    assert run("print(len([1, 2, 3]))") == "3"
    assert run("print(type(42))") == "Number"
    assert run("print(42 is Number)") == "true"
    assert run('print("hi" is String)') == "true"
    assert run("print(map([1, 2, 3], do |x| x * 2 end))") == "[2, 4, 6]"
    assert run("print(filter([1, 2, 3, 4], do |x| x > 2 end))") == "[3, 4]"
    assert run('print(split("a,b,c", ","))') == "[a, b, c]"
    assert run('print(join(["a", "b", "c"], "-"))') == "a-b-c"


def test_errors():
    with pytest.raises(LumenTransformError):
        run_source('"hello" as Number')
    with pytest.raises(LumenNameError):
        run_source("foo")
    with pytest.raises(LumenArithmeticError):
        run_source("1 / 0")
    with pytest.raises(LumenCallError):
        run_source("def f(x)\nreturn x\nend\nf()")
    with pytest.raises(LumenDispatchError):
        run_source("def show(v)\nwhen Number then print(v)\nend\nshow(true)")


def test_strict_add_inside_morph():
    code = '''
morph box
  state value: String = "42"
  transform "bad"
    state.value = state.value + 1
  end
end
box.run()
'''
    with pytest.raises(Exception):
        run_source(code)


def test_golden():
    for fname in sorted(os.listdir(GOLDEN)):
        if not fname.endswith(".lumen"):
            continue
        base = fname[:-6]
        expected_path = os.path.join(GOLDEN, base + ".expected")
        if not os.path.exists(expected_path):
            continue
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "lumen.py"), "run", os.path.join(GOLDEN, fname)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        expected = open(expected_path, encoding="utf-8").read().strip()
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == expected, result.stdout
