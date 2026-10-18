"""Morph-блок: состояние, шаги, журнал."""

from .environment import Environment
from .errors import BreakSignal, ContinueSignal, LumenError, LumenMorphError, ReturnSignal


class LumenMorph:
    def __init__(self, name, state_decls, transforms, llm_directives, closure_env, children=None):
        self.name = name
        self.state = {}
        self.transforms = transforms
        self.llm_directives = llm_directives
        self.history = []
        self.closure_env = closure_env
        self.state_decls = state_decls
        self.children = children or []

    def init_state(self, interpreter, shared=None) -> None:
        self.state = {} if shared is None else shared
        for decl in self.state_decls:
            if decl.default is None:
                self.state[decl.name] = None
            else:
                self.state[decl.name] = interpreter.eval_expr(decl.default, self.closure_env)

    def init_family(self, interpreter) -> None:
        """Сначала поля родителя, затем объявления детей на том же состоянии."""
        self.init_state(interpreter, None)
        self._init_children(interpreter)

    def _init_children(self, interpreter) -> None:
        for child in self.children:
            child.init_state(interpreter, self.state)
            child._init_children(interpreter)

    def _make_env(self) -> Environment:
        env = Environment(self.closure_env)
        env.define("state", self.state)
        return env

    def run(self, interpreter) -> None:
        self._run_steps(interpreter)
        for child in self.children:
            start = len(child.history)
            try:
                child.run(interpreter)
            finally:
                self.history.extend(child.history[start:])

    def _run_steps(self, interpreter) -> None:
        for step in self.transforms:
            record = {"step": step.name, "status": "ok"}
            env = self._make_env()
            interpreter.morph_depth += 1
            try:
                if step.skip_condition is not None:
                    if interpreter.truthy(interpreter.eval_expr(step.skip_condition, env)):
                        record["status"] = "skipped"
                        self.history.append(record)
                        continue
                for clause in step.requires:
                    if not interpreter.truthy(interpreter.eval_expr(clause.condition, env)):
                        raise LumenMorphError(
                            f'require failed in transform "{step.name}"',
                            line=clause.line,
                            col=clause.col,
                            source_line=interpreter._source_line(clause.line),
                        )
                interpreter.exec_stmts(step.body, env)
                self.history.append(record)
            except (ReturnSignal, BreakSignal, ContinueSignal) as signal:
                record["status"] = "error"
                record["message"] = type(signal).__name__
                self.history.append(record)
                raise LumenMorphError(
                    "control transfer is not allowed to escape a transform step",
                    line=step.line,
                    col=step.col,
                ) from signal
            except LumenError as exc:
                record["status"] = "error"
                record["message"] = exc.message
                self.history.append(record)
                raise LumenMorphError(
                    exc.message, line=exc.line, col=exc.col, source_line=exc.source_line
                ) from exc
            finally:
                interpreter.morph_depth -= 1


class BoundMethod:
    def __init__(self, morph: LumenMorph, name: str):
        self.morph = morph
        self.name = name
