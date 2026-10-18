# Формализованная спецификация языка программирования LUMEN
**Версия:** 0.0.4  
**Предыдущая версия:** 0.0.3  
**Статус:** спецификация ядра, сверена с прототипом 0.0.4  
**Дата фиксации:** 18.10.2026  
**Решения автора:** 18.10.2026 (§3.6a.7–§3.6a.10, §7.6–§7.9)  
**Применимость:** Прототип `src/lumen/` исполняет ядро и часть решений от 18.10.2026: вложенность morph (§3.6a.7), `~=` как точное совпадение историй (§7.7), диссонанс (§7.6), `require` (§3.6a.3). Кольцевой буфер (§3.6a.8), значение сущности на шаге и `self` (§3.6a.9) в код не входят.

---

## Часть I. Лексика

### 1.1. Кодировка
Исходный код LUMEN кодируется в UTF-8. Идентификаторы используют только символы ASCII (латиница, цифры, `_`). Строковые литералы могут содержать любые Unicode-символы.

### 1.2. Токены

#### 1.2.1. Ключевые слова (зарезервированы)
```
def      end      if       else     elsif
while    for      in       do       return
true     false    null     and      or
not      when     then     as       is
context  remove   from     dissonance
morph    transform state   skip     require  # morph-блок
shadow   think    reason   explain           # LLM-native
break    continue                            # управление циклами
become   grow     extend                     # зарезервированы
```

#### 1.2.2. Идентификаторы
**Грамматика:**
```
IDENT ::= (LETTER | '_') (LETTER | DIGIT | '_')*
LETTER ::= [a-zA-Z]
DIGIT  ::= [0-9]
```
**Примеры:** `x`, `user_name`, `_foo42`, `myVar`

#### 1.2.3. Числовые литералы
```
INT_LIT   ::= '-'? DIGIT+
FLOAT_LIT ::= '-'? DIGIT+ '.' DIGIT+
```
**Примеры:** `42`, `-7`, `3.14`, `-0.5`

#### 1.2.4. Строковые литералы
```
STR_LIT ::= '"' STR_CHAR* '"'
STR_CHAR ::= любой Unicode-символ кроме '"' и '\' 
           | ESCAPE_SEQ
ESCAPE_SEQ ::= '\\' | '\"' | '\n' | '\t' | '\r'
```

#### 1.2.5. Булевы литералы
```
BOOL_LIT ::= 'true' | 'false'
```

#### 1.2.6. Null
```
NULL_LIT ::= 'null'
```

#### 1.2.7. Операторы и разделители
```
= += -= *= /=
== != ~= < > <= >=
+ - * / %
. ,  : ( ) [ ] { }
```

#### 1.2.8. Комментарии
Однострочные, от `#` до конца строки. Лексер игнорирует комментарии.
```
COMMENT ::= '#' (любой символ кроме '\n')*
```

#### 1.2.9. Пробельные символы
Пробел, табуляция, `\r`, `\n` — разделители токенов. **Не** несут семантической нагрузки (никаких питон-отступов).

---

## Часть II. Синтаксис (грамматика)

Формат: расширенная форма Бэкуса-Наура (EBNF).  
`*` — ноль и более, `+` — одно и более, `?` — необязательно, `|` — альтернатива.

### 2.1. Программа
```ebnf
program     ::= statement* EOF
```

### 2.2. Операторы (statements)
```ebnf
statement   ::= assign_stmt
              | func_def
              | if_stmt
              | while_stmt
              | for_stmt
              | context_stmt
              | dissonance_stmt
              | morph_stmt
              | return_stmt
              | break_stmt
              | continue_stmt
              | remove_stmt
              | expr_stmt

assign_stmt ::= IDENT ('.' IDENT)* ('=' | '+=' | '-=' | '*=' | '/=') expression

expr_stmt   ::= expression
```

### 2.3. Объявление функции
```ebnf
func_def    ::= 'def' IDENT '(' param_list? ')' func_body 'end'

param_list  ::= IDENT (',' IDENT)*

func_body   ::= when_clause+
              | statement*

when_clause ::= 'when' type_name 'then' statement+
              | 'when' type_name 'do' statement* 'end'

type_name   ::= 'Number' | 'String' | 'Boolean' | 'List' | 'Map'
              | 'Function' | 'Null' | IDENT
```
*Примечание: `when`-клаузы обрабатывают первый аргумент функции. Функция с `when`-клаузами реализует эволюцию функций (multimethod dispatch).*
*Форма `when T then` используется для однострочных тел (одно или более выражений до следующего `when`, `else` или `end`). Форма `when T do ... end` используется для многострочных тел. Смешивание форм внутри одного `def` не рекомендуется.*

