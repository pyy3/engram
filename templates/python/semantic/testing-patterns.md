# Python Testing Patterns

## Framework: pytest

- Auto-discovers `test_*.py` files
- Fixtures for setup/teardown (dependency injection)
- Parametrize for data-driven tests
- Markers for categorization (@pytest.mark.slow)

## Fixture Patterns

```python
@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    session = create_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="module")
def api_client():
    """Shared test client (expensive setup, reuse across module)."""
    app = create_app(testing=True)
    return app.test_client()
```

## Mocking

```python
from unittest.mock import patch, MagicMock

def test_sends_email(mocker):
    mock_send = mocker.patch("myapp.services.email.send")
    result = notify_user(user_id=1)
    mock_send.assert_called_once_with(to="user@example.com", subject=ANY)
```

## Parametrize

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("", ""),
    ("123", "123"),
])
def test_upper(input, expected):
    assert input.upper() == expected
```

## Best Practices

- One assertion per test (or tightly related group)
- Name tests: `test_<function>_<scenario>_<expected>`
- Use factories (factory_boy) over complex fixtures
- Test behavior at boundaries, not implementation details
- `conftest.py` for shared fixtures (auto-imported by pytest)
- Integration tests in separate directory with own marks
