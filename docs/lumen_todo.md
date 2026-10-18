# Подробное Пошаговое TODO — разработка интерпретатора LUMEN v0.0.4
**Версия:** 0.0.4  
**Предыдущая версия:** 0.0.3  
**Исполнитель:** разработчик (модель или человек)  
**Стек:** Python 3.10+  
**Зависимости:** только стандартная библиотека Python (без Lark/ANTLR на первом этапе — ручной парсер)  
**Результат:** работающий интерпретатор + CLI + REPL + morph-блоки + тесты ≥ 70%  
**Дата фиксации:** 18.10.2026

> **Состояние на 18.10.2026.** Этапы 1–11 выполнены в пакете `src/lumen/`. Версия пакета `0.0.4`, CLI печатает `lumen 0.0.4`. Дерево `src/*.py` и `tools/` ниже — исходный план этапа 0; рабочий код в него не раскладывался. Порог покрытия 70% и проверка на Linux остаются открытыми. Сверх плана в прототипе уже есть вложенные morph, `~=`, `dissonance` и `require`.

---

## ЭТАП 0. Подготовка проекта

### 0.1. Структура директорий
Создать следующую структуру (все пустые файлы создать сразу):

```
lumen/
├── src/
│   ├── __init__.py
│   ├── lexer.py
│   ├── tokens.py
│   ├── parser.py
│   ├── ast_nodes.py
│   ├── interpreter.py
│   ├── environment.py
│   ├── types.py
│   ├── errors.py
│   ├── builtins.py
│   ├── context.py
│   ├── morph.py          # morph-блок, transform, state, history
│   └── llm_native.py     # shadow, think, reason, explain
├── tools/
│   ├── __init__.py
│   ├── cli.py
│   └── repl.py
├── tests/
│   ├── __init__.py
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_interpreter.py
│   ├── test_transforms.py
│   ├── test_evolution.py
│   ├── test_errors.py
│   ├── test_morph.py      # тесты morph-блока
│   ├── test_llm_native.py # тесты LLM-native конструкций
│   └── golden/
│       ├── hello.lumen
│       ├── hello.expected
│       ├── transforms.lumen
│       └── transforms.expected
├── examples/
│   ├── hello.lumen
│   ├── transforms.lumen
│   ├── evolution.lumen
│   └── living_map.lumen
├── docs/
├── README.md
└── lumen.py          ← точка входа CLI
```

### 0.2. Конфигурация Python
Создать `pyproject.toml`:
```toml
[project]
name = "lumen-lang"
version = "0.1.0"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 0.3. Точка входа
Создать `lumen.py` в корне:
```python
#!/usr/bin/env python3
from tools.cli import main
if __name__ == "__main__":
    main()
```

**Проверка.** Ранний план ждал строку `LUMEN 0.1.0`. Прототип печатает `lumen 0.0.4`. Код CLI — `src/lumen/cli.py`.

---

## ЭТАП 1. Токены и лексер

### 1.1. Файл `src/tokens.py` — перечисление токенов

Создать класс `TokenType` (enum) со следующими значениями:

**Литералы:**
- `INT_LIT` — целое число
- `FLOAT_LIT` — вещественное число
- `STR_LIT` — строка
- `BOOL_LIT` — `true` / `false`
- `NULL_LIT` — `null`

**Ключевые слова:**
- `DEF`, `END`, `IF`, `ELSE`, `ELSIF`
- `WHILE`, `FOR`, `IN`, `DO`, `RETURN`
- `AND`, `OR`, `NOT`
- `WHEN`, `THEN`, `AS`, `IS`
- `CONTEXT`, `REMOVE`, `FROM`
- `TRUE`, `FALSE`, `NULL`
- `MORPH`, `TRANSFORM`, `STATE`, `SKIP`
- `SHADOW`, `THINK`, `REASON`, `EXPLAIN`
- `BREAK`, `CONTINUE`
- **(зарезервированы):** `BECOME`, `GROW`, `EXTEND`, `REQUIRE`

**Операторы:**
- `PLUS`, `MINUS`, `STAR`, `SLASH`, `PERCENT`
- `EQ` (`==`), `NEQ` (`!=`), `LT`, `GT`, `LEQ`, `GEQ`
- `ASSIGN` (`=`), `PLUS_ASSIGN`, `MINUS_ASSIGN`, `STAR_ASSIGN`, `SLASH_ASSIGN`

**Разделители:**
- `LPAREN`, `RPAREN` — `(` `)`
- `LBRACKET`, `RBRACKET` — `[` `]`
- `LBRACE`, `RBRACE` — `{` `}`
- `COMMA`, `COLON`, `DOT`, `PIPE`

**Специальные:**
- `IDENT` — идентификатор
- `NEWLINE` — перенос строки (для информации, не обязателен семантически)
- `EOF` — конец файла

Создать класс `Token(type: TokenType, value: str, line: int, col: int)`.

### 1.2. Файл `src/lexer.py` — лексер

Создать класс `Lexer`:

```python
class Lexer:
    def __init__(self, source: str): ...
    def tokenize(self) -> list[Token]: ...
    def _next_token(self) -> Token: ...
```

#### 1.2.1. Метод `tokenize()`
- Пройти по `source` посимвольно.
- Пропускать пробелы, табуляции, `\r`.
- Пропускать `\n` (не несут семантики, но обновлять счётчик строк).
- Пропускать комментарии: при встрече `#` — читать до `\n`.
- Для каждого токена вызывать `_next_token()` и добавлять в список.
- В конце добавить токен `EOF`.

#### 1.2.2. Метод `_next_token()` — логика распознавания

**Числа:**
- Если текущий символ — цифра → читать цифры. Отрицательные числа обрабатываются через унарный минус в парсере (`UnaryOp('-', literal)`), а не в лексере. Лексер всегда создаёт `MINUS` + `INT_LIT`/`FLOAT_LIT`.
- Если есть `.` — создать `FLOAT_LIT`, иначе `INT_LIT`.

**Строки:**
- Если `"` → читать до закрывающего `"`, обрабатывая escape-последовательности `\\`, `\"`, `\n`, `\t`, `\r`.
- Создать `STR_LIT` с уже обработанным содержимым.

**Идентификаторы и ключевые слова:**
- Если буква или `_` → читать `[a-zA-Z0-9_]+`.
- Проверить по словарю ключевых слов:
  ```python
  KEYWORDS = {
      "def": TokenType.DEF, "end": TokenType.END,
      "if": TokenType.IF, "else": TokenType.ELSE, "elsif": TokenType.ELSIF,
      "while": TokenType.WHILE, "for": TokenType.FOR, "in": TokenType.IN,
      "do": TokenType.DO, "return": TokenType.RETURN,
      "and": TokenType.AND, "or": TokenType.OR, "not": TokenType.NOT,
      "when": TokenType.WHEN, "then": TokenType.THEN,
      "as": TokenType.AS, "is": TokenType.IS,
      "context": TokenType.CONTEXT, "remove": TokenType.REMOVE, "from": TokenType.FROM,
      "true": TokenType.TRUE, "false": TokenType.FALSE, "null": TokenType.NULL,
      # morph-блок и LLM-native
      "morph": TokenType.MORPH, "transform": TokenType.TRANSFORM,
      "state": TokenType.STATE, "skip": TokenType.SKIP,
      "shadow": TokenType.SHADOW, "think": TokenType.THINK,
      "reason": TokenType.REASON, "explain": TokenType.EXPLAIN,
      # управление циклами
      "break": TokenType.BREAK, "continue": TokenType.CONTINUE,
      # зарезервированы для v0.2
      "become": TokenType.BECOME, "grow": TokenType.GROW,
      "extend": TokenType.EXTEND, "require": TokenType.REQUIRE,
  }
  ```