### 2.4. Условный оператор
```ebnf
if_stmt     ::= 'if' expression statement* elsif_clause* else_clause? 'end'

elsif_clause ::= 'elsif' expression statement*

else_clause ::= 'else' statement*
```

### 2.5. Цикл while
```ebnf
while_stmt  ::= 'while' expression statement* 'end'
```

### 2.6. Цикл for
```ebnf
for_stmt    ::= 'for' IDENT 'in' expression statement* 'end'
```

### 2.7. Оператор контекста
```ebnf
context_stmt ::= 'context' IDENT statement* 'end'
```

### 2.7a. Morph-блок
```ebnf
morph_stmt     ::= 'morph' IDENT morph_body 'end'

morph_body     ::= (state_decl | transform_clause | morph_stmt | llm_directive)*

state_decl     ::= 'state' IDENT ':' type_name ('=' expression)?

transform_clause ::= 'transform' STR_LIT transform_body 'end'

transform_body ::= (skip_clause | require_clause | llm_directive | statement)*

skip_clause    ::= 'skip' 'if' expression

require_clause ::= 'require' expression

llm_directive  ::= 'shadow' STR_LIT
                 | 'think' STR_LIT
                 | 'reason' STR_LIT
                 | 'explain' STR_LIT
```
*Примечание: `morph`-блок объявляет именованное состояние с цепочкой именованных трансформаций. Шаги выполняются последовательно при вызове `.run()`. Имя `state` — зарезервированный идентификатор внутри morph-блока, ссылающийся на живую структуру (Map) этого morph-объекта. Синтаксически `state.field` — обычный `FieldAccess` на `Ident("state")`; интерпретатор разрешает `state` в объект состояния текущего morph-блока. Вне morph-блоков `state` не имеет специального значения. `llm_directive` парсится, но не исполняется — сохраняется в метаданных.*

### 2.8. Оператор return
```ebnf
return_stmt ::= 'return' expression?
```

### 2.8a. Операторы break и continue
```ebnf
break_stmt    ::= 'break'
continue_stmt ::= 'continue'
```
- `break` — немедленный выход из ближайшего цикла (`while` или `for`).
- `continue` — переход к следующей итерации ближайшего цикла.
- Использование вне цикла → `SyntaxError`.

### 2.9. Оператор remove
```ebnf
remove_stmt ::= 'remove' IDENT 'from' IDENT
```

### 2.10. Выражения
```ebnf
expression  ::= logical_expr

logical_expr ::= comparison_expr (('and' | 'or') comparison_expr)*
               | 'not' logical_expr

comparison_expr ::= additive_expr (('==' | '!=' | '~=' | '<' | '>' | '<=' | '>=') additive_expr)*

additive_expr ::= multiplicative_expr (('+' | '-') multiplicative_expr)*

multiplicative_expr ::= unary_expr (('*' | '/' | '%') unary_expr)*

unary_expr  ::= '-' unary_expr
              | 'not' unary_expr
              | postfix_expr

postfix_expr ::= primary_expr postfix*

postfix     ::= '.' IDENT                          -- доступ к полю
              | '[' expression ']'                 -- индексация
              | '(' arg_list? ')'                  -- вызов функции
              | 'as' type_name                     -- трансформация типа
              | 'is' type_name                     -- проверка типа

primary_expr ::= INT_LIT
               | FLOAT_LIT
               | STR_LIT
               | BOOL_LIT
               | NULL_LIT
               | IDENT
               | list_literal
               | map_literal
               | '(' expression ')'
               | lambda_expr

list_literal ::= '[' (expression (',' expression)*)? ']'

map_literal  ::= '{' (map_entry (',' map_entry)*)? '}'
map_entry    ::= IDENT ':' expression

lambda_expr  ::= 'do' '|' param_list? '|' statement* 'end'

arg_list     ::= expression (',' expression)*
```

---

## Часть III. Семантика

### 3.1. Значения и типы

#### 3.1.1. Иерархия типов
```
Value
├── Number    (IEEE 754 double, внутреннее представление)
├── String    (последовательность Unicode code points)
├── Boolean   (true | false)
├── List      (динамический массив Value)
├── Map       (упорядоченный словарь String → Value)
├── Function  (замыкание: параметры + тело + окружение)
├── Morph     (объект morph-блока — state + transforms + history)
├── Context   (системный тип, недоступен пользователю напрямую)
└── Null      (единственное значение: null)
```

#### 3.1.2. Равенство
- `Number`: числовое равенство (`1.0 == 1` → `true`)
- `String`: посимвольное
- `Boolean`: значение
- `List`: поэлементное рекурсивное
- `Map`: по ключам и значениям (порядок не важен)
- `Null == Null` → `true`
- `Null == всё остальное` → `false`
- `Function == Function` → всегда `false` (функции уникальны)
- `Morph == Morph` → всегда `false` (morph-объекты уникальны)

