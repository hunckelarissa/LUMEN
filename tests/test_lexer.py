from lumen.lexer import Lexer
from lumen.tokens import TokenType


def kinds(source):
    return [(tok.type, tok.value) for tok in Lexer(source).tokenize()]


def test_empty():
    assert kinds("") == [(TokenType.EOF, "")]


def test_int_and_float():
    assert kinds("42")[0] == (TokenType.INT_LIT, "42")
    assert kinds("3.14")[0] == (TokenType.FLOAT_LIT, "3.14")


def test_string_escape():
    assert kinds('"hello"')[0] == (TokenType.STR_LIT, "hello")
    assert kinds('"hell\\"o"')[0] == (TokenType.STR_LIT, 'hell"o')


def test_keywords_and_ident():
    got = kinds("def foo end")
    assert [item[0] for item in got] == [TokenType.DEF, TokenType.IDENT, TokenType.END, TokenType.EOF]
    assert got[1][1] == "foo"


def test_assign_and_comparisons():
    assert kinds("x = 42")[1][0] == TokenType.ASSIGN
    for source, kind in [("==", TokenType.EQ), ("!=", TokenType.NEQ), ("~=", TokenType.PATH_EQ), ("<=", TokenType.LEQ), (">=", TokenType.GEQ)]:
        assert kinds(source)[0][0] == kind


def test_bool_null():
    assert kinds("true")[0][0] == TokenType.TRUE
    assert kinds("false")[0][0] == TokenType.FALSE
    assert kinds("null")[0][0] == TokenType.NULL


def test_comment_and_whitespace():
    got = kinds("# комментарий\nx")
    assert got[0] == (TokenType.IDENT, "x")


def test_line_and_column():
    tokens = Lexer("x\ny").tokenize()
    assert (tokens[0].line, tokens[0].col) == (1, 1)
    assert (tokens[1].line, tokens[1].col) == (2, 1)