- Если ключевое слово — вернуть соответствующий тип, иначе `IDENT`.

**Операторы (двухсимвольные — проверять первыми):**
- `==` → `EQ`, `!=` → `NEQ`, `<=` → `LEQ`, `>=` → `GEQ`
- `+=` → `PLUS_ASSIGN`, `-=` → `MINUS_ASSIGN`, `*=` → `STAR_ASSIGN`, `/=` → `SLASH_ASSIGN`

**Операторы (односимвольные):**
- `=` → `ASSIGN`, `+` → `PLUS`, `-` → `MINUS`, `*` → `STAR`, `/` → `SLASH`, `%` → `PERCENT`
- `<` → `LT`, `>` → `GT`
- `(` → `LPAREN`, `)` → `RPAREN`
- `[` → `LBRACKET`, `]` → `RBRACKET`
- `{` → `LBRACE`, `}` → `RBRACE`
- `,` → `COMMA`, `:` → `COLON`, `.` → `DOT`, `|` → `PIPE`

**Неизвестный символ:** поднять `LumenSyntaxError`.

### 1.3. Тесты лексера (`tests/test_lexer.py`)

Написать тесты для:
- [ ] Пустая строка → только `[EOF]`
- [ ] `42` → `[INT_LIT(42), EOF]`
- [ ] `3.14` → `[FLOAT_LIT(3.14), EOF]`
- [ ] `"hello"` → `[STR_LIT("hello"), EOF]`
- [ ] `"hell\"o"` → `[STR_LIT('hell"o'), EOF]`
- [ ] `true` → `[TRUE, EOF]`, `false` → `[FALSE, EOF]`
- [ ] `null` → `[NULL, EOF]`
- [ ] `def foo end` → `[DEF, IDENT(foo), END, EOF]`
- [ ] `x = 42` → `[IDENT(x), ASSIGN, INT_LIT(42), EOF]`
- [ ] `==`, `!=`, `<=`, `>=` — двухсимвольные операторы
- [ ] `# комментарий\nx` → `[IDENT(x), EOF]`
- [ ] Пробелы и переносы строк игнорируются корректно
- [ ] Проверка номеров строк и колонок в токенах

**Критерий:** все тесты лексера зелёные.

---

## ЭТАП 2. AST-узлы

### 2.1. Файл `src/ast_nodes.py`

Создать датаклассы (или namedtuple) для каждого типа узла AST.  
Каждый узел должен хранить `line: int` для сообщений об ошибках.

```python
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Program:
    body: list  # list[Statement]
    line: int = 0

# --- Statements ---

@dataclass
class AssignStmt:
    target: Any        # IDENT или цепочка .field
    op: str            # '=', '+=', '-=', '*=', '/='
    value: Any         # expression
    line: int = 0

@dataclass
class FuncDef:
    name: str
    params: list[str]
    body: list         # list[Statement] или list[WhenClause]
    line: int = 0

@dataclass
class WhenClause:
    type_name: str
    body: list         # list[Statement]
    line: int = 0

@dataclass
class IfStmt:
    condition: Any
    then_body: list
    elsif_clauses: list   # list[(condition, body)]
    else_body: list
    line: int = 0

@dataclass
class WhileStmt:
    condition: Any
    body: list
    line: int = 0

@dataclass
class ForStmt:
    var: str
    iterable: Any
    body: list
    line: int = 0

@dataclass
class ContextStmt:
    name: str
    body: list
    line: int = 0

@dataclass
class ReturnStmt:
    value: Any  # Optional
    line: int = 0

@dataclass
class RemoveStmt:
    field: str
    obj: str
    line: int = 0

@dataclass
class BreakStmt:
    line: int = 0

@dataclass
class ContinueStmt:
    line: int = 0

@dataclass
class ExprStmt:
    expr: Any
    line: int = 0

# --- Expressions ---

@dataclass
class BinOp:
    left: Any
    op: str
    right: Any
    line: int = 0

@dataclass
class UnaryOp:
    op: str
    operand: Any
    line: int = 0

@dataclass
class Literal:
    value: Any   # int, float, str, bool, None
    line: int = 0

@dataclass
class Ident:
    name: str
    line: int = 0

@dataclass
class FieldAccess:
    obj: Any
    field: str
    line: int = 0

@dataclass
class IndexAccess:
    obj: Any
    index: Any
    line: int = 0

@dataclass
class FuncCall:
    callee: Any
    args: list
    line: int = 0

@dataclass
class AsExpr:
    value: Any
    type_name: str
    line: int = 0

@dataclass
class IsExpr:
    value: Any
    type_name: str
    line: int = 0

@dataclass
class ListLiteral:
    elements: list
    line: int = 0

@dataclass
class MapLiteral:
    entries: list   # list[(key_str, value_expr)]
    line: int = 0

@dataclass
class LambdaExpr:
    params: list[str]
    body: list
    line: int = 0

# --- Morph-блок ---

@dataclass
class MorphStmt:
    name: str
    state_decls: list       # list[StateDecl]
    transforms: list        # list[TransformClause]
    llm_directives: list    # list[LLMDirective]
    line: int = 0

@dataclass
class StateDecl:
    name: str
    type_name: str
    default: Any            # expression или None
    line: int = 0

@dataclass
class TransformClause:
    name: str               # строковое имя шага
    body: list              # list[Statement]
    skip_condition: Any     # expression или None
    llm_directives: list    # list[LLMDirective]
    line: int = 0

@dataclass
class LLMDirective:
    kind: str               # "shadow" | "think" | "reason" | "explain"
    text: str
    line: int = 0
```

---

## ЭТАП 3. Парсер

### 3.1. Файл `src/parser.py`

Реализовать **рекурсивный нисходящий парсер** (recursive descent).

```python
class Parser:
    def __init__(self, tokens: list[Token]): ...
    def parse(self) -> Program: ...
    
    # вспомогательные
    def _peek(self) -> Token: ...
    def _advance(self) -> Token: ...
    def _expect(self, type: TokenType) -> Token: ...
    def _match(self, *types: TokenType) -> bool: ...
    def _at_end(self) -> bool: ...
```

### 3.2. Реализация методов парсера

#### 3.2.1. `parse()` → `Program`
Читать операторы пока не `EOF`.

#### 3.2.2. `parse_statement()` → `Statement`
По текущему токену выбирать:
- `DEF` → `parse_func_def()`
- `IF` → `parse_if()`
- `WHILE` → `parse_while()`
- `FOR` → `parse_for()`
- `CONTEXT` → `parse_context()`
- `MORPH` → `parse_morph()`
- `RETURN` → `parse_return()`
- `BREAK` → `BreakStmt(line=current_line)`
- `CONTINUE` → `ContinueStmt(line=current_line)`
- `REMOVE` → `parse_remove()`
- иначе → попытаться разобрать как присваивание или выражение:
  - если `IDENT` и следующий — `ASSIGN` или `+=/-=/*=/=` → `parse_assign()`
  - если `IDENT DOT ... ASSIGN` → `parse_field_assign()`
  - иначе → `ExprStmt(parse_expression())`

