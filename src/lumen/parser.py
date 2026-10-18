"""Рекурсивный нисходящий парсер LUMEN."""

from .ast_nodes import (
    AsExpr,
    AssignStmt,
    BinOp,
    BreakStmt,
    ContextStmt,
    DissonanceStmt,
    ContinueStmt,
    ExprStmt,
    FieldAccess,
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
    Program,
    RemoveStmt,
    RequireClause,
    ReturnStmt,
    StateDecl,
    TransformClause,
    UnaryOp,
    WhenClause,
    WhileStmt,
    ForStmt,
)
from .errors import LumenSyntaxError
from .tokens import LLM_KEYWORDS, RESERVED, Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token], source: str = ""):
        self.tokens = tokens
        self.source = source
        self.pos = 0
        self.loop_depth = 0
        self.morph_depth = 0
        self.inside_transform = False

    def parse(self) -> Program:
        body = []
        while not self._at_end():
            body.append(self.parse_statement())
        return Program(body)

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _check(self, *types: TokenType) -> bool:
        return self._peek().type in types

    def _advance(self) -> Token:
        tok = self._peek()
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _match(self, *types: TokenType) -> bool:
        if self._check(*types):
            self._advance()
            return True
        return False

    def _source_line(self, line: int) -> str | None:
        if not self.source or not line:
            return None
        lines = self.source.splitlines()
        if 1 <= line <= len(lines):
            return lines[line - 1]
        return None

    def _error(self, message: str, token: Token | None = None) -> None:
        tok = token or self._peek()
        err = LumenSyntaxError(message, tok.line, tok.col, self._source_line(tok.line))
        err.incomplete = tok.type == TokenType.EOF
        raise err

    def _expect(self, kind: TokenType) -> Token:
        tok = self._peek()
        if tok.type != kind:
            got = tok.type.name if tok.type == TokenType.EOF else (tok.value or tok.type.name)
            self._error(f"expected {kind.name}, got {got}", tok)
        return self._advance()

    def _reject_reserved(self, token: Token) -> None:
        if token.type in RESERVED:
            self._error(f"'{token.value}' is reserved", token)

    def parse_statement(self):
        tok = self._peek()
        self._reject_reserved(tok)
        if tok.type == TokenType.REQUIRE:
            self._error("require is only allowed inside a transform", tok)
        if tok.type == TokenType.DEF:
            return self.parse_func_def()
        if tok.type == TokenType.IF:
            return self.parse_if()
        if tok.type == TokenType.WHILE:
            return self.parse_while()
        if tok.type == TokenType.FOR:
            return self.parse_for()
        if tok.type == TokenType.CONTEXT:
            return self.parse_context()
        if tok.type == TokenType.DISSONANCE:
            return self.parse_dissonance()
        if tok.type == TokenType.MORPH:
            return self.parse_morph()
        if tok.type == TokenType.RETURN:
            return self.parse_return()
        if tok.type == TokenType.BREAK:
            if self.loop_depth == 0:
                self._error("break outside loop", tok)
            self._advance()
            return BreakStmt(line=tok.line, col=tok.col)
        if tok.type == TokenType.CONTINUE:
            if self.loop_depth == 0:
                self._error("continue outside loop", tok)
            self._advance()
            return ContinueStmt(line=tok.line, col=tok.col)
        if tok.type == TokenType.REMOVE:
            return self.parse_remove()
        if tok.type in LLM_KEYWORDS:
            return self.parse_llm_directive()
        if self._looks_like_assign():
            return self.parse_assign()
        expr = self.parse_expression()
        return ExprStmt(expr, line=expr.line, col=expr.col)

    def _looks_like_assign(self) -> bool:
        saved = self.pos
        if not self._check(TokenType.IDENT, TokenType.STATE):
            return False
        self._advance()
        while self._match(TokenType.DOT):
            if not self._check(TokenType.IDENT, TokenType.STATE):
                self.pos = saved
                return False
            self._advance()
        is_assign = self._check(
            TokenType.ASSIGN,
            TokenType.PLUS_ASSIGN,
            TokenType.MINUS_ASSIGN,
            TokenType.STAR_ASSIGN,
            TokenType.SLASH_ASSIGN,
        )
        self.pos = saved
        return is_assign

    def _parse_name(self) -> tuple[str, Token]:
        tok = self._peek()
        if tok.type == TokenType.IDENT:
            self._advance()
            return tok.value, tok
        if tok.type == TokenType.STATE:
            self._advance()
            return "state", tok
        self._error(f"expected name, got {tok.value or tok.type.name}", tok)
        raise AssertionError("unreachable")

    def parse_assign(self) -> AssignStmt:
        name, tok = self._parse_name()
        target = Ident(name, tok.line, tok.col)
        while self._match(TokenType.DOT):
            field, ftok = self._parse_name()
            target = FieldAccess(target, field, ftok.line, ftok.col)
        op_tok = self._advance()
        value = self.parse_expression()
        return AssignStmt(target, op_tok.value, value, tok.line, tok.col)

    def _statements_until(self, *stop: TokenType) -> list:
        body = []
        while not self._at_end() and not self._check(*stop):
            body.append(self.parse_statement())
        return body

    def parse_func_def(self) -> FuncDef:
        tok = self._expect(TokenType.DEF)
        name, _ = self._parse_name()
        self._expect(TokenType.LPAREN)
        params = self._param_list()
        self._expect(TokenType.RPAREN)
        when_clauses = []
        body = []
        if self._check(TokenType.WHEN):
            while self._check(TokenType.WHEN):
                when_clauses.append(self.parse_when_clause(params))
        else:
            body = self._statements_until(TokenType.END)
        self._expect(TokenType.END)
        return FuncDef(name, params, body, when_clauses, tok.line, tok.col)

    def _param_list(self) -> list[str]:
        if self._check(TokenType.RPAREN, TokenType.PIPE):
            return []
        params = []
        name, _ = self._parse_name()
        params.append(name)
        while self._match(TokenType.COMMA):
            name, _ = self._parse_name()
            params.append(name)
        return params

    def parse_when_clause(self, params: list[str]) -> WhenClause:
        tok = self._expect(TokenType.WHEN)
        type_name, _ = self._parse_name()
        if self._match(TokenType.THEN):
            body = self._statements_until(TokenType.WHEN, TokenType.END)
        elif self._match(TokenType.DO):
            body = self._statements_until(TokenType.END)
            self._expect(TokenType.END)
        else:
            self._error("expected 'then' or 'do' after when")
            body = []
        return WhenClause(type_name, list(params), body, tok.line, tok.col)

    def parse_if(self) -> IfStmt:
        tok = self._expect(TokenType.IF)
        condition = self.parse_expression()
        then_body = self._statements_until(TokenType.ELSIF, TokenType.ELSE, TokenType.END)
        elsif_clauses = []
        while self._match(TokenType.ELSIF):
            cond = self.parse_expression()
            body = self._statements_until(TokenType.ELSIF, TokenType.ELSE, TokenType.END)
            elsif_clauses.append((cond, body))
        else_body = []
        if self._match(TokenType.ELSE):
            else_body = self._statements_until(TokenType.END)
        self._expect(TokenType.END)
        return IfStmt(condition, then_body, elsif_clauses, else_body, tok.line, tok.col)

    def parse_while(self) -> WhileStmt:
        tok = self._expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.loop_depth += 1
        try:
            body = self._statements_until(TokenType.END)
        finally:
            self.loop_depth -= 1
        self._expect(TokenType.END)
        return WhileStmt(condition, body, tok.line, tok.col)

    def parse_for(self) -> ForStmt:
        tok = self._expect(TokenType.FOR)
        var, _ = self._parse_name()
        self._expect(TokenType.IN)
        iterable = self.parse_expression()
        self.loop_depth += 1
        try:
            body = self._statements_until(TokenType.END)
        finally:
            self.loop_depth -= 1
        self._expect(TokenType.END)
        return ForStmt(var, iterable, body, tok.line, tok.col)

    def parse_dissonance(self) -> DissonanceStmt:
        tok = self._expect(TokenType.DISSONANCE)
        mode, mode_tok = self._parse_name()
        if mode not in ("strict", "soft", "creative"):
            self._error("dissonance mode must be strict, soft, or creative", mode_tok)
        body = self._statements_until(TokenType.END)
        self._expect(TokenType.END)
        return DissonanceStmt(mode, body, tok.line, tok.col)

    def parse_context(self) -> ContextStmt:
        tok = self._expect(TokenType.CONTEXT)
        name, _ = self._parse_name()
        body = self._statements_until(TokenType.END)
        self._expect(TokenType.END)
        return ContextStmt(name, body, tok.line, tok.col)

    def parse_morph(self) -> MorphStmt:
        tok = self._expect(TokenType.MORPH)
        if self.inside_transform:
            self._error(
                "declare a nested morph in the morph body, not inside a transform",
                tok,
            )
        name, _ = self._parse_name()
        self.morph_depth += 1
        try:
            state_decls = []
            transforms = []
            directives = []
            children = []
            while not self._at_end() and not self._check(TokenType.END):
                if self._check(TokenType.STATE):
                    state_decls.append(self.parse_state_decl())
                elif self._check(TokenType.TRANSFORM):
                    transforms.append(self.parse_transform())
                elif self._check(TokenType.MORPH):
                    children.append(self.parse_morph())
                elif self._peek().type in LLM_KEYWORDS:
                    directives.append(self.parse_llm_directive())
                else:
                    self._error(
                        "expected state, transform, nested morph, or a documentation directive"
                    )
        finally:
            self.morph_depth -= 1
        self._expect(TokenType.END)
        return MorphStmt(
            name, state_decls, transforms, directives, tok.line, tok.col, children
        )

    def parse_state_decl(self) -> StateDecl:
        tok = self._expect(TokenType.STATE)
        name, _ = self._parse_name()
        self._expect(TokenType.COLON)
        type_name, _ = self._parse_name()
        default = None
        if self._match(TokenType.ASSIGN):
            default = self.parse_expression()
        return StateDecl(name, type_name, default, tok.line, tok.col)

    def parse_transform(self) -> TransformClause:
        tok = self._expect(TokenType.TRANSFORM)
        if not self._check(TokenType.STR_LIT):
            self._error("transform name must be a string")
        name_tok = self._advance()
        body = []
        skip = None
        directives = []
        requires = []
        self.inside_transform = True
        try:
            while not self._at_end() and not self._check(TokenType.END):
                if self._check(TokenType.SKIP):
                    self._advance()
                    self._expect(TokenType.IF)
                    skip = self.parse_expression()
                elif self._check(TokenType.REQUIRE):
                    req_tok = self._advance()
                    requires.append(
                        RequireClause(self.parse_expression(), req_tok.line, req_tok.col)
                    )
                elif self._peek().type in LLM_KEYWORDS:
                    directives.append(self.parse_llm_directive())
                else:
                    body.append(self.parse_statement())
        finally:
            self.inside_transform = False
        self._expect(TokenType.END)
        return TransformClause(
            name_tok.value, body, skip, directives, tok.line, tok.col, requires
        )

    def parse_llm_directive(self) -> LLMDirective:
        tok = self._advance()
        if not self._check(TokenType.STR_LIT):
            self._error(f"{tok.value} expects a string")
        text = self._advance()
        return LLMDirective(tok.value, text.value, tok.line, tok.col)

    def parse_return(self) -> ReturnStmt:
        tok = self._expect(TokenType.RETURN)
        if self._at_statement_boundary():
            return ReturnStmt(None, tok.line, tok.col)
        return ReturnStmt(self.parse_expression(), tok.line, tok.col)

    def _at_statement_boundary(self) -> bool:
        return self._check(
            TokenType.EOF,
            TokenType.END,
            TokenType.ELSE,
            TokenType.ELSIF,
            TokenType.WHEN,
            TokenType.DEF,
            TokenType.IF,
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.CONTEXT,
            TokenType.DISSONANCE,
            TokenType.MORPH,
            TokenType.RETURN,
            TokenType.BREAK,
            TokenType.CONTINUE,
            TokenType.REMOVE,
            TokenType.STATE,
            TokenType.TRANSFORM,
            TokenType.SKIP,
            TokenType.REQUIRE,
            *LLM_KEYWORDS,
            *RESERVED,
        )

    def parse_remove(self) -> RemoveStmt:
        tok = self._expect(TokenType.REMOVE)
        field, _ = self._parse_name()
        self._expect(TokenType.FROM)
        obj, _ = self._parse_name()
        return RemoveStmt(field, obj, tok.line, tok.col)

    def parse_expression(self):
        return self.parse_logical()

    def parse_logical(self):
        if self._check(TokenType.NOT):
            tok = self._advance()
            operand = self.parse_logical()
            return UnaryOp("not", operand, tok.line, tok.col)
        left = self.parse_comparison()
        while self._check(TokenType.AND, TokenType.OR):
            op = self._advance()
            right = self.parse_comparison()
            left = BinOp(left, op.value, right, op.line, op.col)
        return left

    def parse_comparison(self):
        left = self.parse_additive()
        ops = (
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.PATH_EQ,
            TokenType.LT,
            TokenType.GT,
            TokenType.LEQ,
            TokenType.GEQ,
        )
        while self._check(*ops):
            op = self._advance()
            right = self.parse_additive()
            left = BinOp(left, op.value, right, op.line, op.col)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self._check(TokenType.PLUS, TokenType.MINUS):
            op = self._advance()
            right = self.parse_multiplicative()
            left = BinOp(left, op.value, right, op.line, op.col)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self._check(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._advance()
            right = self.parse_unary()
            left = BinOp(left, op.value, right, op.line, op.col)
        return left

    def parse_unary(self):
        if self._check(TokenType.MINUS, TokenType.NOT):
            op = self._advance()
            operand = self.parse_unary()
            return UnaryOp(op.value, operand, op.line, op.col)
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self._match(TokenType.DOT):
                field, tok = self._parse_name()
                expr = FieldAccess(expr, field, tok.line, tok.col)
            elif self._match(TokenType.LBRACKET):
                index = self.parse_expression()
                self._expect(TokenType.RBRACKET)
                expr = IndexAccess(expr, index, expr.line, expr.col)
            elif self._match(TokenType.LPAREN):
                args = []
                if not self._check(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self._match(TokenType.COMMA):
                        args.append(self.parse_expression())
                self._expect(TokenType.RPAREN)
                expr = FuncCall(expr, args, expr.line, expr.col)
            elif self._match(TokenType.AS):
                type_name, tok = self._parse_name()
                expr = AsExpr(expr, type_name, tok.line, tok.col)
            elif self._match(TokenType.IS):
                type_name, tok = self._parse_name()
                expr = IsExpr(expr, type_name, tok.line, tok.col)
            else:
                break
        return expr

    def parse_primary(self):
        tok = self._peek()
        if tok.type == TokenType.INT_LIT:
            self._advance()
            return Literal(int(tok.value), tok.line, tok.col)
        if tok.type == TokenType.FLOAT_LIT:
            self._advance()
            return Literal(float(tok.value), tok.line, tok.col)
        if tok.type == TokenType.STR_LIT:
            self._advance()
            return Literal(tok.value, tok.line, tok.col)
        if tok.type == TokenType.TRUE:
            self._advance()
            return Literal(True, tok.line, tok.col)
        if tok.type == TokenType.FALSE:
            self._advance()
            return Literal(False, tok.line, tok.col)
        if tok.type == TokenType.NULL:
            self._advance()
            return Literal(None, tok.line, tok.col)
        if tok.type in (TokenType.IDENT, TokenType.STATE):
            name, tok = self._parse_name()
            return Ident(name, tok.line, tok.col)
        if tok.type == TokenType.LBRACKET:
            return self.parse_list_literal()
        if tok.type == TokenType.LBRACE:
            return self.parse_map_literal()
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self.parse_expression()
            self._expect(TokenType.RPAREN)
            return expr
        if tok.type == TokenType.DO:
            return self.parse_lambda()
        if self._at_end():
            self._error("unexpected end of input", tok)
        self._error(f"unexpected token '{tok.value}'", tok)
        raise AssertionError("unreachable")

    def parse_list_literal(self) -> ListLiteral:
        tok = self._expect(TokenType.LBRACKET)
        elements = []
        if not self._check(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            while self._match(TokenType.COMMA):
                if self._check(TokenType.RBRACKET):
                    break
                elements.append(self.parse_expression())
        self._expect(TokenType.RBRACKET)
        return ListLiteral(elements, tok.line, tok.col)

    def parse_map_literal(self) -> MapLiteral:
        tok = self._expect(TokenType.LBRACE)
        entries = []
        if not self._check(TokenType.RBRACE):
            entries.append(self._map_entry())
            while self._match(TokenType.COMMA):
                if self._check(TokenType.RBRACE):
                    break
                entries.append(self._map_entry())
        self._expect(TokenType.RBRACE)
        return MapLiteral(entries, tok.line, tok.col)

    def _map_entry(self):
        name, _ = self._parse_name()
        self._expect(TokenType.COLON)
        value = self.parse_expression()
        return (name, value)

    def parse_lambda(self) -> LambdaExpr:
        tok = self._expect(TokenType.DO)
        self._expect(TokenType.PIPE)
        params = self._param_list()
        self._expect(TokenType.PIPE)
        body = self._statements_until(TokenType.END)
        self._expect(TokenType.END)
        return LambdaExpr(params, body, tok.line, tok.col)
