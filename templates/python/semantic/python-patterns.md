# Python Patterns & Best Practices

## Project Structure

```
project/
├── src/project_name/     # Source code (src layout)
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
│   ├── conftest.py       # Shared fixtures
│   ├── unit/
│   └── integration/
├── pyproject.toml        # Project config (PEP 621)
├── README.md
└── .github/workflows/
```

## Modern Python (3.10+)

- **Type hints** everywhere: `def greet(name: str) -> str:`
- **Structural pattern matching**: `match command: case "quit": ...`
- **Union types**: `str | None` instead of `Optional[str]`
- **dataclasses** or **Pydantic** for structured data (not dicts)
- **f-strings** for formatting: `f"{name=}, {count=}"`
- **pathlib.Path** over os.path
- **walrus operator**: `if (n := len(data)) > 10:`

## Error Handling

- Specific exceptions over generic `except Exception`
- Custom exception hierarchy for domains
- Context managers for resource cleanup
- `contextlib.suppress()` for expected/ignorable errors
- Never silence errors silently — at minimum, log them

## Performance Tips

- `functools.lru_cache` for expensive pure functions
- Generators for large sequences (yield, not list)
- `collections.defaultdict`, `Counter`, `deque` for common patterns
- `asyncio` for I/O-bound concurrency
- `multiprocessing` for CPU-bound parallelism

## Common Gotchas

- Mutable default arguments: `def f(items=None): items = items or []`
- Late binding in closures: `lambda x=x: x` for capture
- `is` vs `==`: use `is` only for None/singletons
- Import cycles: restructure or use TYPE_CHECKING guard
- GIL prevents true threading parallelism for CPU-bound work
