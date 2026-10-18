"""Интерпретатор AST LUMEN."""

import sys

from .ast_nodes import (
    AsExpr,
    AssignStmt,
    BinOp,
    BreakStmt,
    ContextStmt,
    ContinueStmt,
    DissonanceStmt,
    ExprStmt,
    FieldAccess,
    ForStmt,
    FuncCall,
    FuncDef,
    Ident,
    IfStmt,
    IndexAccess,
    IsExpr,
    LambdaExpr,
    ListLiteral,
    LLMDirective,
    Literal,
    MapLiteral,
    MorphStmt,
    ReturnStmt,
    RemoveStmt,
    UnaryOp,
    WhileStmt,
)
from .builtins import make_builtins
from .environment import Environment
from .errors import (
    BreakSignal,
    ContinueSignal,
    LumenArithmeticError,
    LumenCallError,
    LumenDispatchError,
    LumenError,
    LumenIndexError,
    LumenTransformError,
    LumenNameError,
    LumenSyntaxError,
    LumenTypeError,
    ReturnSignal,
)
from .lexer import Lexer
from .morph import BoundMethod, LumenMorph
from .parser import Parser
from .types import (
    LumenBuiltin,
    LumenContext,
    LumenFunction,
    RuntimeWhen,
    creative_cast,
    histories_equal,
    is_number,
    lumen_add,
    lumen_equal,
    lumen_to_str,
    lumen_transform,
    lumen_truthy,
    lumen_type_name,
)


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_context = LumenContext("cli")
        self.morph_depth = 0
        self.dissonance = "strict"
        self.dissonance_log = []
        self.source = ""
        self._load_builtins()

    def _load_builtins(self) -> None:
        for name, fn in make_builtins().items():
            self.global_env.define(name, fn)

    def run(self, program):
        try:
            return self.exec_stmts(program.body, self.global_env)
        except ReturnSignal as exc:
            raise LumenSyntaxError("return outside function") from exc
        except BreakSignal as exc:
            raise LumenSyntaxError("break outside loop") from exc
        except ContinueSignal as exc:
            raise LumenSyntaxError("continue outside loop") from exc

    def exec_stmts(self, stmts, env):
        result = None
        for stmt in stmts:
            result = self.exec_stmt(stmt, env)
        return result

    def exec_stmt(self, stmt, env):
        if isinstance(stmt, AssignStmt):
            value = self.eval_expr(stmt.value, env)
            if stmt.op != "=":
                current = self._read_target(stmt.target, env)
                value = self._apply_aug(current, stmt.op, value, stmt)
            self._write_target(stmt.target, value, env)
            return None
        if isinstance(stmt, FuncDef):
            self._define_function(stmt, env)
            return None
        if isinstance(stmt, IfStmt):
            if lumen_truthy(self.eval_expr(stmt.condition, env)):
                return self.exec_stmts(stmt.then_body, env)
            for cond, body in stmt.elsif_clauses:
                if lumen_truthy(self.eval_expr(cond, env)):
                    return self.exec_stmts(body, env)
            if stmt.else_body:
                return self.exec_stmts(stmt.else_body, env)
            return None
        if isinstance(stmt, WhileStmt):
            while lumen_truthy(self.eval_expr(stmt.condition, env)):
                try:
                    self.exec_stmts(stmt.body, env)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return None
        if isinstance(stmt, ForStmt):
            seq = self.eval_expr(stmt.iterable, env)
            if not isinstance(seq, list):
                self._fail(LumenTypeError, "for loop expects List", stmt)
            for item in seq:
                child = Environment(env)
                child.define(stmt.var, item)
                try:
                    self.exec_stmts(stmt.body, child)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return None
        if isinstance(stmt, DissonanceStmt):
            previous = self.dissonance
            self.dissonance = stmt.mode
            try:
                return self.exec_stmts(stmt.body, env)
            finally:
                self.dissonance = previous
        if isinstance(stmt, ContextStmt):
            previous = self.current_context
            self.current_context = LumenContext(stmt.name, previous)
            try:
                return self.exec_stmts(stmt.body, env)
            finally:
                self.current_context = previous
        if isinstance(stmt, ReturnStmt):
            value = None if stmt.value is None else self.eval_expr(stmt.value, env)
            raise ReturnSignal(value)
        if isinstance(stmt, RemoveStmt):
            obj = self._get_name(stmt.obj, env, stmt)
            if not isinstance(obj, dict):
                self._fail(LumenTypeError, "remove expects a Map", stmt)
            obj.pop(stmt.field, None)
            return None
        if isinstance(stmt, BreakStmt):
            raise BreakSignal()
        if isinstance(stmt, ContinueStmt):
            raise ContinueSignal()
        if isinstance(stmt, ExprStmt):
            return self.eval_expr(stmt.expr, env)
        if isinstance(stmt, MorphStmt):
            morph = self._build_morph(stmt, env)
            morph.init_family(self)
            self._define_morph_tree(stmt, morph, env)
            return None
        if isinstance(stmt, LLMDirective):
            return None
        self._fail(LumenTypeError, f"unknown statement {type(stmt).__name__}", stmt)

    def _build_morph(self, stmt, env):
        children = [self._build_morph(child, env) for child in stmt.children]
        return LumenMorph(
            stmt.name,
            stmt.state_decls,
            stmt.transforms,
            stmt.llm_directives,
            env,
            children,
        )

    def _define_morph_tree(self, stmt, morph, env) -> None:
        env.define(stmt.name, morph)
        for child_stmt, child in zip(stmt.children, morph.children):
            self._define_morph_tree(child_stmt, child, env)

    def _define_function(self, stmt: FuncDef, env: Environment) -> None:
        clauses = [
            RuntimeWhen(clause.type_name, clause.params, clause.body, env)
            for clause in stmt.when_clauses
        ]
        if clauses and env.has(stmt.name):
            existing = env.get(stmt.name)
            if isinstance(existing, LumenFunction) and existing.when_clauses:
                existing.when_clauses.extend(clauses)
                return
        function = LumenFunction(stmt.name, stmt.params, stmt.body, env, clauses)
        env.define(stmt.name, function)

    def eval_expr(self, expr, env):
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, Ident):
            return self._get_name(expr.name, env, expr)
        if isinstance(expr, BinOp):
            return self._binop(expr, env)
        if isinstance(expr, UnaryOp):
            value = self.eval_expr(expr.operand, env)
            if expr.op == "-":
                if not is_number(value):
                    self._fail(LumenTypeError, "unary minus expects Number", expr)
                return -value
            if expr.op == "not":
                return not lumen_truthy(value)
            self._fail(LumenTypeError, f"unknown operator {expr.op}", expr)
        if isinstance(expr, FieldAccess):
            obj = self.eval_expr(expr.obj, env)
            return self._read_field(obj, expr.field, expr)
        if isinstance(expr, IndexAccess):
            obj = self.eval_expr(expr.obj, env)
            index = self.eval_expr(expr.index, env)
            return self._read_index(obj, index, expr)
        if isinstance(expr, FuncCall):
            callee = self.eval_expr(expr.callee, env)
            args = [self.eval_expr(arg, env) for arg in expr.args]
            return self.call_value(callee, args, expr)
        if isinstance(expr, AsExpr):
            return self._cast(self.eval_expr(expr.value, env), expr.type_name, expr)
        if isinstance(expr, IsExpr):
            return lumen_type_name(self.eval_expr(expr.value, env)) == expr.type_name
        if isinstance(expr, ListLiteral):
            return [self.eval_expr(item, env) for item in expr.elements]
        if isinstance(expr, MapLiteral):
            return {key: self.eval_expr(value, env) for key, value in expr.entries}
        if isinstance(expr, LambdaExpr):
            return LumenFunction(None, expr.params, expr.body, env, [])
        self._fail(LumenTypeError, f"unknown expression {type(expr).__name__}", expr)

    def _binop(self, expr: BinOp, env):
        if expr.op == "and":
            left = self.eval_expr(expr.left, env)
            if not lumen_truthy(left):
                return left
            return self.eval_expr(expr.right, env)
        if expr.op == "or":
            left = self.eval_expr(expr.left, env)
            if lumen_truthy(left):
                return left
            return self.eval_expr(expr.right, env)

        left = self.eval_expr(expr.left, env)
        right = self.eval_expr(expr.right, env)
        if expr.op == "+":
            try:
                return lumen_add(left, right, strict=self.morph_depth > 0)
            except LumenError as exc:
                self._reraise(exc, expr)
        if expr.op in ("-", "*", "/", "%"):
            if not is_number(left) or not is_number(right):
                self._fail(
                    LumenTypeError,
                    f"operator {expr.op} expects Number operands",
                    expr,
                )
            if expr.op == "-" :
                return left - right
            if expr.op == "*":
                return left * right
            if expr.op == "%":
                if right == 0:
                    self._fail(LumenArithmeticError, "division by zero", expr)
                return left % right
            if right == 0:
                self._fail(LumenArithmeticError, "division by zero", expr)
            return left / right
        if expr.op == "==":
            return lumen_equal(left, right)
        if expr.op == "!=":
            return not lumen_equal(left, right)
        if expr.op == "~=":
            if not isinstance(left, LumenMorph) or not isinstance(right, LumenMorph):
                self._fail(LumenTypeError, "operator ~= expects Morph operands", expr)
            return histories_equal(left.history, right.history)
        if expr.op in ("<", ">", "<=", ">="):
            return self._compare(left, right, expr.op, expr)
        self._fail(LumenTypeError, f"unknown operator {expr.op}", expr)

    def _compare(self, left, right, op, node):
        if is_number(left) and is_number(right):
            pair = (left, right)
        elif isinstance(left, str) and isinstance(right, str):
            pair = (left, right)
        else:
            self._fail(LumenTypeError, f"operator {op} expects Number or String", node)
        if op == "<":
            return pair[0] < pair[1]
        if op == ">":
            return pair[0] > pair[1]
        if op == "<=":
            return pair[0] <= pair[1]
        return pair[0] >= pair[1]

    def _apply_aug(self, current, op, value, node):
        if op == "+=":
            return lumen_add(current, value, strict=self.morph_depth > 0)
        if not is_number(current) or not is_number(value):
            self._fail(LumenTypeError, f"operator {op} expects Number operands", node)
        if op == "-=":
            return current - value
        if op == "*=":
            return current * value
        if op == "/=":
            if value == 0:
                self._fail(LumenArithmeticError, "division by zero", node)
            return current / value
        self._fail(LumenTypeError, f"unknown operator {op}", node)

    def call_value(self, callee, args, node):
        line = getattr(node, "line", None)
        col = getattr(node, "col", None)
        if isinstance(callee, LumenBuiltin):
            try:
                return callee.fn(self, args)
            except LumenError as exc:
                if exc.line is None:
                    exc.line = line
                    exc.col = col
                    exc.source_line = self._source_line(line)
                raise
        if isinstance(callee, LumenFunction):
            return self._call_function(callee, args, line, col)
        if isinstance(callee, BoundMethod):
            if callee.name != "run":
                self._fail(LumenTypeError, f"unknown morph method '{callee.name}'", node)
            if args:
                raise LumenCallError(
                    "run() expects 0 argument(s), got %s" % len(args),
                    line,
                    col,
                    self._source_line(line),
                )
            callee.morph.run(self)
            return None
        raise LumenTypeError(
            f"cannot call {lumen_type_name(callee)}",
            line,
            col,
            self._source_line(line),
        )

    def _call_function(self, fn: LumenFunction, args, line, col):
        if fn.when_clauses:
            if not args:
                raise LumenDispatchError(
                    f"no matching clause for type Null in function '{fn.name}'",
                    line,
                    col,
                    self._source_line(line),
                )
            type_name = lumen_type_name(args[0])
            for clause in fn.when_clauses:
                if clause.type_name == type_name:
                    return self._invoke(
                        clause.params, clause.body, clause.closure_env, args, fn.name, line, col
                    )
            raise LumenDispatchError(
                f"no matching clause for type {type_name} in function '{fn.name}'",
                line,
                col,
                self._source_line(line),
            )
        return self._invoke(fn.params, fn.body, fn.closure_env, args, fn.name, line, col)

    def _invoke(self, params, body, closure, args, name, line, col):
        label = name or "<lambda>"
        if len(args) != len(params):
            raise LumenCallError(
                f"function '{label}' expects {len(params)} argument(s), got {len(args)}",
                line,
                col,
                self._source_line(line),
            )
        env = Environment(closure)
        for param, arg in zip(params, args):
            env.define(param, arg)
        try:
            return self.exec_stmts(body, env)
        except ReturnSignal as signal:
            return signal.value

    def _read_target(self, target, env):
        if isinstance(target, Ident):
            return self._get_name(target.name, env, target)
        if isinstance(target, FieldAccess):
            obj = self.eval_expr(target.obj, env) if not isinstance(target.obj, Ident) else self._read_target(target.obj, env)
            # Ident obj of a field chain is a name, not an expression we re-parse.
            if isinstance(target.obj, Ident):
                obj = self._get_name(target.obj.name, env, target.obj)
            elif isinstance(target.obj, FieldAccess):
                obj = self._read_target(target.obj, env)
            else:
                obj = self.eval_expr(target.obj, env)
            return self._read_field(obj, target.field, target)
        self._fail(LumenTypeError, "invalid assignment target", target)

    def _write_target(self, target, value, env) -> None:
        if isinstance(target, Ident):
            env.set(target.name, value)
            return
        if isinstance(target, FieldAccess):
            if isinstance(target.obj, Ident):
                obj = self._get_name(target.obj.name, env, target.obj)
            elif isinstance(target.obj, FieldAccess):
                obj = self._read_target(target.obj, env)
            else:
                obj = self.eval_expr(target.obj, env)
            self._write_field(obj, target.field, value, target)
            return
        self._fail(LumenTypeError, "invalid assignment target", target)

    def _read_field(self, obj, field, node):
        if isinstance(obj, LumenMorph):
            if field == "state":
                return obj.state
            if field == "history":
                return obj.history
            if field == "run":
                return BoundMethod(obj, "run")
            return None
        if isinstance(obj, dict):
            return obj.get(field, None)
        self._fail(LumenTypeError, f"field access expects Map or Morph, got {lumen_type_name(obj)}", node)

    def _write_field(self, obj, field, value, node) -> None:
        if isinstance(obj, dict):
            obj[field] = value
            return
        self._fail(LumenTypeError, f"cannot assign field on {lumen_type_name(obj)}", node)

    def _read_index(self, obj, index, node):
        if isinstance(obj, list):
            if not is_number(index):
                self._fail(LumenTypeError, "list index must be Number", node)
            i = int(index)
            if i < 0 or i >= len(obj):
                self._fail(LumenIndexError, "index out of range", node)
            return obj[i]
        if isinstance(obj, dict):
            if not isinstance(index, str):
                self._fail(LumenTypeError, "map index must be String", node)
            return obj.get(index, None)
        self._fail(LumenTypeError, f"cannot index {lumen_type_name(obj)}", node)

    def _get_name(self, name, env, node):
        try:
            return env.get(name)
        except LumenNameError as exc:
            exc.line = node.line
            exc.col = node.col
            exc.source_line = self._source_line(node.line)
            raise

    def truthy(self, value) -> bool:
        return lumen_truthy(value)

    def _source_line(self, line):
        if not self.source or not line:
            return None
        lines = self.source.splitlines()
        if 1 <= line <= len(lines):
            return lines[line - 1]
        return None

    def _cast(self, value, target_type, node):
        try:
            return lumen_transform(value, target_type)
        except LumenTransformError as exc:
            if self.dissonance == "strict":
                self._reraise(exc, node)
            if self.dissonance == "soft":
                self._note_dissonance(exc.message, node)
                return value
            try:
                return creative_cast(value, target_type)
            except LumenTransformError as cast_exc:
                self._reraise(cast_exc, node)

    def _note_dissonance(self, message, node) -> None:
        line = getattr(node, "line", None)
        col = getattr(node, "col", None)
        self.dissonance_log.append({"message": message, "line": line, "col": col})
        text = f"[dissonance] {message}"
        if line:
            if col:
                text += f"\n  в строке {line}, колонке {col}"
            else:
                text += f"\n  в строке {line}"
        source = self._source_line(line)
        if source:
            text += f"\n  > {source}"
        print(text, file=sys.stderr)

    def _reraise(self, exc, node):
        if exc.line is None:
            exc.line = getattr(node, "line", None)
            exc.col = getattr(node, "col", None)
            exc.source_line = self._source_line(exc.line)
        raise exc

    def _fail(self, cls, message, node):
        line = getattr(node, "line", None)
        col = getattr(node, "col", None)
        raise cls(message, line, col, self._source_line(line))


def run_source(source: str, interpreter: Interpreter | None = None):
    interp = interpreter or Interpreter()
    interp.source = source
    tokens = Lexer(source).tokenize()
    program = Parser(tokens, source).parse()
    result = interp.run(program)
    return interp, result


def format_value(value) -> str:
    return lumen_to_str(value)
