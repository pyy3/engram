# Deploy a Python Package to PyPI

## Prerequisites
- pyproject.toml configured with [build-system]
- PyPI account + API token
- hatchling or setuptools as build backend

## Steps

1. Install build tools:
   ```bash
   uv pip install build twine
   ```

2. Build the package:
   ```bash
   python -m build
   # Creates dist/my-project-0.1.0.tar.gz and .whl
   ```

3. Test upload (TestPyPI):
   ```bash
   twine upload --repository testpypi dist/*
   pip install --index-url https://test.pypi.org/simple/ my-project
   ```

4. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

5. Verify:
   ```bash
   pip install my-project
   python -c "import my_project; print(my_project.__version__)"
   ```

## Automation (GitHub Actions)

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_TOKEN }}
```

## Version Bumping

Use `bump2version` or manual:
```bash
# Update version in pyproject.toml and __init__.py
git tag v0.2.0
git push --tags  # triggers CI release
```
