# Contributing

## Setup
```shell
pip install -e ".[dev]"
```

## Running tests
```shell
PYTHONPATH=src python -m pytest tests/ -v
```

## Adding a rule
1. Add the rule name and severity in `src/outline_audit/core.py` (via the rules list in `run_rules()`).
2. Add test cases in `tests/test_parser.py`.
3. Update `docs/USAGE.md` rules table.

## Design notes
- Keep the runtime stdlib-only.
- Keep HTML extraction regex-based and Markdown extraction line-based.
- Prefer explainable rules with specific evidence over opaque scores.