### 3.2. Правила трансформации типов

**Два режима метаморфности (принятое решение, подтверждено 18.10.2026).** Режимы неявные: отдельного переключателя нет. LUMEN различает два режима работы с трансформациями:
- **Вне morph-блоков** (свободный режим): неявные трансформации через операторы разрешены (см. §3.2.2), включая случаи вроде `"" + 2`. Это обязательное свойство обычных конструкций языка, а не необязательное удобство.
- **Внутри morph-блоков** (строгий режим): метаморфность должна быть явной — трансформации состояния выполняются именованными `transform`-шагами и явным `as`; каждая записывается в history.

Это не противоречие, а спроектированное свойство языка (ранее — открытый вопрос, зафиксировано в `docs/lumen_open_questions.md` §4.1 и §6.4).

#### 3.2.1. Явная трансформация (`as`)

| Источник | Цель | Результат | Ошибка |
|---|---|---|---|
| `String` | `Number` | `parse(s)` | `TransformError` если не число |
| `Number` | `String` | `stringify(n)` | — |
| `Boolean` | `Number` | `true→1`, `false→0` | — |
| `Number` | `Boolean` | `0→false`, иначе `true` | — |
| `List` | `String` | `"[e1, e2, ...]"` | — |
| `Map` | `String` | `"{k: v, ...}"` | — |
| `Null` | `String` | `"null"` | — |
| `Null` | `Number` | `0` | — |
| `Null` | `Boolean` | `false` | — |
| любой | тот же | identity | — |
| любой | несовместимый | — | `TransformError` |

#### 3.2.2. Неявная трансформация через оператор `+`

Вне morph-блока `+` смотрит на левый операнд:

| Левый | Правый | Результат |
|---|---|---|
| `List` | любой | новый список с элементом в конце |
| `Map` | `Map` | слияние (правый перекрывает левый при конфликте ключей) |
| `Number` | приводится к `Number` | арифметическое сложение (`1 + true` → `2`) |
| `Number` | не приводится к `Number` | склейка строк (`100 + "!"` → `"100!"`) |
| `String`, которая разбирается как число | `Number` | арифметическое сложение (`"42" + 1` → `43`) |
| прочая `String` | любой | склейка строк (`"" + 2` → `"2"`, `"hi" + 1` → `"hi1"`) |

Внутри тела `transform` неявное приведение типов запрещено. Там `+` допускает только пару без смены типа: число+число, строка+строка, список+элемент, карта+карта. Иначе — `TypeError`. Явное `as` по-прежнему разрешено.

`-`, `*`, `/`, `%` требуют два `Number` и ничего не приводят.

### 3.3. Семантика операторов

#### 3.3.1. Арифметические (+, -, *, /, %)
- Оба операнда должны быть `Number` после применения правил неявной трансформации.
- `/` — вещественное деление.
- `%` — остаток от деления (знак совпадает со знаком делителя, как в Python).
- Деление на ноль → `ArithmeticError`.

#### 3.3.2. Сравнение (==, !=, ~=, <, >, <=, >=)
- `<`, `>`, `<=`, `>=` применимы только к `Number` и `String`. Иначе — `TypeError`.
- Сравнение `Boolean` значений через `<`, `>` не определено и вызывает `TypeError`.
- Возвращают `Boolean`.
- `==` и `!=` сравнивают значения (см. §3.1.2). Это не сравнение путей.
- `~=` сравнивает истории двух morph-объектов. Запись совпадает, если совпали `step`, `status` и `message`. Текущие значения `state` не участвуют. Оба операнда должны быть `Morph`, иначе `TypeError`. Похожесть путей сюда не входит.

#### 3.3.3. Логические (and, or, not)
- `and` / `or` — с ленивым вычислением (short-circuit).
- `not` — унарный, возвращает `Boolean`.
- Любое значение может быть проверено на истинность: `null`, `false`, `0`, `""`, `[]`, `{}` → falsy; остальное → truthy.

#### 3.3.4. Оператор `is`
```
expression is TypeName → Boolean
```
Возвращает `true` если значение принадлежит указанному типу.

#### 3.3.5. Оператор `as`
```
expression as TypeName → Value
```
Возвращает трансформированное значение или поднимает `TransformError`.
В блоке `dissonance soft` неудачный `as` оставляет исходное значение и пишет предупреждение. В `dissonance creative` вместо ошибки берётся запасное значение целевого типа (§7.6). Вне блока действует `strict`.

### 3.4. Область видимости и окружение

