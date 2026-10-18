"""Токены лексера LUMEN."""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    INT_LIT = auto()
    FLOAT_LIT = auto()
    STR_LIT = auto()
    BOOL_LIT = auto()
    NULL_LIT = auto()

    DEF = auto()
    END = auto()
    IF = auto()
    ELSE = auto()
    ELSIF = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    DO = auto()
    RETURN = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    WHEN = auto()
    THEN = auto()
    AS = auto()
    IS = auto()
    CONTEXT = auto()
    DISSONANCE = auto()
    REMOVE = auto()
    FROM = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    MORPH = auto()
    TRANSFORM = auto()
    STATE = auto()
    SKIP = auto()
    SHADOW = auto()
    THINK = auto()
    REASON = auto()
    EXPLAIN = auto()
    BREAK = auto()
    CONTINUE = auto()
    BECOME = auto()
    GROW = auto()
    EXTEND = auto()
    REQUIRE = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ = auto()
    NEQ = auto()
    PATH_EQ = auto()
    LT = auto()
    GT = auto()
    LEQ = auto()
    GEQ = auto()
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    STAR_ASSIGN = auto()
    SLASH_ASSIGN = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    COLON = auto()
    DOT = auto()
    PIPE = auto()

    IDENT = auto()
    EOF = auto()


KEYWORDS = {
    "def": TokenType.DEF,
    "end": TokenType.END,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elsif": TokenType.ELSIF,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "do": TokenType.DO,
    "return": TokenType.RETURN,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "when": TokenType.WHEN,
    "then": TokenType.THEN,
    "as": TokenType.AS,
    "is": TokenType.IS,
    "context": TokenType.CONTEXT,
    "dissonance": TokenType.DISSONANCE,
    "remove": TokenType.REMOVE,
    "from": TokenType.FROM,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
    "morph": TokenType.MORPH,
    "transform": TokenType.TRANSFORM,
    "state": TokenType.STATE,
    "skip": TokenType.SKIP,
    "shadow": TokenType.SHADOW,
    "think": TokenType.THINK,
    "reason": TokenType.REASON,
    "explain": TokenType.EXPLAIN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "become": TokenType.BECOME,
    "grow": TokenType.GROW,
    "extend": TokenType.EXTEND,
    "require": TokenType.REQUIRE,
}

RESERVED = {
    TokenType.BECOME,
    TokenType.GROW,
    TokenType.EXTEND,
}

LLM_KEYWORDS = {
    TokenType.SHADOW,
    TokenType.THINK,
    TokenType.REASON,
    TokenType.EXPLAIN,
}


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    col: int
