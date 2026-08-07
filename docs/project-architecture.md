# Архитектура проекта LUMEN
**Версия:** 0.0.3  
**Дата обновления:** 07.08.2026

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

```text
lumen/
├── src/
│   ├── __init__.py
│   ├── lexer.py            # токенизация исходного кода
│   ├── tokens.py            # перечисление TokenType, класс Token
│   ├── parser.py            # рекурсивный нисходящий парсер
│   ├── ast_nodes.py         # датаклассы узлов AST
│   ├── interpreter.py       # интерпретатор AST
│   ├── environment.py       # модель окружения (связный список)
│   ├── types.py             # типы, трансформации, lumen_truthy
│   ├── errors.py            # иерархия ошибок
│   ├── builtins.py          # встроенные функции
│   ├── context.py           # контекстная модель
│   ├── morph.py             # morph-блок: state, transforms, history, .run()
│   └── llm_native.py        # shadow, think, reason, explain — метаданные
│
├── tools/
│   ├── __init__.py
│   ├── cli.py               # точка входа CLI (lumen run/repl/version)
│   └── repl.py              # интерактивный режим
│
├── tests/
│   ├── __init__.py
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_interpreter.py
│   ├── test_transforms.py
│   ├── test_evolution.py
│   ├── test_errors.py
│   ├── test_morph.py
│   ├── test_llm_native.py
│   └── golden/              # golden-тесты (.lumen + .expected)
│
├── examples/                # рабочие примеры программ
│   ├── hello.lumen
│   ├── transforms.lumen
│   ├── evolution.lumen
│   ├── living_map.lumen
│   ├── fibonacci.lumen
│   ├── fizzbuzz.lumen
│   ├── morph_pipeline.lumen
│   └── morph_agent.lumen
│
├── docs/                    # проектная документация
│   ├── lumen_manifesto.md
│   ├── lumen_spec.md
│   ├── lumen_tz.md
│   ├── lumen_todo.md
│   ├── lumen_open_questions.md
│   ├── core-language-specification.md
│   ├── metamorphic-paradigm-research.md
│   └── project-architecture.md
│
├── versions/                # зафиксированные версии документов
│   └── v0.0.1/
│
├── research/                # исследовательские заметки
│   ├── main/
│   └── notes/
│
├── lumen.py                 # точка входа: python lumen.py run/repl/version
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── ROADMAP.md
└── LICENSE
```

---

## 3. Компоненты ядра

### 3.1. Лексер (`src/lexer.py`, `src/tokens.py`)

Преобразует исходный текст в поток токенов.  
Поддерживает: литералы, ключевые слова (включая `morph`, `transform`, `state`, `skip`, `break`, `continue`), операторы, LLM-директивы.

### 3.2. Парсер (`src/parser.py`)

Рекурсивный нисходящий парсер. Строит AST по потоку токенов.  
Грамматика соответствует EBNF из `docs/lumen_spec.md`.

### 3.3. AST (`src/ast_nodes.py`)

Датаклассы для каждого типа узла: `Program`, `AssignStmt`, `FuncDef`, `IfStmt`, `WhileStmt`, `ForStmt`, `MorphStmt`, `TransformClause`, `StateDecl`, `LLMDirective`, `BreakStmt`, `ContinueStmt`, и все выражения.

### 3.4. Интерпретатор (`src/interpreter.py`)

Обходит AST и выполняет программу. Управляет окружением, контекстом, диспетчеризацией функций, morph-блоками.

### 3.5. Morph-блок (`src/morph.py`)

Класс `LumenMorph`: объект с `state` (Map), `transforms` (список шагов), `history` (append-only лог), `llm_directives` (метаданные). Метод `.run()` выполняет шаги последовательно.

### 3.6. LLM-native (`src/llm_native.py`)

Обработка директив `shadow`, `think`, `reason`, `explain`. Парсятся, но не исполняются. Сохраняются в метаданных morph-объекта.

---

## 4. Инструменты

### 4.1. CLI (`tools/cli.py`)

| Команда | Действие |
|---|---|
| `lumen run <file>` | Интерпретация .lumen файла |
| `lumen repl` | Интерактивный режим |
| `lumen version` | Вывод версии |

Будущее (v0.2+): `lumen compile`, `lumen fmt`, `lumen test`.

### 4.2. REPL (`tools/repl.py`)

Интерактивный режим с сохранением состояния между вводами. Выводит результат выражений через `=>`.

---

## 5. Тестовая инфраструктура

- **Юнит-тесты** (`tests/test_*.py`): лексер, парсер, интерпретатор, трансформации, эволюция, ошибки, morph, LLM-native.
- **Golden-тесты** (`tests/golden/`): пары `.lumen` + `.expected` — проверка вывода программ.
- **Фреймворк**: pytest.
- **Критерий**: покрытие ≥ 70%.

---

## 6. Этапы реализации

1. **Документация** — парадигма, манифест, спецификация, ТЗ. *(завершено)*
2. **Прототип** — лексер, парсер, AST, интерпретатор (Python). *(в процессе)*
3. **Morph-блок** — парсинг, AST, интерпретация morph/transform/state/skip/history.
4. **LLM-native** — shadow, think, reason, explain — парсинг и хранение метаданных.
5. **Тесты** — юнит-тесты + golden-тесты.
6. **CLI и REPL** — точка входа, интерактивный режим.
7. **Примеры и документация** — .lumen файлы, «Быстрый старт».
8. **Транспилятор в C** — генерация C-кода + рантайм. *(перспектива)*