#### 3.4.1. Модель окружения
- Окружение — связный список таблиц имён: `Environment = {bindings: Map<String, Value>, parent: Environment | null}`.
- Поиск имени: сначала в текущем окружении, затем рекурсивно в родительском.
- Присваивание в уже существующее имя обновляет ближайший окружение, где оно найдено.
- Присваивание в новое имя — создаёт связь в **текущем** окружении.

#### 3.4.2. Глобальное окружение
- Создаётся при запуске интерпретатора.
- Содержит встроенные функции.

#### 3.4.3. Замыкания
- При определении функции захватывается ссылка на текущее окружение.
- Вызов функции создаёт новое окружение с родителем = окружение захвата.

### 3.5. Семантика функций

#### 3.5.1. Обычная функция
```
def имя(p1, p2, ...)
  тело
end
```
- При вызове: создаётся новое окружение; параметры связываются с аргументами.
- Несоответствие числа аргументов → `CallError`.
- `return expr` — немедленный выход с возвратом значения.
- Функция без явного `return` возвращает значение последнего вычисленного выражения.
- Это правило применяется и к обычным функциям, и к телам `when`-клауз. Если тело пусто — возвращается `null`.

#### 3.5.2. Функция с эволюцией (when-dispatch)
```
def имя(arg, ...)
  when TypeA then ...
  when TypeB then ...
end
```
- Dispatch по **типу первого аргумента**.
- Проверка ветвей: сверху вниз, первое совпадение.
- Нет совпадения → `DispatchError: no matching clause for type T in function 'имя'`.
- Ветви можно **добавлять** к уже определённой функции через повторный `def`:

```
def имя(arg)
  when TypeC then ...   # добавляет новую ветвь
end
```
При добавлении новая ветвь помещается **после** существующих. Ветви сортируются в порядке объявления.

#### 3.5.3. Лямбда-функции
```
do |p1, p2| выражение end
```
Анонимная функция, захватывает текущее окружение.

### 3.6. Семантика объектов (Map как живая структура)

- `Map` создаётся литералом `{k: v, ...}`.
- Доступ к полю: `obj.field` — возвращает `null` если поля нет.
- Присваивание поля: `obj.field = expr` — добавляет или обновляет поле.
- Удаление поля: `remove field from obj` — удаляет ключ; если ключа нет — ничего не происходит.
- `Map` — это **не класс**; нет встроенных методов, только данные. Если поле содержит `Function`, её можно вызвать: `obj.fn()` — это `FieldAccess` + `FuncCall`.
- Тип `Morph` — отдельный от `Map`. Morph-объекты имеют встроенные свойства `.run()`, `.history`, `.state`, которые не являются полями Map, а реализуются интерпретатором через специальную логику для типа `Morph`.

### 3.6a. Семантика Morph-блока

#### 3.6a.1. Объект Morph
- `morph имя ... end` создаёт объект типа `Morph` и связывает его с именем в текущем окружении.
- Объект Morph содержит:
  - `state` — живую структуру (Map), инициализированную `state_decl` объявлениями.
  - `transforms` — упорядоченный список именованных transform-шагов.
  - `history` — список записей о выполненных трансформациях (изначально пуст).

#### 3.6a.2. State-объявления
```
state rows: List
state cleaned: Boolean = false
```
- Каждое `state` объявление создаёт поле в `state`-объекте morph-блока.
- Тип указывается для документации; фактическая типизация — динамическая.
- Значение по умолчанию — `null`, если не указано иное.

#### 3.6a.3. Transform-шаги
```
transform "имя_шага"
  тело
end
```
- Каждый шаг имеет строковое имя.
- Тело шага — произвольные операторы, имеющие доступ к `state`.
- `skip if выражение` — если выражение истинно, шаг пропускается.
- `require выражение` — жёсткое предусловие шага. Если выражение ложно, тело шага не выполняется, в `history` пишется `{step, status: "error", message: "require failed in transform \"имя\""}`, выполнение `.run()` прерывается с `MorphError`. Несколько `require` проверяются по порядку текста; первое ложное останавливает шаг, остальные не вычисляются.
- `require` стоит только непосредственно в теле `transform`. Вложенный оператор и код вне morph — синтаксическая ошибка.

#### 3.6a.4. Метод `.run()`
- Вызов `morph_obj.run()` выполняет все transform-шаги последовательно, в порядке объявления.
- Перед каждым шагом проверяется `skip if` (если есть). Пропущенный шаг не вычисляет свои `require`.
- Если шаг не пропущен, проверяются его `require`. Ложное предусловие — ошибка шага, тело не выполняется.
- После каждого успешного шага в `history` добавляется запись: `{step: "имя", status: "ok"}`.
- При ошибке в шаге: `{step: "имя", status: "error", message: "..."}`. Выполнение прерывается (если не указано иное).