#### 3.2.3. `parse_func_def()` → `FuncDef`
```
DEF IDENT LPAREN [params] RPAREN body END
```
- `body` — если первый токен тела это `WHEN` → читать `when`-клаузы.
- Иначе — читать обычные операторы до `END`.

#### 3.2.4. `parse_when_clause()` → `WhenClause`
```
WHEN type_name THEN statement+
WHEN type_name DO statement* END
```

#### 3.2.5. `parse_if()` → `IfStmt`
```
IF expr body [ELSIF expr body]* [ELSE body] END
```

#### 3.2.6. `parse_while()` → `WhileStmt`
```
WHILE expr body END
```

#### 3.2.7. `parse_for()` → `ForStmt`
```
FOR IDENT IN expr body END
```

#### 3.2.8. `parse_context()` → `ContextStmt`
```
CONTEXT IDENT body END
```

#### 3.2.8a. `parse_morph()` → `MorphStmt`
```
MORPH IDENT morph_body END
morph_body = (state_decl | transform_clause | llm_directive)*
state_decl = STATE IDENT COLON type_name (ASSIGN expr)?
transform_clause = TRANSFORM STR_LIT transform_body END
transform_body = (skip_clause | llm_directive | statement)*
skip_clause = SKIP IF expr
llm_directive = (SHADOW | THINK | REASON | EXPLAIN) STR_LIT
```

#### 3.2.9. `parse_return()` → `ReturnStmt`
```
RETURN [expr]
```

#### 3.2.10. `parse_remove()` → `RemoveStmt`
```
REMOVE IDENT FROM IDENT
```

#### 3.2.11. Выражения — цепочка методов с приоритетами

```
parse_expression()        → parse_logical()
parse_logical()           → parse_comparison() ((AND|OR) parse_comparison())*
                            | NOT parse_logical()
parse_comparison()        → parse_additive() (CMP_OP parse_additive())*
parse_additive()          → parse_multiplicative() ((PLUS|MINUS) parse_multiplicative())*
parse_multiplicative()    → parse_unary() ((STAR|SLASH|PERCENT) parse_unary())*
parse_unary()             → MINUS parse_unary() | NOT parse_unary() | parse_postfix()
parse_postfix()           → parse_primary() postfix*
  postfix = DOT IDENT
           | LBRACKET expr RBRACKET
           | LPAREN args RPAREN
           | AS type_name
           | IS type_name
parse_primary()           → INT_LIT | FLOAT_LIT | STR_LIT | TRUE | FALSE | NULL
                            | IDENT | list_literal | map_literal
                            | LPAREN expr RPAREN | lambda
```

#### 3.2.12. `parse_list_literal()` → `ListLiteral`
```
LBRACKET [expr (COMMA expr)*] RBRACKET
```

#### 3.2.13. `parse_map_literal()` → `MapLiteral`
```
LBRACE [IDENT COLON expr (COMMA IDENT COLON expr)*] RBRACE
```

#### 3.2.14. `parse_lambda()` → `LambdaExpr`
```
DO PIPE [params] PIPE body END
```

### 3.3. Тесты парсера (`tests/test_parser.py`)

Написать тесты для:
- [ ] `x = 42` → `AssignStmt(target=Ident("x"), op="=", value=Literal(42))`
- [ ] `print("hello")` → `ExprStmt(FuncCall(Ident("print"), [Literal("hello")]))`
- [ ] `def foo(x) ... end` → `FuncDef(name="foo", params=["x"], ...)`
- [ ] `def show(v) when Number then print(v) end` → `FuncDef` с `WhenClause`
- [ ] `if x > 0 ... elsif x == 0 ... else ... end` → `IfStmt` с обоими ветвями
- [ ] `for i in range(5) ... end` → `ForStmt`
- [ ] `while x < 10 ... end` → `WhileStmt`
- [ ] `user.age = 30` → `AssignStmt` с `FieldAccess` в target
- [ ] `[1, 2, 3]` → `ListLiteral`
- [ ] `{name: "Lara", age: 30}` → `MapLiteral`
- [ ] `x as Number` → `AsExpr`
- [ ] `x is String` → `IsExpr`
- [ ] `do |x| x * 2 end` → `LambdaExpr`
- [ ] Тест на приоритет операций: `2 + 3 * 4` → `BinOp(+, 2, BinOp(*, 3, 4))`
- [ ] Тест на ошибку: незакрытый `def` → `SyntaxError`
- [ ] `morph dataset ... end` → `MorphStmt` с корректными state_decls и transforms
- [ ] `transform "clean" ... end` внутри morph → `TransformClause`
- [ ] `state rows: List` → `StateDecl`
- [ ] `skip if condition` внутри transform → skip_condition в TransformClause
- [ ] `shadow "text"` → `LLMDirective(kind="shadow")`
- [ ] `think "text"`, `reason "text"`, `explain "text"` → LLMDirective

**Критерий:** все тесты парсера зелёные.

---

## ЭТАП 4. Окружение и типы

### 4.1. Файл `src/environment.py`

```python
class Environment:
    def __init__(self, parent=None):
        self.bindings: dict[str, Any] = {}
        self.parent: Optional[Environment] = parent
    
    def get(self, name: str) -> Any:
        """Поиск имени в текущем и родительских окружениях."""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise LumenNameError(f"undefined variable '{name}'")
    
    def set(self, name: str, value: Any):
        """Обновить существующее или создать в текущем."""
        if name in self.bindings:
            self.bindings[name] = value
        elif self.parent and self.parent.has(name):
            self.parent.set(name, value)
        else:
            self.bindings[name] = value
    
    def define(self, name: str, value: Any):
        """Создать в текущем окружении (игнорируя родителя)."""
        self.bindings[name] = value
    
    def has(self, name: str) -> bool:
        if name in self.bindings:
            return True
        if self.parent:
            return self.parent.has(name)
        return False
```

### 4.2. Файл `src/types.py`

Создать Python-классы для представления значений LUMEN:

```python
class LumenFunction:
    def __init__(self, name, params, body, closure_env, when_clauses=None):
        self.name = name
        self.params = params
        self.body = body              # list[Statement]
        self.closure_env = closure_env
        self.when_clauses = when_clauses or []  # list[WhenClause]

class LumenContext:
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent

# Morph-объект
class LumenMorph:
    def __init__(self, name, state_decls, transforms, llm_directives, closure_env):
        self.name = name
        self.state = {}                    # живая структура (Map)
        self.transforms = transforms       # list[TransformClause]
        self.llm_directives = llm_directives
        self.history = []                  # лог выполненных шагов
        self.closure_env = closure_env
        self._init_state(state_decls)

    def _init_state(self, decls):
        for decl in decls:
            self.state[decl.name] = decl.default  # None если не указано

    def run(self, interpreter):
        for t in self.transforms:
            record = {"step": t.name, "status": "ok"}
            if t.skip_condition:
                if interpreter.eval_expr(t.skip_condition, self._make_env()):
                    record["status"] = "skipped"
                    self.history.append(record)
                    continue
            try:
                interpreter.exec_stmts(t.body, self._make_env())
            except Exception as e:
                record["status"] = "error"
                record["message"] = str(e)
                self.history.append(record)
                raise
            self.history.append(record)
```

Нативные типы Python используются напрямую:
- `int` / `float` → `Number`
- `str` → `String`
- `bool` → `Boolean`
- `list` → `List`
- `dict` → `Map`
- `None` → `Null`
- `LumenFunction` → `Function`
- `LumenContext` → `Context`

