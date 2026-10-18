# Архитектура проекта LUMEN
**Версия:** 0.0.4  
**Дата обновления:** 18.10.2026

---

## 1. Общий обзор

Проект состоит из нескольких уровней:

- **Документы**: парадигма, манифест, спецификация ядра, техническое задание.
- **Ядро реализации**: лексер, парсер, AST, интерпретатор, morph-блок, LLM-native.
- **Инструменты**: CLI (`lumen run/repl/version`), REPL.
- **Инфраструктура**: тесты (pytest), golden-тесты, примеры (.lumen).
- **Перспектива**: транспилятор в C, рантайм на C, форматтер, линтер.

---

## 2. Структура репозитория

Рабочий код — пакет `src/lumen/`. Отдельных каталогов `src/*.py` и `tools/` нет: CLI и REPL лежат в пакете. Контекст исполнения живёт в `types.py` и `interpreter.py`. Директивы `shadow`, `think`, `reason`, `explain` разбирает парсер и хранит morph; отдельного модуля `llm_native.py` нет.

```text
lumen/
├── src/lumen/
│   ├── __init__.py          # версия пакета 0.0.4
│   ├── tokens.py            # TokenType, ключевые слова
│   ├── lexer.py
│   ├── ast_nodes.py
│   ├── parser.py
│   ├── environment.py
│   ├── types.py             # значения, сложение, `as`, `~=` по историям
│   ├── errors.py
│   ├── builtins.py
│   ├── morph.py             # state, шаги, вложенность, require, history
│   ├── interpreter.py       # исполнение, диссонанс, контекст
│   ├── repl.py
│   └── cli.py               # run / repl / version
│
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_interpreter.py
│   ├── test_transforms.py
│   ├── test_errors.py
│   ├── test_morph.py
│   ├── test_dissonance.py
│   ├── test_require.py
│   ├── test_smoke.py
│   └── golden/              # пары .lumen + .expected
│
├── examples/                # hello, transforms, evolution, living_map,
│                            # control_flow, functions, contexts, fibonacci,
│                            # fizzbuzz, morph_pipeline, morph_agent,
│                            # morph_nested, path_eq, dissonance, require,
│                            # llm_native
│
├── docs/
├── research/                # исторические заметки, не источник требований
├── lumen.py                 # python lumen.py run/repl/version
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── ROADMAP.md
└── CHANGELOG.md
```

---

## 3. Компоненты ядра

### 3.1. Лексер (`src/lumen/lexer.py`, `src/lumen/tokens.py`)

Преобразует исходный текст в поток токенов.  
Поддерживает литералы, ключевые слова (`morph`, `transform`, `state`, `skip`, `require`, `dissonance`, `break`, `continue`), оператор `~=`, LLM-директивы. `become`, `grow` и `extend` зарезервированы.

### 3.2. Парсер (`src/lumen/parser.py`)

Рекурсивный нисходящий парсер. Строит AST по потоку токенов.  
Грамматика соответствует EBNF из `docs/lumen_spec.md`.

### 3.3. AST (`src/lumen/ast_nodes.py`)

Датаклассы узлов: `Program`, `AssignStmt`, `FuncDef`, `IfStmt`, `WhileStmt`, `ForStmt`, `MorphStmt`, `TransformClause`, `RequireClause`, `StateDecl`, `DissonanceStmt`, `LLMDirective`, `BreakStmt`, `ContinueStmt` и выражения.

### 3.4. Интерпретатор (`src/lumen/interpreter.py`)

Обходит AST и выполняет программу. Управляет окружением, контекстом, диспетчеризацией функций и режимом диссонанса.

### 3.5. Morph-блок (`src/lumen/morph.py`)

Класс `LumenMorph`: `state` (Map), шаги, вложенные дети, `history` (список записей, пока без кольцевого буфера). `.run()` выполняет свои шаги, затем детей. `skip if` пропускает шаг. `require` при ложном условии пишет статус `error` и прерывает прогон.

### 3.6. LLM-директивы

`shadow`, `think`, `reason`, `explain` парсятся и не исполняются. Хранятся в метаданных morph-объекта. Отдельного модуля под них нет.

---

## 4. Инструменты

### 4.1. CLI (`src/lumen/cli.py`)

| Команда | Действие |
|---|---|
| `lumen run <file>` | Интерпретация .lumen файла |
| `lumen repl` | Интерактивный режим |
| `lumen version` | Печатает `lumen 0.0.4` |

Дальше по дорожной карте: `lumen compile`, `lumen fmt`.

### 4.2. REPL (`src/lumen/repl.py`)

Интерактивный режим с сохранением состояния между вводами. Печатает `=>`, когда результат выражения не `null`.

---

## 5. Тестовая инфраструктура

- **Юнит-тесты** (`tests/test_*.py`): лексер, парсер, интерпретатор, трансформации, ошибки, morph, диссонанс, `require`, CLI.
- **Golden-тесты** (`tests/golden/`): пары `.lumen` + `.expected`.
- **Фреймворк**: pytest.
- **Порог покрытия ≥ 70%** записан как цель и в этой среде не замерялся.

---

## 6. Этапы реализации

1. **Документация** — парадигма, манифест, спецификация, ТЗ. Готово.
2. **Прототип** — лексер, парсер, AST, интерпретатор. Готово, пакет `src/lumen/`.
3. **Morph-блок** — `state`, `transform`, `skip if`, `require`, `.run()`, `.history`, вложенность. Готово.
4. **LLM-директивы** — парсинг без исполнения. Готово. Развитие темы отложено.
5. **Тесты** — юнит-тесты и golden-тесты есть. Порог покрытия не замерен.
6. **CLI и REPL** — готовы.
7. **Примеры** — `examples/*.lumen` запускаются.
8. **Транспилятор в C** — впереди, см. `ROADMAP.md`.
