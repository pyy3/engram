# Set Up a Python Project

## Prerequisites
- Python >= 3.10
- uv (recommended) or pip

## Steps

1. Create project structure:
   ```bash
   mkdir my-project && cd my-project
   uv init --lib
   # Or manually:
   mkdir -p src/my_project tests
   touch src/my_project/__init__.py
   ```

2. Configure pyproject.toml:
   ```toml
   [project]
   name = "my-project"
   version = "0.1.0"
   requires-python = ">=3.10"
   dependencies = []

   [project.optional-dependencies]
   dev = ["pytest", "ruff", "mypy"]

   [tool.ruff]
   line-length = 100
   target-version = "py310"

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   ```

3. Set up virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

4. Configure linting:
   ```bash
   ruff check src/
   ruff format src/
   mypy src/
   ```

5. Run tests:
   ```bash
   pytest -v
   ```

## Development Workflow

1. Write code in `src/`
2. Write tests in `tests/`
3. Run `ruff check --fix` before committing
4. Run `pytest` to verify
5. Type check with `mypy`