Создать вспомогательную функцию:
```python
def lumen_type_name(value) -> str:
    if isinstance(value, bool):   return "Boolean"  # bool до int!
    if isinstance(value, (int, float)): return "Number"
    if isinstance(value, str):    return "String"
    if isinstance(value, list):   return "List"
    if isinstance(value, dict):   return "Map"
    if isinstance(value, LumenFunction): return "Function"
    if isinstance(value, LumenMorph):   return "Morph"
    if isinstance(value, LumenContext):  return "Context"
    if value is None:             return "Null"
    return "Unknown"
```

### 4.3. Файл `src/errors.py`

```python
class LumenError(Exception):
    def __init__(self, message, line=None, col=None, source_line=None):
        self.message = message
        self.line = line
        self.col = col
        self.source_line = source_line
    
    def __str__(self):
        s = f"[{self.__class__.__name__}] {self.message}"
        if self.line:
            s += f"\n  в строке {self.line}"
        if self.source_line:
            s += f"\n  > {self.source_line}"
        return s

class LumenSyntaxError(LumenError): pass
class LumenNameError(LumenError): pass
class LumenTypeError(LumenError): pass
class LumenTransformError(LumenError): pass
class LumenArithmeticError(LumenError): pass
class LumenIndexError(LumenError): pass
class LumenCallError(LumenError): pass
class LumenDispatchError(LumenError): pass
class LumenContextError(LumenError): pass
class LumenMorphError(LumenError): pass

# Внутренние сигналы (не ошибки)
class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception): pass

class ContinueSignal(Exception): pass
```

---

## ЭТАП 5. Трансформации типов

### 5.1. Файл `src/types.py` — добавить функцию трансформации

```python
def lumen_transform(value, target_type: str):
    """
    Явная трансформация: value as target_type.
    Возвращает преобразованное значение или поднимает LumenTransformError.
    """
    src = lumen_type_name(value)
    
    if src == target_type:
        return value
    
    # String → Number
    if src == "String" and target_type == "Number":
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            raise LumenTransformError(
                f'cannot transform String "{value}" to Number'
            )
    
    # Number → String
    if src == "Number" and target_type == "String":
        return str(int(value)) if isinstance(value, float) and value == int(value) else str(value)
    
    # Boolean → Number
    if src == "Boolean" and target_type == "Number":
        return 1 if value else 0
    
    # Number → Boolean
    if src == "Number" and target_type == "Boolean":
        return value != 0
    
    # Null → Number
    if value is None and target_type == "Number":
        return 0
    
    # Null → Boolean
    if value is None and target_type == "Boolean":
        return False
    
    # Null → String
    if value is None and target_type == "String":
        return "null"
    
    # List → String
    if src == "List" and target_type == "String":
        return "[" + ", ".join(lumen_to_str(e) for e in value) + "]"
    
    # Map → String
    if src == "Map" and target_type == "String":
        parts = [f"{k}: {lumen_to_str(v)}" for k, v in value.items()]
        return "{" + ", ".join(parts) + "}"
    
    raise LumenTransformError(
        f"cannot transform {src} to {target_type}"
    )

def lumen_to_str(value) -> str:
    """Вспомогательная: преобразовать в строку для вывода."""
    if value is None: return "null"
    if isinstance(value, bool): return "true" if value else "false"
    return lumen_transform(value, "String")
```

### 5.2. Тесты трансформаций (`tests/test_transforms.py`)

- [ ] `"42" as Number` → `42`
- [ ] `"3.14" as Number` → `3.14`
- [ ] `"hello" as Number` → `LumenTransformError`
- [ ] `42 as String` → `"42"`
- [ ] `3.14 as String` → `"3.14"`
- [ ] `true as Number` → `1`
- [ ] `false as Number` → `0`
- [ ] `0 as Boolean` → `False`
- [ ] `42 as Boolean` → `True`
- [ ] `null as Number` → `0`
- [ ] `null as Boolean` → `False`
- [ ] `null as String` → `"null"`
- [ ] `[1,2,3] as String` → `"[1, 2, 3]"`
- [ ] `{name: "Lara"} as String` → `"{name: Lara}"`

**Критерий:** все тесты трансформаций зелёные.

---

## ЭТАП 6. Встроенные функции

### 6.1. Файл `src/builtins.py`

Создать словарь встроенных функций. Каждая — Python-callable.

```python
def make_builtins() -> dict:
    def lumen_print(*args):
        print(" ".join(lumen_to_str(a) for a in args))
        return None
    
    def lumen_len(v):
        if isinstance(v, (str, list, dict)):
            return len(v)
        raise LumenTypeError(f"len() requires String, List or Map, got {lumen_type_name(v)}")
    
    def lumen_type(v):
        return lumen_type_name(v)
    
    def lumen_str(v):
        return lumen_transform(v, "String")
    
    def lumen_num(v):
        return lumen_transform(v, "Number")
    
    def lumen_bool(v):
        return lumen_transform(v, "Boolean")
    
    def lumen_append(lst, v):
        if not isinstance(lst, list):
            raise LumenTypeError(f"append() requires List as first argument")
        return lst + [v]
    
    def lumen_keys(m):
        if not isinstance(m, dict):
            raise LumenTypeError(f"keys() requires Map")
        return list(m.keys())
    
    def lumen_values(m):
        if not isinstance(m, dict):
            raise LumenTypeError(f"values() requires Map")
        return list(m.values())
    
    def lumen_has(m, key):
        if not isinstance(m, dict):
            raise LumenTypeError(f"has() requires Map as first argument")
        return key in m
    
    def lumen_range(*args):
        if len(args) == 1:
            return list(range(int(args[0])))
        elif len(args) == 2:
            return list(range(int(args[0]), int(args[1])))
        raise LumenCallError("range() takes 1 or 2 arguments")
    
    def lumen_input(prompt=""):
        return input(prompt)
    
    def lumen_exit(code=0):
        import sys
        sys.exit(int(code))
    
    def lumen_map(lst, fn):
        if not isinstance(lst, list): raise LumenTypeError("map() requires List")
        return [fn(e) for e in lst]

    def lumen_filter(lst, fn):
        if not isinstance(lst, list): raise LumenTypeError("filter() requires List")
        return [e for e in lst if lumen_truthy(fn(e))]

    def lumen_sort(lst):
        if not isinstance(lst, list): raise LumenTypeError("sort() requires List")
        return sorted(lst)

    def lumen_split(s, sep):
        if not isinstance(s, str): raise LumenTypeError("split() requires String")
        return s.split(sep)

    def lumen_join(lst, sep):
        if not isinstance(lst, list): raise LumenTypeError("join() requires List")
        return sep.join(lumen_to_str(e) for e in lst)

    def lumen_replace(s, old, new):
        if not isinstance(s, str): raise LumenTypeError("replace() requires String")
        return s.replace(old, new)

    return {
        "print":   lumen_print,
        "println": lumen_print,
        "len":     lumen_len,
        "type":    lumen_type,
        "str":     lumen_str,
        "num":     lumen_num,
        "bool":    lumen_bool,
        "append":  lumen_append,
        "keys":    lumen_keys,
        "values":  lumen_values,
        "has":     lumen_has,
        "range":   lumen_range,
        "map":     lumen_map,
        "filter":  lumen_filter,
        "sort":    lumen_sort,
        "split":   lumen_split,
        "join":    lumen_join,
        "replace": lumen_replace,
        "input":   lumen_input,
        "exit":    lumen_exit,
    }
```