#### 3.6a.5. Свойство `.history`
- `morph_obj.history` — журнал выполненных шагов.
- Контракт прототипа v0.1: список записей (Map). Каждая запись содержит как минимум `step` (String) и `status` (String).
- Целевая семантика (после v0.1, решение 18.10.2026): интроспекция полная. Запись хранит значение сущности на этом шаге. Код может прочитать историю и ветвиться, если на шаге N сущность приняла конкретное значение. Такое ветвление считается разновидностью морфизма. Доступ по номеру шага, timestamp, имени и меткам проектируется позже (§7.1 в `docs/lumen_open_questions.md`).

#### 3.6a.6. LLM-директивы
- `shadow`, `think`, `reason`, `explain` — парсятся как директивы.
- Не влияют на исполнение программы. По решению от 18.10.2026 они приравниваются к документирующим комментариям.
- Вопрос, нужны ли LUMEN и языковые модели друг другу, отложен. Автогенерация `llms.txt` и правила «оптимизации под LLM» не являются требованием языка.

#### 3.6a.7. Вложенность и вызов (принято 18.10.2026)
- Morph-блок может быть объявлен в теле другого morph-блока, рядом с `state` и `transform`. Внутри `transform` вложенное объявление — синтаксическая ошибка.
- Имя вложенного morph связывается в том же окружении, что и имя родителя.
- Состояние общее. Сначала записываются поля родителя, затем объявления детей в порядке исходного текста. Поле ребёнка с тем же именем заменяет начальное значение.
- `parent.run()` выполняет шаги родителя, затем `run` каждого ребёнка. В `parent.history` записи идут в этом порядке. `child.history` содержит шаги самого ребёнка и его потомков, без шагов родителя.
- Отдельно объявленный morph, вызванный через `.run()` из чужого шага, работает со своим состоянием и свою историю в вызывающего не переносит. Когда такой вызов делит контекст с вызывающим, по-прежнему не решено.

#### 3.6a.8. Хранение истории (принят 18.10.2026, не входит в прототип v0.1)
- Семантически история может быть неограниченной.
- Хранимый журнал — кольцевой буфер. Размер настраивается. Фактический потолок — ресурсы машины, на которой выполняется программа.
- Язык предоставляет режимы хранения, очистку журнала и другие служебные операции над историей. Имена и синтаксис этих операций фиксируются при реализации.

#### 3.6a.9. Morph как расширение типа (принят 18.10.2026, не входит в прототип v0.1)
- Помимо машины состояний, morph-блок может добавлять поведение типу. Внутри такого блока `self` обозначает текущее значение.
- Как синтаксически отличить это употребление от morph с `state` — открытый остаток. Отказ от `self` этим остатком не подразумевается.

#### 3.6a.10. Чего в синтаксисе нет
- Опциональные слова-связки (noise words) в язык не входят. `add a to b giving c` не является формой `c = a + b`. Синтаксис остаётся лаконичным (решение 18.10.2026).

### 3.7. Контекстная модель

#### 3.7.1. Объект контекста
- Хранит имя контекста, доступные модули, правила адаптации.
- Встроенные функции могут запрашивать текущий контекст.

#### 3.7.2. Оператор context
```
context имя
  тело
end
```
- Создаёт дочерний контекст с именем `имя`.
- Тело выполняется в этом контексте.
- После выхода — восстанавливается родительский контекст.

#### 3.7.3. Контексты ядра
| Имя | Описание |
|---|---|
| `cli` | Вывод в stdout. По умолчанию. |
| `test` | Вывод перехватывается тестовым раннером. |

### 3.8. Встроенные функции

| Функция | Сигнатура | Описание |
|---|---|---|
| `print` | `print(v...)` | Вывод значений через пробел и перевод строки. Если аргумент уже граничит с пробелом, второй пробел не вставляется |
| `println` | `println(v...)` | Алиас `print` |
| `len` | `len(v) → Number` | Длина строки, списка или карты |
| `type` | `type(v) → String` | Имя типа значения |
| `str` | `str(v) → String` | Аналог `v as String` |
| `num` | `num(v) → Number` | Аналог `v as Number` |
| `bool` | `bool(v) → Boolean` | Аналог `v as Boolean` |
| `append` | `append(list, v) → List` | Возвращает новый список с добавленным элементом |
| `keys` | `keys(map) → List` | Список ключей карты |
| `values` | `values(map) → List` | Список значений карты |
| `has` | `has(map, key) → Boolean` | Проверка наличия ключа |
| `range` | `range(n) → List` | `[0, 1, ..., n-1]` |
| `range` | `range(a, b) → List` | `[a, a+1, ..., b-1]` |
| `map` | `map(list, fn) → List` | Применить функцию к каждому элементу |
| `filter` | `filter(list, fn) → List` | Отфильтровать элементы по предикату |
| `sort` | `sort(list) → List` | Отсортировать список (числа/строки) |
| `split` | `split(str, sep) → List` | Разделить строку по разделителю |
| `join` | `join(list, sep) → String` | Объединить список в строку через разделитель |
| `replace` | `replace(str, old, new) → String` | Заменить подстроку |
| `input` | `input(prompt?) → String` | Чтение строки из stdin |
| `exit` | `exit(code?)` | Завершение программы |

