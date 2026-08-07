📦 Список сущностей COBOL, которые стоит забрать

Я дам тебе отфильтрованный набор, который:

полезен людям

полезен LLM

не ломает Lumen

1. Разделение на секции (DIVISION-идея)

COBOL:

IDENTIFICATION DIVISION.
DATA DIVISION.
PROCEDURE DIVISION.
Что взять

👉 Явные логические блоки программы

В Lumen
define
    ...
end

flow
    ...
end

test
    ...
end
Почему это важно

LLM понимает контекст

человек быстрее ориентируется

2. Самоописывающие конструкции

COBOL:

ADD A TO B GIVING C
Что взять

👉 операции, читаемые как предложения

В Lumen
transform x with double
grow total with 10
become value as string

💡 Ты уже это сделал — это правильное направление

3. Явные данные (DATA DIVISION)

COBOL заставляет описывать данные заранее.

Что взять

👉 явное объявление структуры

В Lumen
define user
    name: string
    age: int
end
Почему это хорошо

LLM получает структуру

меньше ошибок

4. Именованные шаги

COBOL:

READ-FILE.
PROCESS-RECORD.
WRITE-OUTPUT.
Что взять

👉 именование этапов процесса

В Lumen
transform data with clean_data
transform data with normalize_data
transform data with export_results

или даже:

stage clean_data
stage normalize_data
stage export_results
5. Минимум символов — максимум слов

COBOL избегает:

{}, ->, =>
Что взять

👉 избегать перегруженных символов

В Lumen

❌ плохо:

x |> f |> g

✅ хорошо:

transform x with f
transform x with g
6. Однозначность операций

В COBOL почти нет перегрузки.

Что взять

👉 одна операция = одно значение

В Lumen
transform — всегда функция
grow — всегда накопление
become — всегда изменение типа
7. Линейный поток выполнения

COBOL — почти всегда top-down.

Что взять

👉 линейность

В Lumen
transform x with f
grow x with 5
become x as string
8. Отсутствие "магии"

COBOL почти не имеет скрытых эффектов.

Что взять

👉 никакой неявности

В Lumen

❌ плохо:

x + 5  # непонятно grow или transform?

✅ хорошо:

grow x with 5
9. Verb-based модель

COBOL = язык глаголов.

Это ЗОЛОТО

👉 вся грамматика через действия

В Lumen
transform
grow
become
define
check
trace

Это идеально:

для человека

для LLM

10. Самодокументируемость

COBOL код часто читается как текст.

Что взять

👉 код = документация

В Lumen
transform payment with validate_input
transform payment with apply_discount
transform payment with finalize
🔥 Что НЕ брать из COBOL

Важно.

❌ Чрезмерную многословность
MOVE ZERO TO TOTAL-AMOUNT

👉 слишком много шума

❌ Жёсткий формат колонок

(исторический артефакт)

❌ Слабую композицию

COBOL плохо масштабируется.

🧠 Итоговый набор для Lumen

Вот чистый список:

📌 Core элементы
1. Verb-based syntax
2. Явные операции
3. Линейный поток
4. Самоописывающий код
5. Минимум символов
6. Явные структуры данных
7. Именованные стадии
8. Отсутствие магии
9. Разделение на логические блоки
10. Избыточность (но контролируемая)
💡 Самое важное наблюдение

Ты сейчас приходишь к очень редкой комбинации:

COBOL (читаемость)
+
functional pipelines
+
trace semantics
+
LLM predictability
🚀 Очень сильная идея

Можно сформулировать философию языка так:

Lumen — это глагольный язык описания эволюции состояния.

⚖️ Итог

COBOL был «слишком человеческим» для программистов,
но именно это делает его:

идеально понятным для машин, обученных на тексте



=======================================================================