---

## ЭТАП 7. Интерпретатор

### 7.1. Файл `src/interpreter.py`

Создать класс `Interpreter`:

```python
class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_context = LumenContext("cli")
        self._load_builtins()
    
    def _load_builtins(self):
        for name, fn in make_builtins().items():
            self.global_env.define(name, fn)
    
    def run(self, program: Program):
        return self.exec_stmts(program.body, self.global_env)
    
    def exec_stmts(self, stmts, env) -> Any:
        result = None
        for stmt in stmts:
            result = self.exec_stmt(stmt, env)
        return result
    
    def exec_stmt(self, stmt, env) -> Any: ...
    def eval_expr(self, expr, env) -> Any: ...
```

### 7.2. Реализация `exec_stmt`

#### AssignStmt
- Вычислить `value` через `eval_expr`.
- Если `target` — простой `Ident`: `env.set(name, value)`.
- Если `target` — `FieldAccess(obj, field)`: получить объект, если `dict` → установить `obj[field] = value`.
- Составные операторы `+=/-=/*=/=`: получить текущее значение, применить операцию, сохранить.

#### FuncDef
- Создать `LumenFunction(name, params, body, env)`.
- **Особый случай:** если функция с таким именем уже существует в `env` и это `LumenFunction` с `when_clauses`, а новое определение тоже содержит `when_clauses` — **добавить** новые `when_clauses` к существующим (эволюция).
- Иначе: `env.define(name, function)`.

#### IfStmt
- `eval_expr(condition)` → `lumen_truthy(value)`.
- Если true → `exec_stmts(then_body)`.
- Иначе проверить `elsif_clauses` по порядку.
- Если ни одно не подошло → `exec_stmts(else_body)`.

#### WhileStmt
- Цикл: пока `lumen_truthy(eval_expr(condition))` → `exec_stmts(body)`.
- Перехватывать `BreakSignal` — выход из цикла.
- Перехватывать `ContinueSignal` — переход к следующей итерации.
- Перехватывать `ReturnSignal` — пробрасывать выше.

#### ForStmt
- Вычислить `iterable = eval_expr(iterable_expr)`.
- Если не `list` — `TypeError`.
- Для каждого элемента: создать дочернее окружение, установить `var = element`, выполнить тело.
- Перехватывать `BreakSignal` — выход из цикла.
- Перехватывать `ContinueSignal` — переход к следующему элементу.

#### ContextStmt
- Сохранить текущий контекст.
- Создать новый `LumenContext(name, parent=current)`.
- Установить как текущий.
- Выполнить тело.
- Восстановить предыдущий контекст.

#### ReturnStmt
- `raise ReturnSignal(eval_expr(value) if value else None)`

#### RemoveStmt
- Получить объект по имени из `env`.
- Если не `dict` → `TypeError`.
- `del obj[field]` (если ключа нет — молча игнорировать).

#### ExprStmt
- `eval_expr(expr, env)`.

### 7.3. Реализация `eval_expr`

#### Literal
- Вернуть `node.value` (Python-значение напрямую).

#### Ident
- `env.get(node.name)`.

#### BinOp
- Вычислить `left` и `right`.
- Применить оператор. Таблица операторов:
  - `+`: вызвать `lumen_add(left, right)` (см. ниже)
  - `-`, `*`, `/`, `%`: оба должны быть Number; `/` → float-деление; `/ 0` → `ArithmeticError`
  - `==`, `!=`: `lumen_equal(left, right)` и инверсия
  - `<`, `>`, `<=`, `>=`: оба Number или String; иначе `TypeError`
  - `and`, `or`: ленивые; возвращать последнее вычисленное значение (как в Python/JS)

#### `lumen_add(left, right)` — отдельная функция:
```python
def lumen_add(left, right):
    # List + anything → append
    if isinstance(left, list):
        return left + [right]
    # Map + Map → merge
    if isinstance(left, dict) and isinstance(right, dict):
        return {**left, **right}
    # String + anything → String
    if isinstance(left, str):
        return left + lumen_transform(right, "String")
    # Number + anything → Number
    if isinstance(left, (int, float)) and not isinstance(left, bool):
        r = lumen_transform(right, "Number")
        return left + r
    raise LumenTypeError(f"cannot add {lumen_type_name(left)} and {lumen_type_name(right)}")
```

#### UnaryOp
- `-`: значение должно быть Number; `-value`.
- `not`: `not lumen_truthy(value)`.

#### FieldAccess
- Вычислить `obj`.
- Если `dict` → `obj.get(field, None)`.
- Иначе `TypeError`.

#### IndexAccess
- Вычислить `obj` и `index`.
- Если `list` и `index` — Number → `obj[int(index)]` (IndexError если выход за пределы).
- Если `dict` и `index` — String → `obj.get(index, None)`.
- Иначе `TypeError`.

#### FuncCall
- Вычислить `callee`.
- Вычислить все аргументы.
- Если `callee` — Python callable (встроенная функция) → вызвать напрямую.
- Если `LumenFunction`:
  - Если есть `when_clauses` → диспетчеризация по типу первого аргумента:
    - Найти первую клаузу, где `lumen_type_name(args[0]) == clause.type_name`.
    - Если не найдено → `DispatchError`.
    - Создать дочернее окружение от `closure_env`.
    - Связать параметры с аргументами.
    - Выполнить тело клаузы, перехватить `ReturnSignal`.
  - Иначе: создать дочернее окружение, связать параметры, выполнить тело, перехватить `ReturnSignal`.
  - Несоответствие числа аргументов → `CallError`.

#### AsExpr
- `lumen_transform(eval_expr(value), type_name)`.

#### IsExpr
- `lumen_type_name(eval_expr(value)) == type_name`.

#### ListLiteral
- Вычислить все элементы, вернуть Python list.

#### MapLiteral
- Вычислить все значения, вернуть Python dict.

#### LambdaExpr
- Создать `LumenFunction(name=None, params, body, closure_env=env)`.

### 7.4. Вспомогательная функция `lumen_truthy`
```python
def lumen_truthy(value) -> bool:
    if value is None: return False
    if isinstance(value, bool): return value
    if isinstance(value, (int, float)): return value != 0
    if isinstance(value, str): return len(value) > 0
    if isinstance(value, list): return len(value) > 0
    if isinstance(value, dict): return len(value) > 0
    return True
```

### 7.5. Тесты интерпретатора (`tests/test_interpreter.py`)

Создать хелпер `run(code: str) -> stdout_output`:
```python
def run(code):
    import io, sys
    from src.lexer import Lexer
    from src.parser import Parser
    from src.interpreter import Interpreter
    
    tokens = Lexer(code).tokenize()
    ast = Parser(tokens).parse()
    
    captured = io.StringIO()
    sys.stdout = captured
    Interpreter().run(ast)
    sys.stdout = sys.__stdout__
    return captured.getvalue().strip()
```

