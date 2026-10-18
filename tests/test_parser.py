import pytest

from lumen.ast_nodes import (
    AsExpr,
    AssignStmt,
    BinOp,
    ExprStmt,
    FieldAccess,
    ForStmt,
    FuncCall,
    FuncDef,
    Ident,
    IfStmt,
    IsExpr,
    LambdaExpr,
    ListLiteral,
    Literal,
    MapLiteral,
    MorphStmt,
    StateDecl,
    TransformClause,
    WhileStmt,
)
from lumen.errors import LumenSyntaxError
from lumen.lexer import Lexer
from lumen.parser import Parser


def parse(source):
    return Parser(Lexer(source).tokenize(), source).parse()


def test_assign():
    stmt = parse("x = 42").body[0]
    assert isinstance(stmt, AssignStmt)
    assert isinstance(stmt.target, Ident)
    assert stmt.target.name == "x"
    assert stmt.value.value == 42


def test_print_call():
    stmt = parse('print("hello")').body[0]
    assert isinstance(stmt, ExprStmt)
    assert isinstance(stmt.expr, FuncCall)
    assert stmt.expr.callee.name == "print"


def test_func_and_when():
    program = parse("def foo(x)\nreturn x\nend")
    fn = program.body[0]
    assert isinstance(fn, FuncDef)
    assert fn.params == ["x"]
    shown = parse('def show(v)\nwhen Number then print(v)\nend').body[0]
    assert shown.when_clauses[0].type_name == "Number"


def test_if_elsif_else():
    stmt = parse("if x > 0\nprint(1)\nelsif x == 0\nprint(0)\nelse\nprint(2)\nend").body[0]
    assert isinstance(stmt, IfStmt)
    assert len(stmt.elsif_clauses) == 1
    assert stmt.else_body


def test_loops():
    assert isinstance(parse("for i in range(5)\nprint(i)\nend").body[0], ForStmt)
    assert isinstance(parse("while x < 10\nx = x + 1\nend").body[0], WhileStmt)


def test_field_list_map():
    stmt = parse('user.age = 30').body[0]
    assert isinstance(stmt.target, FieldAccess)
    assert isinstance(parse("[1, 2, 3]").body[0].expr, ListLiteral)
    mapping = parse('{name: "Lara", age: 30}').body[0].expr
    assert isinstance(mapping, MapLiteral)
    assert mapping.entries[0][0] == "name"


def test_as_is_lambda_precedence():
    assert isinstance(parse("x as Number").body[0].expr, AsExpr)
    assert isinstance(parse("x is String").body[0].expr, IsExpr)
    assert isinstance(parse("do |x| x * 2 end").body[0].expr, LambdaExpr)
    expr = parse("2 + 3 * 4").body[0].expr
    assert isinstance(expr, BinOp)
    assert expr.op == "+"
    assert isinstance(expr.right, BinOp)
    assert expr.right.op == "*"


def test_morph():
    stmt = parse(
        'morph dataset\n'
        'state rows: List\n'
        'transform "clean"\n'
        'skip if ready\n'
        'state.rows = null\n'
        'end\n'
        'shadow "hint"\n'
        'end'
    ).body[0]
    assert isinstance(stmt, MorphStmt)
    assert isinstance(stmt.state_decls[0], StateDecl)
    assert isinstance(stmt.transforms[0], TransformClause)
    assert stmt.transforms[0].skip_condition is not None
    assert stmt.llm_directives[0].kind == "shadow"


def test_unclosed_def():
    with pytest.raises(LumenSyntaxError):
        parse("def foo(x)")


def test_break_outside_loop():
    with pytest.raises(LumenSyntaxError):
        parse("break")


def test_nested_morph_in_body():
    stmt = parse(
        "morph outer\n"
        "state n: Number = 1\n"
        "morph inner\n"
        "state extra: Number = 2\n"
        'transform "child"\n'
        "end\n"
        "end\n"
        "end"
    ).body[0]
    assert isinstance(stmt, MorphStmt)
    assert stmt.children[0].name == "inner"
    assert stmt.children[0].state_decls[0].name == "extra"


def test_morph_inside_transform_rejected():
    source = (
        'morph outer\n'
        'transform "go"\n'
        'morph inner\n'
        'end\n'
        'end\n'
        'end'
    )
    with pytest.raises(LumenSyntaxError):
        parse(source)