---

## Часть IV. Ошибки

### 4.1. Иерархия ошибок
```
LumenError
├── SyntaxError       -- ошибка разбора исходного текста
├── NameError         -- имя не найдено в области видимости
├── TypeError         -- операция неприменима к типу
├── TransformError    -- невозможна трансформация типа
├── ArithmeticError   -- деление на ноль и подобное
├── IndexError        -- выход за пределы списка
├── CallError         -- неверное число аргументов
├── DispatchError     -- нет совпадающей when-ветви
├── ContextError      -- операция недопустима в данном контексте
└── MorphError        -- ошибка в morph-блоке (неудачный transform-шаг)
```
*В пользовательских сообщениях об ошибках используются короткие имена (например, `[TransformError]`). В реализации на Python классы именуются с префиксом `Lumen` (например, `LumenTransformError`) для избежания конфликтов с встроенными исключениями Python.*

### 4.2. Формат сообщения об ошибке
```
[ErrorType] сообщение
  в строке N, колонке M
  > исходная строка кода
```

### 4.3. Примеры сообщений
```
[TransformError] cannot transform String "hello" to Number
  в строке 3, колонке 5
  > y = "hello" as Number

[DispatchError] no matching clause for type Boolean in function 'show'
  в строке 7, колонке 1
  > show(true)

[NameError] undefined variable 'foo'
  в строке 12, колонке 3
  > print(foo)
```

---

## Часть V. Грамматика полностью (сводная EBNF)

```ebnf
program          ::= statement* EOF

statement        ::= assign_stmt
                   | func_def
                   | if_stmt
                   | while_stmt
                   | for_stmt
                   | context_stmt
                   | dissonance_stmt
                   | morph_stmt
                   | return_stmt
                   | break_stmt
                   | continue_stmt
                   | remove_stmt
                   | expr_stmt

break_stmt       ::= 'break'
continue_stmt    ::= 'continue'

assign_stmt      ::= lvalue assign_op expression
lvalue           ::= IDENT ('.' IDENT)*
assign_op        ::= '=' | '+=' | '-=' | '*=' | '/='

func_def         ::= 'def' IDENT '(' param_list? ')' func_body 'end'
param_list       ::= IDENT (',' IDENT)*
func_body        ::= when_clause+ | statement*
when_clause      ::= 'when' type_name 'then' statement+
                   | 'when' type_name 'do' statement* 'end'
type_name        ::= 'Number' | 'String' | 'Boolean' | 'List'
                   | 'Map' | 'Function' | 'Null' | IDENT

if_stmt          ::= 'if' expression statement* elsif_clause* else_clause? 'end'
elsif_clause     ::= 'elsif' expression statement*
else_clause      ::= 'else' statement*

while_stmt       ::= 'while' expression statement* 'end'

for_stmt         ::= 'for' IDENT 'in' expression statement* 'end'

context_stmt     ::= 'context' IDENT statement* 'end'

# morph-блок
morph_stmt       ::= 'morph' IDENT morph_body 'end'
morph_body       ::= (state_decl | transform_clause | morph_stmt | llm_directive)*
state_decl       ::= 'state' IDENT ':' type_name ('=' expression)?
transform_clause ::= 'transform' STR_LIT transform_body 'end'
transform_body   ::= (skip_clause | require_clause | llm_directive | statement)*
skip_clause      ::= 'skip' 'if' expression
require_clause   ::= 'require' expression
llm_directive    ::= ('shadow' | 'think' | 'reason' | 'explain') STR_LIT

return_stmt      ::= 'return' expression?

remove_stmt      ::= 'remove' IDENT 'from' IDENT

expr_stmt        ::= expression

expression       ::= logical_expr

logical_expr     ::= comparison_expr (('and' | 'or') comparison_expr)*
                   | 'not' logical_expr

comparison_expr  ::= additive_expr (cmp_op additive_expr)*
cmp_op           ::= '==' | '!=' | '~=' | '<' | '>' | '<=' | '>='

additive_expr    ::= multiplicative_expr (('+' | '-') multiplicative_expr)*

multiplicative_expr ::= unary_expr (('*' | '/' | '%') unary_expr)*

unary_expr       ::= '-' unary_expr | 'not' unary_expr | postfix_expr

postfix_expr     ::= primary_expr postfix*
postfix          ::= '.' IDENT
                   | '[' expression ']'
                   | '(' arg_list? ')'
                   | 'as' type_name
                   | 'is' type_name

primary_expr     ::= INT_LIT | FLOAT_LIT | STR_LIT | BOOL_LIT | NULL_LIT
                   | IDENT | list_literal | map_literal
                   | '(' expression ')' | lambda_expr

list_literal     ::= '[' (expression (',' expression)*)? ']'
map_literal      ::= '{' (map_entry (',' map_entry)*)? '}'
map_entry        ::= IDENT ':' expression
lambda_expr      ::= 'do' '|' param_list? '|' statement* 'end'
arg_list         ::= expression (',' expression)*
```