Написать тесты:
- [ ] `print("hello")` → `"hello"`
- [ ] `x = 42\nprint(x)` → `"42"`
- [ ] `"42" + 1` (в print) → `"43"`
- [ ] `42 + "!"` → `"42!"`
- [ ] `if true\nprint("yes")\nend` → `"yes"`
- [ ] `if false\nprint("no")\nelse\nprint("yes")\nend` → `"yes"`
- [ ] `for i in range(3)\nprint(i)\nend` → `"0\n1\n2"`
- [ ] `n=0\nwhile n<3\nprint(n)\nn=n+1\nend` → `"0\n1\n2"`
- [ ] `def f(x)\nreturn x*2\nend\nprint(f(5))` → `"10"`
- [ ] Функция с `when`: show(10), show("hi"), show([1,2])
- [ ] Эволюция функции: определить с Number, потом добавить Boolean
- [ ] Живая карта: добавить поле, проверить, remove, проверить null
- [ ] Лямбда: `double = do |x| x*2 end\nprint(double(5))` → `"10"`
- [ ] `len([1,2,3])` → `"3"`
- [ ] `type(42)` → `"Number"`
- [ ] `42 is Number` → `true`
- [ ] `"hi" is String` → `true`
- [ ] `for i in range(5)\nif i==3\nbreak\nend\nprint(i)\nend` → `"0\n1\n2"`
- [ ] `for i in range(4)\nif i%2==0\ncontinue\nend\nprint(i)\nend` → `"1\n3"`
- [ ] `map([1,2,3], do |x| x*2 end)` → `[2, 4, 6]`
- [ ] `filter([1,2,3,4], do |x| x > 2 end)` → `[3, 4]`
- [ ] `split("a,b,c", ",")` → `["a", "b", "c"]`
- [ ] `join(["a","b","c"], "-")` → `"a-b-c"`

### 7.6. Тесты обработки ошибок (`tests/test_errors.py`)
- [ ] `"hello" as Number` → `LumenTransformError`
- [ ] `foo` (не определено) → `LumenNameError`
- [ ] `1 / 0` → `LumenArithmeticError`
- [ ] Вызов функции с неверным числом аргументов → `LumenCallError`
- [ ] `when`-dispatch без подходящей ветви → `LumenDispatchError`

**Критерий:** все тесты интерпретатора и ошибок зелёные.

---

## ЭТАП 7a. Morph-блок

### 7a.1. Файл `src/morph.py` — реализация morph-блока

Создать класс `LumenMorph` (см. описание в `src/types.py` выше).

### 7a.2. Расширение парсера для morph

Добавить в `src/parser.py` метод `parse_morph()`:
- `MORPH IDENT morph_body END`
- Внутри `morph_body`: `state_decl*`, `transform_clause*`, `llm_directive*`
- Каждый `transform_clause`: `TRANSFORM STR_LIT body END`, с опциональным `SKIP IF expr`
- `llm_directive`: `(SHADOW | THINK | REASON | EXPLAIN) STR_LIT`

### 7a.3. Расширение интерпретатора для morph

В `exec_stmt` добавить обработку `MorphStmt`:
- Создать `LumenMorph` объект с state, transforms, llm_directives.
- Связать с именем в окружении.
- При доступе к `.run()` — выполнить все transform-шаги.
- При доступе к `.history` — вернуть список записей.
- При доступе к `.state` — вернуть текущее состояние.
- При создании окружения для transform-шагов: связать имя `state` с Map-объектом состояния morph-блока через `env.define("state", self.state)`. Внутри transform-шагов `state.field` разрешается как обычный `FieldAccess` на этом Map.

### 7a.4. LLM-native конструкции

Добавить обработку `shadow`, `think`, `reason`, `explain`:
- Парсер распознаёт их как `LLMDirective`.
- Интерпретатор **игнорирует** их при выполнении.
- Они сохраняются в метаданных morph-объекта.

### 7a.5. Тесты morph-блока (`tests/test_morph.py`)

- [ ] Создание morph с state и transforms
- [ ] `state rows: List` инициализирует `state.rows = null`
- [ ] `state cleaned: Boolean = false` инициализирует `state.cleaned = false`
- [ ] `.run()` выполняет все transform-шаги последовательно
- [ ] `.history` содержит записи о выполненных шагах
- [ ] `skip if true` пропускает шаг (статус "skipped" в history)
- [ ] `skip if false` не пропускает шаг
- [ ] Ошибка в transform → `MorphError`, шаг записан как "error" в history
- [ ] `shadow`, `think`, `reason`, `explain` парсятся без ошибок
- [ ] `shadow`, `think`, `reason`, `explain` не влияют на выполнение
- [ ] morph-объект доступен как значение в окружении
- [ ] `.state` доступен после `.run()` с корректными значениями

**Критерий:** все тесты morph-блока зелёные.

---

## ЭТАП 8. CLI и REPL

Реализация этапа — `src/lumen/cli.py` и `src/lumen/repl.py`. Фрагменты ниже — черновик плана, не текущий исходник. Версия печатается как `lumen 0.0.4`.

### 8.1. Файл `tools/cli.py`

```python
import sys, argparse
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.errors import LumenError

def run_file(path: str):
    with open(path, encoding="utf-8") as f:
        source = f.read()
    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        Interpreter().run(ast)
    except LumenError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog="lumen")
    sub = parser.add_subparsers(dest="cmd")
    
    run_p = sub.add_parser("run", help="Выполнить файл")
    run_p.add_argument("file")
    
    sub.add_parser("repl", help="Интерактивный режим")
    sub.add_parser("version", help="Версия")
    
    args = parser.parse_args()
    
    if args.cmd == "run":
        run_file(args.file)
    elif args.cmd == "repl":
        from tools.repl import start_repl
        start_repl()
    elif args.cmd == "version":
        print("LUMEN 0.1.0")
    else:
        parser.print_help()
```

### 8.2. Файл `tools/repl.py`

```python
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.errors import LumenError

def start_repl():
    print("LUMEN 0.1.0 REPL")
    print("Введите 'exit' для выхода.\n")
    
    interp = Interpreter()
    
    while True:
        try:
            line = input("lumen> ")
        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            break
        
        if line.strip() in ("exit", "quit"):
            break
        if not line.strip():
            continue
        
        try:
            tokens = Lexer(line).tokenize()
            ast = Parser(tokens).parse()
            result = interp.run(ast)
            if result is not None:
                from src.types import lumen_to_str
                print("=>", lumen_to_str(result))
        except LumenError as e:
            print(e)
        except Exception as e:
            print(f"[InternalError] {e}")
```

**Требования к REPL:**
- Сохранять состояние между вводами (один `Interpreter` на сессию).
- Выводить результат выражений через `=>`.
- Не падать на ошибках — выводить сообщение и продолжать.

---

## ЭТАП 9. Golden-тесты

### 9.1. Структура golden-тестов

Создать файлы в `tests/golden/`:

**`hello.lumen`:**
```lumen
print("Hello, World!")
```
**`hello.expected`:**
```
Hello, World!
```

**`transforms.lumen`:**
```lumen
x = "42"
y = x + 1
print(y)
z = 42 + "!"
print(z)
```
**`transforms.expected`:**
```
43
42!
```

**`evolution.lumen`:**
```lumen
def show(v)
  when Number then print("number: ", v)
  when String then print("string: ", v)
  when List   then print("list of ", len(v), " items")
end

show(10)
show("hello")
show([1, 2, 3])
```
**`evolution.expected`:**
```
number: 10
string: hello
list of 3 items
```

**`living_map.lumen`:**
```lumen
user = {name: "Lara"}
user.age = 30
print(user.name)
print(user.age)
remove age from user
print(user.age)
```
**`living_map.expected`:**
```
Lara
30
null
```

**`morph_basic.lumen`:**
```lumen
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
```
**`morph_basic.expected`:**
```
2
2
```