Теперь по твоему вопросу: какие сущности из COBOL можно забрать в LUMEN, чтобы сохранить/усилить человеческую читаемость, но при этом не сделать язык неприятным для нейронок.
Вот список из 8 самых перспективных идей (я отобрал только те, что хорошо ложатся на современный LLM-стиль и не создают сильного cognitive overhead).
№,Сущность из COBOL,Как выглядит в классическом COBOL,Как можно адаптировать в LUMEN (пример),Почему это полезно для человека,Почему это не отпугнёт нейронки (2026)
1,Prose-like / глагольные конструкции,"ADD YEARS TO AGE  
MOVE ""Hello"" TO GREETING","add years to age  
move ""Hello"" to greeting  
или age += years (оба варианта разрешены)",Читается почти как предложение на английском,LLM обожают естественный язык — это их родная среда
2,Noise words (опциональные слова-шум),"ADD A TO B GIVING C  
IS GREATER THAN","add a to b giving c  
add a and b into c  
a is greater than b (все три работают)",Делает код похожим на человеческий текст,Модели прекрасно справляются с синонимами и вариациями
3,Condition names (88-level),"88 PASS VALUE 'Y' 'YES'  
IF PASS ...","condition valid-age value 18..120  
if valid-age then ...","Логика читается как бизнес-правило, а не как IF-магия",Очень похоже на enum + if-let в Rust/TS — модели знают
4,Picture clauses (форматирование вывода),"PIC 999,999.99  
PIC X(20)","picture ""999,999.99""  
format ""currency:USD""  
или display price with picture ""999,999.99""",Автоматическое красивое форматирование без лишнего кода,LLM уже генерируют форматирование в Python f-strings и т.д.
5,Divisions / Sections / Paragraphs,"IDENTIFICATION DIVISION. 
PROCEDURE DIVISION.","section identification 
section procedures 
или просто paragraph main-logic",Чёткое разделение кода на логические блоки,Модели любят структурированный код (sections как comments)
6,PERFORM paragraph-name,PERFORM CALCULATE-TAX THRU END-TAX,"perform calculate-tax thru end-tax  
или do calculate-tax",Легко читаемые подпрограммы без лишних скобок,"Похоже на вызовы функций + goto, но в хорошем смысле"
7,Explicit scope terminators (END-IF и т.п.),IF condition ... END-IF,"if condition then ... end-if  
или if condition { ... } (оба варианта)",Нет путаницы с вложенностью (особенно в большом коде),Современные модели отлично понимают и { } и END-IF
8,GIVING / INTO / FROM (явные направления),"ADD A B GIVING C  
SUBTRACT DISCOUNT FROM COST","add a and b giving c  
subtract discount from cost",Направление операции видно сразу,Это почти как chain-методы — LLM это обожают


Мои рекомендации (что взять в первую очередь)
Топ-4 самых вкусных и безопасных для копирования в LUMEN:

Глагольные конструкции + noise words — add years to age, move input to buffer, subtract tax from total giving net
→ Самое человеческое, что есть в COBOL, и LLM это проглотят без проблем.
Condition names — condition adult value 18..150 → if adult then ...
→ Очень сильная фича для бизнес-логики, почти не встречается в современных языках.
Picture / format — picture "999,999.99" или display price with format "currency:USD"
→ Удобно для вывода, особенно в data/reporting-сценариях.
Perform thru — perform validate thru finalize
→ Простой и читаемый способ структурировать большие процедуры без функций.

Что точно не стоит брать

Жёсткую колонковую разметку (6–72 столбцы) — это уже артефакт перфокарт, убьёт любой современный редактор.
DIVISION/SECTION как обязательные — лучше сделать опциональными или заменить на section/paragraph как подсказки.
88-level в полном виде — слишком много магии для новичков и LLM.


Вот маленький, самодостаточный кусочек кода на LUMEN, который использует 4 идеи из COBOL, но при этом выглядит современно, читаемо и приятно для глаза в 2026 году.


section identification
    program-id "monthly-sales-report"
    author     "Larisa"
    date       "March 20, 2026"

section data
    flow input-file   picture "sales-q1-2026.csv"
    flow output-file  picture "report-q1-2026.txt" format "fixed-width"

    condition valid-record value true false
    condition adult-customer value 18..120

section procedures

paragraph main-logic
    open input-file  giving input-stream
    open output-file giving report-stream

    perform read-and-process-record thru end-of-file

    close input-file
    close output-file
    display "Report generated successfully"
    stop run

paragraph read-and-process-record
    read input-file
        at end go to end-of-file
    end-read

    if record is valid-record
        move input-stream.customer-age to temp-age

        if temp-age is adult-customer
            add input-stream.amount to total-adult-sales giving total-adult-sales
            move "ADULT" to customer-category
        else
            add input-stream.amount to total-young-sales giving total-young-sales
            move "YOUNG" to customer-category
        end-if

        write report-stream
            from customer-name    picture "X(30)"
            from customer-category picture "X(10)"
            from input-stream.amount picture "ZZZ,ZZ9.99"
        end-write
    else
        display "Invalid record skipped"
    end-if

    perform read-and-process-record

end-of-file.
    exit paragraph
    
    
Какие именно идеи из COBOL здесь взяты и как адаптированы

Section / Paragraph
→ section procedures, paragraph main-logic, perform ... thru ...
Чёткое разделение на логические блоки, как в COBOL, но без кричащей многословности.
Глагольные конструкции + noise words
→ open input-file giving input-stream
→ add ... to ... giving ...
→ move ... to ...
→ write ... from ...
Всё звучит как естественный английский, но остаётся лаконичным.
Condition names (аналог 88-level)
→ condition valid-record value true false
→ condition adult-customer value 18..120
→ if temp-age is adult-customer
Очень читаемо, почти как бизнес-правило.
Picture clauses
→ picture "sales-q1-2026.csv" (для файла)
→ picture "ZZZ,ZZ9.99" (для вывода суммы)
→ picture "X(30)" (для строки фиксированной длины)
Форматирование остаётся декларативным и понятным.

Почему это выглядит современно и приятно

Нет колонковой разметки и номеров строк.
Нет DIVISION в верхнем регистре.
Используется flow вместо устаревших WORKING-STORAGE.
perform ... thru ... сохранено, но выглядит как вызов подпрограммы.
Всё на нижнем регистре, с современными отступами.
Легко читается даже человеку, который никогда не видел COBOL.

Это именно то, что ты хотела:
многословность и читаемость COBOL + современный вид + человеческая теплота.