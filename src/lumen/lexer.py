"""Лексер LUMEN: исходный текст → список токенов."""

from .errors import LumenSyntaxError
from .tokens import KEYWORDS, Token, TokenType


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.n = len(source)
        self.i = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> list[Token]:
        tokens = []
        while True:
            self._skip_ignored()
            if self.i >= self.n:
                break
            tokens.append(self._next_token())
        tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return tokens

    def _peek(self) -> str:
        if self.i >= self.n:
            return ""
        return self.source[self.i]

    def _peek_at(self, offset: int) -> str:
        j = self.i + offset
        if j >= self.n:
            return ""
        return self.source[j]

    def _advance_char(self) -> str:
        ch = self.source[self.i]
        self.i += 1
        self.col += 1
        return ch

    def _newline(self) -> None:
        if self._peek() == "\r":
            self._advance_char()
            if self._peek() == "\n":
                self._advance_char()
        elif self._peek() == "\n":
            self._advance_char()
        self.line += 1
        self.col = 1

    def _skip_ignored(self) -> None:
        while self.i < self.n:
            ch = self._peek()
            if ch in " \t":
                self._advance_char()
                continue
            if ch in "\r\n":
                self._newline()
                continue
            if ch == "#":
                while self.i < self.n and self._peek() not in "\r\n":
                    self._advance_char()
                continue
            break

    def _source_line(self, line: int) -> str | None:
        lines = self.source.splitlines()
        if 1 <= line <= len(lines):
            return lines[line - 1]
        return None

    def _error(self, message: str, line: int, col: int) -> None:
        raise LumenSyntaxError(message, line, col, self._source_line(line))

    def _next_token(self) -> Token:
        line, col = self.line, self.col
        ch = self._peek()

        if ch.isdigit():
            return self._number(line, col)
        if ch == '"':
            return self._string(line, col)
        if ch.isalpha() or ch == "_":
            return self._ident(line, col)

        two = ch + self._peek_at(1)
        mapping = {
            "==": TokenType.EQ,
            "!=": TokenType.NEQ,
            "~=": TokenType.PATH_EQ,
            "<=": TokenType.LEQ,
            ">=": TokenType.GEQ,
            "+=": TokenType.PLUS_ASSIGN,
            "-=": TokenType.MINUS_ASSIGN,
            "*=": TokenType.STAR_ASSIGN,
            "/=": TokenType.SLASH_ASSIGN,
        }
        if two in mapping:
            self._advance_char()
            self._advance_char()
            return Token(mapping[two], two, line, col)

        singles = {
            "=": TokenType.ASSIGN,
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
            "<": TokenType.LT,
            ">": TokenType.GT,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
            ".": TokenType.DOT,
            "|": TokenType.PIPE,
        }
        if ch in singles:
            self._advance_char()
            return Token(singles[ch], ch, line, col)

        self._error(f"unexpected character {ch!r}", line, col)
        raise AssertionError("unreachable")

    def _number(self, line: int, col: int) -> Token:
        start = self.i
        while self._peek().isdigit():
            self._advance_char()
        if self._peek() == "." and self._peek_at(1).isdigit():
            self._advance_char()
            while self._peek().isdigit():
                self._advance_char()
            text = self.source[start:self.i]
            return Token(TokenType.FLOAT_LIT, text, line, col)
        text = self.source[start:self.i]
        return Token(TokenType.INT_LIT, text, line, col)

    def _string(self, line: int, col: int) -> Token:
        self._advance_char()
        chars = []
        while self.i < self.n and self._peek() != '"':
            ch = self._advance_char()
            if ch == "\\":
                if self.i >= self.n:
                    self._error("unterminated string", line, col)
                esc = self._advance_char()
                mapping = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
                if esc not in mapping:
                    self._error(f"unknown escape \\{esc}", line, col)
                chars.append(mapping[esc])
                continue
            if ch in "\r\n":
                self._error("unterminated string", line, col)
            chars.append(ch)
        if self._peek() != '"':
            self._error("unterminated string", line, col)
        self._advance_char()
        return Token(TokenType.STR_LIT, "".join(chars), line, col)

    def _ident(self, line: int, col: int) -> Token:
        start = self.i
        while self._peek().isalnum() or self._peek() == "_":
            self._advance_char()
        text = self.source[start:self.i]
        kind = KEYWORDS.get(text, TokenType.IDENT)
        return Token(kind, text, line, col)
