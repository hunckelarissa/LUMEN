import pytest

from lumen.errors import LumenMorphError
from lumen.interpreter import run_source
from tests.support import run


def test_run_history_and_skip():
    code = '''
morph counter
  state value: Number = 0
  transform "increment"
    state.value = state.value + 1
  end
  transform "double"
    state.value = state.value * 2
  end
end
counter.run()
print(counter.state.value)
print(len(counter.history))
'''
    assert run(code) == "2\n2"


def test_defaults_and_skip():
    code = '''
morph pipeline
  state rows: List
  state cleaned: Boolean = false
  state ready: Boolean = false
  transform "check"
    state.ready = true
  end
  transform "process"
    skip if state.ready == false
    print("processing")
  end
  transform "later"
    skip if true
    print("nope")
  end
end
pipeline.run()
print(pipeline.state.rows)
print(pipeline.state.cleaned)
print(pipeline.history)
'''
    output = run(code)
    assert output.splitlines()[0] == "processing"
    assert "null" in output
    assert "false" in output
    assert "skipped" in output


def test_transform_error_is_morph_error():
    code = '''
morph box
  transform "bad"
    print(missing)
  end
end
box.run()
'''
    with pytest.raises(LumenMorphError):
        run_source(code)


def test_nested_morph_shares_state_and_merges_history():
    code = '''
morph outer
  state n: Number = 1
  transform "parent"
    state.n = state.n + 1
  end
  morph inner
    state extra: Number = 3
    transform "child"
      state.extra = state.extra + state.n
    end
  end
end
outer.run()
print(outer.state.n)
print(outer.state.extra)
print(inner.state.n)
print(len(outer.history))
print(len(inner.history))
'''
    assert run(code) == "2\n5\n2\n2\n1"


def test_child_declaration_overrides_parent_field():
    code = '''
morph outer
  state n: Number = 1
  transform "parent"
    state.n = state.n + 1
  end
  morph inner
    state n: Number = 10
    transform "child"
      state.n = state.n + 1
    end
  end
end
outer.run()
print(outer.state.n)
'''
    assert run(code) == "12"


def test_called_morph_keeps_its_own_state():
    code = '''
morph helper
  state n: Number = 1
  transform "set"
    state.n = 7
  end
end

morph main
  state n: Number = 1
  transform "use"
    helper.run()
    state.n = state.n + 1
  end
end
main.run()
print(main.state.n)
print(helper.state.n)
'''
    assert run(code) == "2\n7"


def test_path_equality_matches_history_not_state():
    code = '''
morph left
  state n: Number = 0
  transform "inc"
    state.n = state.n + 1
  end
end
morph right
  state n: Number = 5
  transform "inc"
    state.n = state.n + 1
  end
end
morph other
  state n: Number = 0
  transform "dec"
    state.n = state.n + 1
  end
end
left.run()
right.run()
other.run()
print(left ~= right)
print(left ~= other)
print(left == right)
print(left ~= left)
'''
    assert run(code) == "true\nfalse\nfalse\ntrue"


def test_path_equality_rejects_non_morph():
    import pytest
    from lumen.errors import LumenTypeError
    from lumen.interpreter import run_source

    with pytest.raises(LumenTypeError):
        run_source("print(1 ~= 1)")


def test_llm_directives_do_not_run():
    code = '''
morph agent
  shadow "hint"
  transform "act"
    think "quietly"
    print("go")
  end
end
agent.run()
'''
    assert run(code) == "go"
