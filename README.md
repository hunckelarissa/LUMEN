# LUMEN — Metamorphic Programming Language  
*A language that evolves with you.*

> **morph для LUMEN — то же, что async/await для JavaScript, ownership для Rust, монады для Haskell.**

> **Статус: прототип ядра 0.0.4.** Интерпретатор выполняет программы (`python lumen.py run examples/hello.lumen`, `python lumen.py version` печатает `lumen 0.0.4`). В коде есть morph (`state`, `transform`, `skip if`, `require`, `.run()`, `.history`), вложенные morph, оператор `~=` и блок `dissonance`. Кольцевая история, значение сущности на шаге, `self`, `grow`, `become`, `extend` и `import` ждут следующих решений. План: `ROADMAP.md`.

*English version: [README.en.md](README.en.md)*

---

## О языке

LUMEN — язык программирования общего назначения, основанный на **метаморфной парадигме**.  
Центральная идея: код — это **живая структура**, которая эволюционирует через состояния.

**Killer feature** — `morph`-блок: языковая конструкция (не библиотека), которая объявляет именованное состояние и цепочку его трансформаций с встроенной историей.

```
morph pipeline
  state rows: List
  state cleaned: Boolean = false

  transform "clean"
    state.rows = remove_nulls(state.rows)
    state.cleaned = true
  end

  transform "normalize"
    skip if state.cleaned == false
    state.rows = scale(state.rows, "zscore")
  end
end

pipeline.run()
print(pipeline.history)
```

Ни один существующий язык не предлагает эволюцию состояния как первоклассную языковую абстракцию.

---

## Основные идеи

### Morph-блоки — эволюция состояния
Именованные цепочки трансформаций с встроенной историей, `skip`-условиями и интроспекцией.

### Трансформация типов
Значения переходят между типами по формальным правилам: `"42" as Number`, `42 + "!" → "42!"`.

### Эволюция функций
Функции расширяют поведение через `when`-ветви без переопределения:
```
def show(v)
  when Number then print("число: ", v)
  when String then print("строка: ", v)
end
```

### Живые структуры
Объекты (Map) изменяют состав полей в любой момент: `user.age = 30`, `remove age from user`.

### Контекстная адаптация
Контекст исполнения (`cli`, `test`) влияет на интерпретацию операций.

### LLM-директивы
`shadow`, `think`, `reason`, `explain` парсятся и не исполняются: это документирующие комментарии. Вопрос, нужны ли языку модели, отложен.

---

## Как выглядит код

*(синтаксис прототипа; запуск: `python lumen.py run examples/<файл>.lumen`)*

```
# Переменные и трансформации
x = "42"
y = x + 1        # → 43 (String → Number, левый операнд определяет тип)
z = 100 + "!"    # → "100!" (Number → String)

# Функция с эволюцией
def describe(v)
  when Number then print("это число: ", v)
  when String then print("это строка: ", v)
  when List   then print("список из ", len(v), " элементов")
end

describe(42)
describe("hello")
describe([1, 2, 3])

# Morph-блок
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
print(counter.state.value)   # → 2
print(counter.history)       # → [{step: "increment", status: "ok"}, ...]
```

---

## Документация

| Документ | Файл | Для кого |
|---|---|---|
| Манифест языка | `docs/lumen_manifesto.md` | Философия и мотивация — источник истины по идеям |
| Формализованная спецификация | `docs/lumen_spec.md` | **Источник истины по языку** (EBNF, семантика, ошибки) |
| Техническое задание | `docs/lumen_tz.md` | Контрибьюторы: цели, требования, критерии приёмки |
| TODO разработки | `docs/lumen_todo.md` | Разработчики интерпретатора: план из 12 этапов |
| Справочник встроенных функций | `docs/lumen_builtins.md` | Пользователи языка |
| Справочник ошибок | `docs/lumen_errors.md` | Пользователи языка |
| Исследование парадигмы | `docs/metamorphic-paradigm-research.md` | Исследователи |
| Спецификация ядра (обзор) | `docs/core-language-specification.md` | Быстрое чтение (производный от spec) |
| Архитектура проекта | `docs/project-architecture.md` | Контрибьюторы |
| Открытые вопросы | `docs/lumen_open_questions.md` | Все: что ещё не решено |
| Журнал решений автора | `LUMEN_decisions_needed.md` | Решения от 18.10.2026 и то, что ещё без имени |
| План разработки | `ROADMAP.md` | Все: этапы и границы версий |
| История изменений | `CHANGELOG.md` | Все |

Папка `research/` содержит исторические материалы (заметки, обсуждения, результаты поиска) — контекст того, **почему** язык спроектирован именно так. Это не источник требований.

---

## Статус проекта

**Текущая версия пакета:** 0.0.4 (18.10.2026)  
**Код:** прототип интерпретатора в `src/lumen/`

```
python lumen.py run examples/hello.lumen
python lumen.py repl
python lumen.py version
pytest tests/
```

### Уже есть
- [x] Спецификация, ТЗ, манифест, исследование парадигмы
- [x] Интерпретатор: лексер, парсер, AST, окружение, типы, встроенные функции
- [x] Morph: `state`, `transform`, `skip if`, `require`, `.run()`, `.history`, вложенные morph
- [x] Оператор `~=` (точное совпадение историй) и блок `dissonance strict|soft|creative`
- [x] CLI `run` / `repl` / `version`, pytest и golden-тесты
- [x] Примеры в `examples/`: hello, transforms, evolution, living_map, control_flow, functions, contexts, fibonacci, fizzbuzz, morph_pipeline, morph_agent, morph_nested, path_eq, dissonance, require, llm_native

### Дальше
- [ ] Кольцевая история, полная интроспекция значения на шаге, `self`
- [ ] `grow`, `become`, `extend` — слова зарезервированы, синтаксис не закрыт
- [ ] Модули `import`, `trace`, форматтер, транспилятор в C
- [ ] Порог покрытия 70% не замерялся; Linux в этой среде не проверялся

---

## Целевые ниши

*(подробное обоснование — в `docs/lumen_manifesto.md` и `docs/lumen_tz.md`)*

| Ниша | Почему LUMEN |
|---|---|
| Data / ETL / ML pipelines | `morph`-блок — идеальная абстракция для clean → enrich → train |
| LLM-агенты | observe → reason → act = `morph`-блок с ReAct-паттерном |
| State machines / workflows | Бизнес-процессы, игры, IoT — конечные автоматы |
| Прототипирование DSL | Быстрое расширение без изменения ядра |
| Образование | Низкий порог входа, Ruby-подобный синтаксис |

---

## Стек разработки

- **Python 3.10+** — прототип интерпретатора (стандартная библиотека, без внешних зависимостей)
- **C** — транспилятор и рантайм (фаза 2)
- **pytest** — тесты
- **Ручной рекурсивный спуск** — парсер (без Lark/ANTLR на первом этапе)

---

## Как присоединиться

Мы ищем людей, которым интересно:
- проектировать синтаксис и семантику,
- писать интерпретаторы и компиляторы,
- создавать инструменты (CLI, REPL, форматтер),
- писать документацию и примеры,
- участвовать в формировании новой парадигмы.

Подробнее: `CONTRIBUTING.md`

---

## Об авторе

Проект создан Ларисой — программисткой с опытом создания интерпретаторов, транспиляторов и доработки компиляторов (Школьный Алгоритмический Язык, Euler, Mesa, Cedar, Euclid, форки GNU-компиляторов).

---

## Лицензия

MIT — см. `LICENSE`