---

## Часть VI. Примеры программ

### 6.1. Hello, World
```lumen
print("Hello, World!")
```

### 6.2. Трансформация типов
```lumen
x = "42"
y = x + 1
print(y)           # → 43

z = 100 + "!"
print(z)           # → "100!"

a = "3.14" as Number
print(a * 2)       # → 6.28
```

### 6.3. Эволюция функции
```lumen
def show(v)
  when Number then print("number: ", v)
  when String then print("string: ", v)
  when List   then print("list of ", len(v), " items")
end

show(10)          # → number: 10
show("hello")     # → string: hello
show([1, 2, 3])   # → list of 3 items
```

### 6.4. Расширение функции (добавление ветви)
```lumen
def show(v)
  when Number then print("number: ", v)
end

# Позже в том же файле или в другом модуле:
def show(v)
  when Boolean then print("bool: ", v)
end

show(42)     # → number: 42
show(true)   # → bool: true
```

### 6.5. Живая структура (Map)
```lumen
user = {name: "Lara"}
user.age = 30
user.tags = ["dev", "creator"]

print(user.name)    # → Lara
print(user.age)     # → 30
print(user.tags)    # → [dev, creator]

remove age from user
print(user.age)     # → null
```

### 6.6. Условия
```lumen
x = 42

if x > 100
  print("big")
elsif x > 10
  print("medium")
else
  print("small")
end
```

### 6.7. Циклы
```lumen
# for
for i in range(5)
  print(i)
end

# while
n = 0
while n < 3
  print(n)
  n = n + 1
end
```

### 6.8. Break и continue
```lumen
# break — выход из цикла
for i in range(10)
  if i == 5
    break
  end
  print(i)
end
# → 0 1 2 3 4

# continue — пропуск итерации
for i in range(6)
  if i % 2 == 0
    continue
  end
  print(i)
end
# → 1 3 5
```

### 6.9. Функции высшего порядка
```lumen
def apply(f, x)
  return f(x)
end

double = do |x| x * 2 end

print(apply(double, 5))    # → 10
```

### 6.10. Контекстная адаптация
```lumen
context cli
  print("Running in CLI mode")
end

context test
  print("Running in test mode")
end
```

### 6.11. Проверка типа
```lumen
def describe(v)
  if v is Number
    print("это число: ", v)
  end
  if v is String
    print("это строка: ", v)
  end
  if v is Null
    print("это null")
  end
end

describe(42)
describe("hello")
describe(null)
```

### 6.12. Morph-блок (data pipeline)
```lumen
morph dataset
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

dataset.run()
print(dataset.history)
```

### 6.13. Morph-блок (агент)
```lumen
morph agent
  state goal: String
  state memory: List

  shadow "LLM: treat this as ReAct loop"

  transform "observe"
    state.observation = sense()
  end

  transform "reason"
    reason "deciding action based on observation"
    state.action = decide(state.goal, state.observation)
  end

  transform "act"
    execute(state.action)
  end
end

agent.run()
```

### 6.14. LLM-native конструкции
```lumen
# Теневая документация
morph pipeline
  shadow "LLM: this is a data cleaning pipeline, suggest only row-preserving transforms"
  think "Current state: raw CSV with nulls"

  transform "ingest"
    explain "loading raw data from CSV source"
    state.data = load_csv("input.csv")
  end
end
```

---

## Часть VII. Формальная семантическая модель

### 7.1. Потоки как основа семантики

Формально каждое имя в LUMEN может рассматриваться как **поток** — функция времени в значения:

```
x: N → V
```

Состояние программы: `σ: X → (N → V)` — отображение имён в их полную историю значений.

Текущее значение: `curr(x, σ) = x(n)`, где `n` — последний индекс.

