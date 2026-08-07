# LUMEN — Metamorphic Programming Language
*A language that evolves with you.*

> **morph is to LUMEN what async/await is to JavaScript, ownership is to Rust, and monads are to Haskell.**

> ⚠️ **Status: design stage.** The language specification is complete, but the interpreter is not implemented yet — `src/` contains a CLI stub (banner and version only). The code samples below show what LUMEN **will** look like; they cannot be executed yet. Implementation plan: `docs/lumen_todo.md`, roadmap: `ROADMAP.md`.

*Русская версия: [README.md](README.md)*

---

## About

LUMEN is a general-purpose programming language based on the **metamorphic paradigm**.
The central idea: code is a **living structure** that evolves through states.

**Killer feature** — the `morph` block: a language construct (not a library) that declares a named state and a chain of its transformations with built-in history.

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

No existing language offers state evolution as a first-class language abstraction.

---

## Core ideas

- **Morph blocks** — named transformation chains with built-in history, `skip` conditions, and introspection.
- **Type transformation** — values move between types by formal rules: `"42" as Number`, `42 + "!" → "42!"`.
- **Function evolution** — functions extend behavior via `when` clauses without redefinition.
- **Living structures** — Map objects change their fields at any moment: `user.age = 30`, `remove age from user`.
- **Context adaptation** — the execution context (`cli`, `test`) affects how operations are interpreted.
- **LLM-native** — built-in `shadow`, `think`, `reason`, `explain` directives: parseable but non-executable hints for language models.

---

## Documentation

Primary documents are currently in Russian. English translations are planned before the community launch.

| Document | File |
|---|---|
| Language manifesto | `docs/lumen_manifesto.md` |
| Formal specification (source of truth) | `docs/lumen_spec.md` |
| Technical requirements | `docs/lumen_tz.md` |
| Implementation TODO (12 stages) | `docs/lumen_todo.md` |
| Built-in functions reference | `docs/lumen_builtins.md` |
| Error messages reference | `docs/lumen_errors.md` |
| Open questions | `docs/lumen_open_questions.md` |
| Roadmap | `ROADMAP.md` |

---

## Target niches

| Niche | Why LUMEN |
|---|---|
| Data / ETL / ML pipelines | `morph` is the natural abstraction for clean → enrich → train |
| LLM agents | observe → reason → act = a `morph` block with the ReAct pattern |
| State machines / workflows | Business processes, games, IoT |
| DSL prototyping | Fast extension without changing the core |
| Education | Low entry barrier, Ruby-like syntax |

---

## Stack

- **Python 3.10+** — interpreter prototype (standard library only)
- **C** — transpiler and runtime (phase 2)
- **pytest** — tests
- **Hand-written recursive descent** parser

---

## Contributing

See `CONTRIBUTING.md`. At the current stage the most valuable contributions are specification review, open-questions discussion, and implementing stages from `docs/lumen_todo.md`.

## License

MIT — see `LICENSE`.