**`morph_skip.lumen`:**
```lumen
morph pipeline
  state ready: Boolean = false

  transform "check"
    state.ready = true
  end

  transform "process"
    skip if state.ready == false
    print("processing")
  end
end

pipeline.run()
```
**`morph_skip.expected`:**
```
processing
```

### 9.2. Раннер golden-тестов (добавить в `tests/test_interpreter.py`)

```python
import os, subprocess

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden")

def test_golden():
    for fname in os.listdir(GOLDEN_DIR):
        if not fname.endswith(".lumen"):
            continue
        base = fname[:-6]
        expected_file = os.path.join(GOLDEN_DIR, base + ".expected")
        lumen_file = os.path.join(GOLDEN_DIR, fname)
        
        if not os.path.exists(expected_file):
            continue
        
        result = subprocess.run(
            ["python", "lumen.py", "run", lumen_file],
            capture_output=True, text=True
        )
        expected = open(expected_file).read().strip()
        assert result.stdout.strip() == expected, \
            f"Golden test '{base}' failed:\n  expected: {expected!r}\n  got: {result.stdout.strip()!r}"
```

---

## ЭТАП 10. Примеры

Создать в `examples/` следующие файлы (все должны выполняться без ошибок):

**`examples/hello.lumen`** — Hello, World  
**`examples/transforms.lumen`** — демонстрация трансформаций типов  
**`examples/evolution.lumen`** — демонстрация эволюции функций  
**`examples/living_map.lumen`** — демонстрация живых структур  
**`examples/fibonacci.lumen`** — числа Фибоначчи (через цикл)  
**`examples/fizzbuzz.lumen`** — FizzBuzz  
**`examples/context_demo.lumen`** — демонстрация контекстов  
**`examples/morph_pipeline.lumen`** — демонстрация morph-блока (data pipeline)  
**`examples/morph_agent.lumen`** — демонстрация morph-блока (агент)  
**`examples/llm_native.lumen`** — демонстрация shadow/think/reason/explain  

---

## ЭТАП 11. Финальная проверка и аудит

### 11.1. Чеклист прототипа

Сверено 18.10.2026. Версия пакета — `0.0.4`, не `0.1.0`.

- [x] `python lumen.py version` выводит `lumen 0.0.4`
- [x] `python lumen.py run examples/hello.lumen` выводит `Hello, World!`
- [x] `python lumen.py repl` запускается и хранит состояние между вводами
- [x] `pytest tests/` — зелёный набор (лексер, парсер, интерпретатор, morph, диссонанс, require, golden)
- [ ] Покрытие: `pytest --cov=src tests/` ≥ 70% (порог не замерялся)
- [x] Golden-тесты проходят
- [x] Файлы в `examples/` запускаются
- [ ] Linux в этой среде не проверялся
- [x] Windows: пути и запуск проверены; консоль может искажать кириллицу в сообщениях об ошибках
- [x] `README.md` содержит запуск и статус прототипа
- [x] Morph-блок с transform-шагами работает
- [x] `.run()` и `.history` работают
- [x] `skip if` условно пропускает шаг
- [x] `shadow`, `think`, `reason`, `explain` парсятся и не исполняются
- [x] Примеры `morph_pipeline.lumen` и `morph_agent.lumen` выполняются

### 11.2. Что намеренно не входит в прототип
(не считается ошибкой, фиксируется в `ROADMAP.md`)

Уже добавлено сверх исходного ядра: вложенные morph (§3.6a.7), `require` (§3.6a.3), `~=` (§7.7), диссонанс (§7.6).

Ещё не входит:
- `import` / модули
- Исключения (`try/catch`)
- Многопоточность
- JIT
- Оптимизатор
- Пакетный менеджер
- Контексты `web`, `gui`
- Числа с основанием (hex, oct, bin)
- Интерполяция строк
- Автогенерация `llms.txt`
- Распределённые процессы и кластеры
- Кольцевая история и значение сущности на шаге
- `self`
- `become`, `grow`, `extend` (зарезервированы)

---

## Порядок выполнения этапов (рекомендуемый)

```
ЭТАП 0  → ЭТАП 1 → ЭТАП 2 → ЭТАП 3
                                 ↓
ЭТАП 4 ← ЭТАП 5 ← ЭТАП 6 ← ЭТАП 7
    ↓
ЭТАП 7a (morph) → ЭТАП 8 → ЭТАП 9 → ЭТАП 10 → ЭТАП 11
```

Каждый этап заканчивается зелёными тестами для своего модуля. Не переходить к следующему этапу, пока предыдущий не стабилен.

---

---

## ЭТАП 12. Открытые вопросы и задачи из notes

### 12.1. Открытые архитектурные вопросы

#### OQ-1. Композиция morph-блоков — РЕШЕНО 18.10.2026
**Приоритет:** Высокий (после v0.1)  
**Решение:** Вложенность разрешена. Состояние: сначала родитель, затем ребёнок (совпавшее имя поля задаётся объявлением ребёнка). История сливается в том же порядке. Чужой morph вызывается как подпрограмма и не обязан менять состояние вызывающего: контекст может быть другим.  
**Остаток:** когда контекст вызова общий. Спецификация: `docs/lumen_spec.md` §3.6a.7.

**Нанотаски:**
- [x] Принять решение и зафиксировать в спецификации
- [x] Вложенное объявление: `examples/morph_nested.lumen`. Вызов чужого morph как подпрограммы покрыт тестом и не меняет состояние вызывающего
- [ ] Решить, при каком условии вызванный morph делит контекст с вызывающим

#### OQ-2. Стоимость истории трансформаций — РЕШЕНО 18.10.2026
**Приоритет:** Средний (после v0.1)  
**Решение:** Кольцевой буфер настраиваемого размера. Теоретически история не обязана быть конечной; практически её ограничивают ресурсы машины. Нужны режимы хранения, очистка и другие служебные операции. Имена операций — при реализации. Полная интроспекция (значение на шаге) — целевая, не контракт v0.1. Спецификация: §3.6a.8, §7.9.

**Нанотаски:**
- [x] Выбрать стратегию хранения (кольцо, не ленивое отключение по умолчанию)
- [ ] Назвать режимы хранения и операции очистки
- [ ] Задать, чем настраивается размер кольца

#### OQ-3. LLM-контролируемость — ОТЛОЖЕНО 18.10.2026
**Приоритет:** не в текущей очереди  
**Решение:** LLM-специфика отложена. Подозрение автора: LUMEN и LLM могут оказаться чуждыми друг другу. Правила именования шагов ради моделей не вводить, пока этот вопрос не открыт заново.

**Нанотаски:**
- [ ] Вернуться к теме только по отдельному решению автора

#### OQ-4. Диссонанс vs TransformError — РЕШЕНО 18.10.2026
**Приоритет:** Средний (после v0.1)  
**Решение:** Три режима. Синтаксис — блок `dissonance strict|soft|creative ... end`. По умолчанию strict. Спецификация: §7.6.

**Нанотаски:**
- [x] Принять три режима
- [x] Синтаксис блока `dissonance`
- [x] Реализовать soft и creative для явного `as`

#### OQ-5. Равенство как путь (path equivalence) — РЕШЕНО 18.10.2026
**Приоритет:** после v0.1  
**Решение:** `==` остаётся сравнением значений. Оператор `~=` реализован как точное совпадение историй двух morph (`step`, `status`, `message`). Похожесть и вероятность похожести — позже, классификатор не выбран. Спецификация: §3.3.2, §7.7.

