# Default recipe runs both test suites
default: test

# Run both pytest unit tests and behave integration specs
test: pytest behave

# Run pytest unit tests
pytest:
    @echo "== Running pytest unit suite =="
    .venv/bin/python -m pytest tests/ -q -p no:cacheprovider

# Run behave integration specs (offline)
behave:
    @echo "== Running behave integration specs (offline) =="
    .venv/bin/python -m behave tests/features --no-skipped
