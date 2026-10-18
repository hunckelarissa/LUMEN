import pytest

from lumen.errors import LumenMorphError, LumenSyntaxError
from lumen.interpreter import Interpreter, run_source
from tests.support import run


def test_require_passes_and_runs_the_step():
    code = '''
morph door
  state status: String = "closed"
  transform "lock"
    require state.status == "closed"
    state.status = "locked"
  end
end
door.run()
print(door.state.status)
print(door.history)
'''
    output = run(code)
    assert output.splitlines()[0] == "locked"
    assert "ok" in output


def test_failed_require_keeps_state_and_records_error():
    code = '''
morph door
  state status: String = "open"
  transform "note"
    state.status = "noted"
  end
  transform "lock"
    require false
    require missing
    state.status = "locked"
  end
end
door.run()
'''
    interp = Interpreter()
    with pytest.raises(LumenMorphError, match='require failed in transform "lock"') as caught:
        run_source(code, interp)
    assert "NameError" not in str(caught.value)
    door = interp.global_env.get("door")
    assert door.state["status"] == "noted"
    assert [record["status"] for record in door.history] == ["ok", "error"]
    assert door.history[1]["message"] == 'require failed in transform "lock"'


def test_skip_does_not_evaluate_require():
    code = '''
morph door
  state status: String = "locked"
  transform "lock"
    skip if state.status == "locked"
    require missing
    print("nope")
  end
end
door.run()
print(door.history)
'''
    output = run(code)
    assert "nope" not in output
    assert "skipped" in output


def test_require_outside_transform_is_syntax_error():
    with pytest.raises(LumenSyntaxError, match="only allowed inside a transform"):
        run_source("require true\n")