**Нанотаски:**
- [x] Выбрать оператор, а не метод `.reachable`
- [x] Точное совпадение историй: `examples/path_eq.lumen`
- [ ] Алгоритм похожести не выбирать, пока нет отдельного решения

### 12.2. Задачи по расширению языка (v0.2+)

#### T-1. Ключевое слово `extend`
**Приоритет:** Высокий (v0.2)  
Альтернатива повторному `def` для добавления when-ветвей. Более явная семантика: `extend show when Boolean then ...`.

**Нанотаски:**
- [ ] Определить синтаксис `extend`
- [ ] Определить, заменяет ли `extend` текущий механизм или дополняет
- [ ] Обновить грамматику и парсер
- [ ] Написать тесты

#### T-2. Ключевое слово `require` — РЕАЛИЗОВАНО
**Приоритет:** Высокий (v0.2)  
Предусловие внутри transform-шага. Аналог `skip if`, но с ошибкой при несоответствии:
```
transform "lock"
  require state.status == "closed"
  state.status = "locked"
end
```
Семантика: все `require` шага проверяются до тела, в порядке текста. Ложное условие — `MorphError`, статус `error`, тело не выполняется. `skip if` проверяется раньше и отменяет `require`.

**Нанотаски:**
- [x] Определить семантику: ложное условие → `MorphError`, тело шага не выполняется
- [x] Токен REQUIRE уже был в лексере; слово больше не в списке зарезервированных
- [x] Парсер принимает `require` рядом с `skip if`
- [x] Тесты: `tests/test_require.py`

#### T-3. Ключевое слово `grow`
**Приоритет:** Средний (после v0.1)  
Рабочая гипотеза от 18.10.2026, может измениться при реализации: `grow` наращивает поток состояний. Форма: `grow x with 5`, `grow x with "a"`. Таблица «число → сложение, строка → конкатенация» — черновик, не норма. Спецификация: §7.8.

**Нанотаски:**
- [ ] Уточнить, что именно добавляется в поток для каждого типа
- [ ] Решить: `grow` — оператор уровня statement или expression?
- [ ] Добавить в грамматику после уточнения семантики

#### T-4. Встроенная функция `trace`
**Приоритет:** Средний (v0.2)  
Трассировка потока: `trace(x)` выводит историю значений потока.

**Нанотаски:**
- [ ] Определить формат вывода trace
- [ ] Реализовать как встроенную функцию
- [ ] Интегрировать с morph-блоком: `trace(morph_obj)` выводит историю

#### T-5. Режимы типизации
**Приоритет:** Низкий (v0.3+)  
Три режима: soft (динамический, по умолчанию), strict (строгие проверки), creative (всё разрешено).

**Нанотаски:**
- [ ] Определить, как выбирается режим (pragma, CLI-флаг, контекст)
- [ ] Описать семантику каждого режима
- [ ] Связать с концепцией диссонанса (OQ-4)

#### T-6. Многострочные комментарии
**Приоритет:** Низкий (v0.2)  
Синтаксис: `=begin ... =end` (как в Ruby).

**Нанотаски:**
- [ ] Добавить в лексер распознавание `=begin`/`=end`
- [ ] Добавить тесты

#### T-7. Операции над историей: `undo`, `timeline`
**Приоритет:** Низкий (v0.3+)  
- `undo x` — откатить последнее изменение
- `timeline x` — получить полную историю изменений

**Нанотаски:**
- [ ] Определить семантику: undo только в morph-блоках или везде?
- [ ] Определить, как undo взаимодействует с history
- [ ] Написать примеры

### 12.3. Исследовательские задачи

#### R-1. Связь с HoTT
**Приоритет:** Фоновое исследование  
Исследовать, насколько Гомотопическая Теория Типов совместима с концепцией «тип — это траектория». Потенциально — математический фундамент LUMEN.

#### R-2. LUMEN-LN: строгий LLM-подъязык
**Приоритет:** Средний (v0.3+)  
Lumen-LN — подмножество LUMEN с жёстко фиксированным синтаксисом `flow/step/end`, оптимизированное для генерации/анализа LLM. Без вложенности, без неявных преобразований.

**Нанотаски:**
- [ ] Определить формальную грамматику LUMEN-LN
- [ ] Написать 5 примеров на LUMEN-LN
- [ ] Определить, транспилируется ли LUMEN-LN в полный LUMEN

#### R-3. Формальная публикация
**Приоритет:** Фоновое  
Оформить формальную математическую семантику LUMEN (потоки, типы-траектории, морфинг как морфизм, диссонанс) в виде статьи/препринта.

#### R-4. COBOL-inspired элементы для v0.2+
**Приоритет:** Низкий  
Оценить применимость в LUMEN:
- Condition names (`condition adult value 18..120`)
- Picture clauses для форматирования вывода
- `perform ... thru ...` для процедурных блоков
- Prose-like / noise words как опциональные синтаксические элементы

### 12.4. Задачи по документации и примерам

#### D-1. Killer-примеры
**Приоритет:** Высокий  
Написать 3–5 конкретных примеров, демонстрирующих уникальность morph-блока:
- [ ] Data cleaning + feature engineering pipeline
- [ ] LLM-агент (ReAct-style)
- [ ] Конечный автомат (state machine) — например, дверь или UI-роутер
- [ ] Live-coding сессия с постепенным обрастанием объекта
- [ ] Бизнес-процесс (заявка → рассмотрение → одобрение → исполнение)

#### D-2. README «LUMEN за 5 минут»
**Приоритет:** Высокий  
С killer-примерами как центральными.

#### D-3. Нишевое позиционирование
**Приоритет:** Средний  
Документ/раздел, явно описывающий целевую аудиторию: артисты, исследователи, моддеры, power users, data engineers, AI/ML practitioners.

#### D-4. Видео «LUMEN за 7 минут»
**Приоритет:** Средний (после прототипа)  
Демонстрация 3–5 примеров + голос за кадром: «почему это не пайплайн и не state machine в привычном смысле».

### 12.5. Пересмотренные решения

| Решение | Ранняя версия (notes) | Текущее решение (spec v0.0.1) | Статус |
|---|---|---|---|
| Синтаксис функций | `func name(params)` | `def name(params)` (Ruby-style) | **Пересмотрено** |
| Null-значение | `nil` | `null` | **Пересмотрено** |
| Цикл | `loop condition` | `while condition` + `for x in y` | **Пересмотрено** |
| Объявление переменных | `let x = 10` | `x = 10` (без `let`) | **Пересмотрено** |
| Синтаксис трансформации | `transform x -> x * 2` | `morph`-блок с `transform "name" ... end` | **Пересмотрено** |
| Синтаксис эволюции функций | `if Type` | `when Type then` | **Пересмотрено** |
| Метаморфность | Тотальная философия всего языка | Центральная абстракция (morph-блок), не всепоглощающая | **Пересмотрено** |
| Многострочные комментарии | `=begin`/`=end` | Не в v0.1 (только `#`) | **Отложено** |

---

*TODO создано на основе Технического Задания (lumen_tz.md) и Формализованной Спецификации (lumen_spec.md) языка LUMEN. Обновлено 12.04.2026: добавлены break/continue, расширенные builtins (map, filter, sort, split, join, replace), исправлены версии, сокращены избыточные reserved words. Версия документа 0.0.4 (18.10.2026).*
