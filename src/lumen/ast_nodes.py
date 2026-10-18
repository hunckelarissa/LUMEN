"""Узлы AST интерпретатора LUMEN."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Program:
    body: list
    line: int = 0
    col: int = 0


@dataclass
class AssignStmt:
    target: Any
    op: str
    value: Any
    line: int = 0
    col: int = 0


@dataclass
class FuncDef:
    name: str
    params: list
    body: list
    when_clauses: list = field(default_factory=list)
    line: int = 0
    col: int = 0


@dataclass
class WhenClause:
    type_name: str
    params: list
    body: list
    line: int = 0
    col: int = 0


@dataclass
class IfStmt:
    condition: Any
    then_body: list
    elsif_clauses: list
    else_body: list
    line: int = 0
    col: int = 0


@dataclass
class WhileStmt:
    condition: Any
    body: list
    line: int = 0
    col: int = 0


@dataclass
class ForStmt:
    var: str
    iterable: Any
    body: list
    line: int = 0
    col: int = 0


@dataclass
class DissonanceStmt:
    mode: str
    body: list
    line: int = 0
    col: int = 0


@dataclass
class ContextStmt:
    name: str
    body: list
    line: int = 0
    col: int = 0


@dataclass
class ReturnStmt:
    value: Any
    line: int = 0
    col: int = 0


@dataclass
class RemoveStmt:
    field: str
    obj: str
    line: int = 0
    col: int = 0


@dataclass
class BreakStmt:
    line: int = 0
    col: int = 0


@dataclass
class ContinueStmt:
    line: int = 0
    col: int = 0


@dataclass
class ExprStmt:
    expr: Any
    line: int = 0
    col: int = 0


@dataclass
class BinOp:
    left: Any
    op: str
    right: Any
    line: int = 0
    col: int = 0


@dataclass
class UnaryOp:
    op: str
    operand: Any
    line: int = 0
    col: int = 0


@dataclass
class Literal:
    value: Any
    line: int = 0
    col: int = 0


@dataclass
class Ident:
    name: str
    line: int = 0
    col: int = 0


@dataclass
class FieldAccess:
    obj: Any
    field: str
    line: int = 0
    col: int = 0


@dataclass
class IndexAccess:
    obj: Any
    index: Any
    line: int = 0
    col: int = 0


@dataclass
class FuncCall:
    callee: Any
    args: list
    line: int = 0
    col: int = 0


@dataclass
class AsExpr:
    value: Any
    type_name: str
    line: int = 0
    col: int = 0


@dataclass
class IsExpr:
    value: Any
    type_name: str
    line: int = 0
    col: int = 0


@dataclass
class ListLiteral:
    elements: list
    line: int = 0
    col: int = 0


@dataclass
class MapLiteral:
    entries: list
    line: int = 0
    col: int = 0


@dataclass
class LambdaExpr:
    params: list
    body: list
    line: int = 0
    col: int = 0


@dataclass
class MorphStmt:
    name: str
    state_decls: list
    transforms: list
    llm_directives: list
    line: int = 0
    col: int = 0
    children: list = field(default_factory=list)


@dataclass
class StateDecl:
    name: str
    type_name: str
    default: Any = None
    line: int = 0
    col: int = 0


@dataclass
class TransformClause:
    name: str
    body: list
    skip_condition: Any = None
    llm_directives: list = field(default_factory=list)
    line: int = 0
    col: int = 0
    requires: list = field(default_factory=list)


@dataclass
class RequireClause:
    condition: Any
    line: int = 0
    col: int = 0


@dataclass
class LLMDirective:
    kind: str
    text: str
    line: int = 0
    col: int = 0


def node_pos(node) -> tuple[int, int]:
    return getattr(node, "line", 0), getattr(node, "col", 0)