### 7.2. Присваивание как продолжение траектории

```
x = e  ⟹  x(n+1) = eval(e, σ)
```

В прагматичном режиме (v0.1) история не хранится для обычных переменных — только для `state` внутри `morph`-блоков.

### 7.3. Трансформации в формальной модели

```
transform "f":  x(n+1) = f(x(n))

Композиция:
transform "f" → transform "g":  x(n+2) = g(f(x(n)))
```

### 7.4. Тип как траектория

Тип — множество допустимых последовательностей:

```
T ⊆ V^N
x ∈ T  ⟺  history(x) ∈ T
```

Альтернативно, тип как граф: `T = (V_T, E_T)`, где `E_T ⊆ V_T × V_T` — допустимые переходы.

Корректность: `(x(n), x(n+1)) ∈ E_T`.

### 7.5. Морфинг как морфизм

```
become x as T₂:  f: T₁ → T₂,  x(n+1) = f(x(n)),  f(x(n)) ∈ V_{T₂}
```

Функция `f` должна сохранять допустимость траекторий.

### 7.6. Диссонанс

Диссонанс — переход вне допустимого множества:

```
D(x, n) = 1  если (x(n), x(n+1)) ∉ E_T
D(x, n) = 0  иначе
```

Режим выбирается блоком. По умолчанию действует `strict`. Имена `strict`, `soft` и `creative` — обычные идентификаторы, не ключевые слова.

```
dissonance strict
  тело
end
```

Допустимые режимы: `strict`, `soft`, `creative`. Вложенный блок перекрывает внешний и восстанавливает его при выходе. Сейчас диссонанс относится к явному `as`, который не попадает в таблицу §3.2.1. Неявный `+` и запрет приведения внутри `transform` этим блоком не меняются.

- **strict**: `D = 1` → `TransformError`
- **soft**: предупреждение в stderr и запись в журнал интерпретатора; результатом `as` остаётся исходное значение, выполнение продолжается
- **creative**: переход разрешён. Если обычной таблицы нет, запасное значение целевого типа такое: `Number` → `0`, `Boolean` → истинность исходного значения, `String` → его текст, `List` → список из одного элемента, `Map` → `{value: исходное}`. Неизвестное имя типа по-прежнему ошибка.

### 7.7. Равенство как путь

Оператор `==` сравнивает текущие значения и таким остаётся (решение 18.10.2026).

Оператор `~=` задуман как достижимость: путь трансформации от A к B существует.

```
a ~= b  ⟺  ∃f₁, ..., fₖ: fₖ(...f₁(a)) = b
```

Реализованная проверка у́же этой формулы: у двух morph-объектов истории совпадают точно (`step`, `status`, `message`). Точное совпадение достаточно для достижимости, обратное неверно. Похожесть путей и вероятность похожести не входят в эту проверку; способ их считать не выбран.

### 7.8. Grow (наращивание потока)

Рабочая гипотеза (18.10.2026), может измениться при реализации. Форма:

```
grow x with y
```

Примеры: `grow x with 5`, `grow x with "a"`. Смысл — наращивание потока состояний `x`, а не замена присваивания. Таблица операций по типам (число → сложение, строка → конкатенация, список → append) остаётся черновиком, не нормой. В прототип v0.1 `grow` не входит; слово зарезервировано.

### 7.9. История: модель и хранение

Каждая трансформация добавляет запись. В модели история потока может расти без заранее заданного конца.

Хранение (решение 18.10.2026, не контракт прототипа v0.1) — кольцевой буфер настраиваемого размера. Когда буфер полон, новая запись вытесняет самую старую из хранимых. Это ограничение носителя, а не запрет на длинную историю: потолок задают ресурсы машины. Явная очистка и режимы хранения могут отбросить или не записывать историю; пока такая операция не вызвана и буфер не переполнен, уже хранимые записи не переписываются.

### 7.10. Связь с реализацией

Формальная модель реализуется прагматично:
- Обычные переменные в прототипе v0.1: `value` (без истории).
- `state` в morph-блоке прототипа v0.1: текущее значение и журнал шагов с полями `step` и `status`.
- Целевая история morph — полная (значение на каждом шаге) и хранится кольцевым буфером; предусмотрены режимы хранения и служебные операции (§3.6a.8).

---

*Спецификация покрывает ядро языка LUMEN версии 0.0.4, включая morph-блоки, их вложенность, оператор `~=`, блок `dissonance`, `require` внутри `transform` и break/continue. Полная интроспекция, кольцевая история и `self` в прототип пока не входят. `become`, `grow` и `extend` зарезервированы. LLM-директивы парсятся и не исполняются; связь языка с языковыми моделями отложена.*
