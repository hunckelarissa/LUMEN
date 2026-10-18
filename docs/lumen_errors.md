# LUMEN — Справочник сообщений об ошибках
**Версия документа:** 0.0.4
**Дата обновления:** 18.10.2026
**Источник истины:** `docs/lumen_spec.md` §IV (при расхождении приоритет у спецификации)
**Статус:** классы ошибок реализованы в `src/lumen/errors.py`

---

## Иерархия ошибок

```
LumenError
├── SyntaxError       — ошибка разбора исходного текста
├── NameError         — имя не найдено в области видимости
├── TypeError         — операция неприменима к типу
├── TransformError    — невозможна трансформация типа
├── ArithmeticError   — деление на ноль и подобное
├── IndexError        — выход за пределы списка
├── CallError         — неверное число аргументов
├── DispatchError     — нет совпадающей when-ветви
├── ContextError      — операция недопустима в данном контексте
└── MorphError        — ошибка в morph-блоке (неудачный transform-шаг)
```

В реализации на Python классы именуются с префиксом `Lumen` (например, `LumenTransformError`), в пользовательских сообщениях используются короткие имена.

---

## Формат сообщения

```
[ErrorType] сообщение
  в строке N, колонке M
  > исходная строка кода
```

---

## Ошибки по типам

### SyntaxError
Возникает на этапе разбора: незакрытая скобка, отсутствующий `end`, `break`/`continue` вне цикла.
```
[SyntaxError] expected 'end' to close 'if' block
  в строке 9, колонке 1
  > print("done")
```

### NameError
Обращение к неопределённому имени.
```
[NameError] undefined variable 'foo'
  в строке 12, колонке 3
  > print(foo)
```

### TypeError
Операция неприменима к типу: `<` для Boolean, `len` от Number, сортировка смешанного списка.
```
[TypeError] operator '<' is not defined for Boolean
  в строке 4, колонке 8
  > if true < false
```

### TransformError
Явная (`as`) или неявная (через операторы) трансформация невозможна.
```
[TransformError] cannot transform String "hello" to Number
  в строке 3, колонке 5
  > y = "hello" as Number
```

### ArithmeticError
Деление (или остаток) на ноль.
```
[ArithmeticError] division by zero
  в строке 7, колонке 9
  > z = x / 0
```

### IndexError
Индекс за пределами списка.
```
[IndexError] index 5 out of range for list of length 3
  в строке 2, колонке 7
  > v = xs[5]
```

### CallError
Число аргументов не совпадает с числом параметров функции.
```
[CallError] function 'add' expects 2 arguments, got 1
  в строке 10, колонке 1
  > add(1)
```

### DispatchError
Ни одна `when`-ветвь функции не совпала с типом первого аргумента.
```
[DispatchError] no matching clause for type Boolean in function 'show'
  в строке 7, колонке 1
  > show(true)
```

### ContextError
Операция недопустима в текущем контексте исполнения.
```
[ContextError] operation 'input' is not allowed in context 'test'
  в строке 5, колонке 3
  > name = input()
```

### MorphError
Ошибка внутри transform-шага morph-блока. Запись об ошибке также попадает в `history`: `{step: "имя", status: "error", message: "..."}`.
```
[MorphError] transform "clean" failed: [NameError] undefined variable 'remove_nulls'
  в строке 6, колонке 5
  > state.rows = remove_nulls(state.rows)
```

Невыполненное `require` — та же ошибка шага. Тело шага не выполняется, в `history` статус `error`:
```
[MorphError] require failed in transform "lock"
```
