# LUMEN — Справочник встроенных функций
**Версия документа:** 0.0.3
**Дата обновления:** 12.04.2026
**Источник истины:** `docs/lumen_spec.md` §3.8 (при расхождении приоритет у спецификации)
**Статус:** документ фазы проектирования — функции ещё не реализованы (см. ROADMAP.md, этап 1)

Все встроенные функции доступны из глобального окружения без импорта.

---

## Ввод/вывод

### `print(v...)`
Выводит значения через пробел, добавляет перевод строки.
```lumen
print("Hello,", "World!")   # → Hello, World!
```

### `println(v...)`
Алиас `print`.

### `input(prompt?) → String`
Читает строку из stdin. Необязательный аргумент — приглашение.
```lumen
name = input("Ваше имя: ")
```

---

## Информация о значениях

### `len(v) → Number`
Длина строки, списка или карты. Другие типы → `TypeError`.
```lumen
len("abc")        # → 3
len([1, 2, 3])    # → 3
len({a: 1})       # → 1
```

### `type(v) → String`
Имя типа значения: `"Number"`, `"String"`, `"Boolean"`, `"List"`, `"Map"`, `"Function"`, `"Morph"`, `"Null"`.
```lumen
type(42)     # → "Number"
type(null)   # → "Null"
```

---

## Трансформации (функциональная форма `as`)

### `str(v) → String`
Аналог `v as String`.

### `num(v) → Number`
Аналог `v as Number`. Нечисловая строка → `TransformError`.

### `bool(v) → Boolean`
Аналог `v as Boolean` (`0 → false`, иначе `true`; `null → false`).

---

## Списки

### `append(list, v) → List`
Возвращает **новый** список с добавленным элементом (исходный не изменяется).
```lumen
a = [1, 2]
b = append(a, 3)   # → [1, 2, 3]; a остаётся [1, 2]
```

### `range(n) → List`
`[0, 1, ..., n-1]`.

### `range(a, b) → List`
`[a, a+1, ..., b-1]`.

### `map(list, fn) → List`
Применяет функцию к каждому элементу.
```lumen
map([1, 2, 3], do |x| x * 2 end)   # → [2, 4, 6]
```

### `filter(list, fn) → List`
Оставляет элементы, для которых предикат истинен.
```lumen
filter([1, 2, 3, 4], do |x| x % 2 == 0 end)   # → [2, 4]
```

### `sort(list) → List`
Сортирует список чисел или строк. Смешанные типы → `TypeError`.

---

## Карты (Map)

### `keys(map) → List`
Список ключей карты (в порядке вставки).

### `values(map) → List`
Список значений карты.

### `has(map, key) → Boolean`
Проверка наличия ключа.
```lumen
user = {name: "Lara"}
has(user, "name")   # → true
has(user, "age")    # → false
```

---

## Строки

### `split(str, sep) → List`
Разделяет строку по разделителю.
```lumen
split("a,b,c", ",")   # → ["a", "b", "c"]
```

### `join(list, sep) → String`
Объединяет список в строку через разделитель.
```lumen
join(["a", "b", "c"], "-")   # → "a-b-c"
```

### `replace(str, old, new) → String`
Заменяет все вхождения подстроки.
```lumen
replace("hello", "l", "L")   # → "heLLo"
```

---

## Управление программой

### `exit(code?)`
Завершает программу. Код завершения по умолчанию — `0`.

---

## Сводная таблица

| Функция | Сигнатура | Категория |
|---|---|---|
| `print` | `print(v...)` | Ввод/вывод |
| `println` | `println(v...)` | Ввод/вывод |
| `input` | `input(prompt?) → String` | Ввод/вывод |
| `len` | `len(v) → Number` | Информация |
| `type` | `type(v) → String` | Информация |
| `str` | `str(v) → String` | Трансформация |
| `num` | `num(v) → Number` | Трансформация |
| `bool` | `bool(v) → Boolean` | Трансформация |
| `append` | `append(list, v) → List` | Списки |
| `range` | `range(n)` / `range(a, b) → List` | Списки |
| `map` | `map(list, fn) → List` | Списки |
| `filter` | `filter(list, fn) → List` | Списки |
| `sort` | `sort(list) → List` | Списки |
| `keys` | `keys(map) → List` | Карты |
| `values` | `values(map) → List` | Карты |
| `has` | `has(map, key) → Boolean` | Карты |
| `split` | `split(str, sep) → List` | Строки |
| `join` | `join(list, sep) → String` | Строки |
| `replace` | `replace(str, old, new) → String` | Строки |
| `exit` | `exit(code?)` | Программа |
