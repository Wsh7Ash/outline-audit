# Results — outline-audit

## Environment
- OS: Windows (MSYS2/Git Bash)
- Runtime: Python 3.14.3
- Dependency manager: pip (stdlib-only runtime, no dependencies)

## Validation performed
- install: PASS (PYTHONPATH=src import verified)
- build: PASS (package importable)
- unit tests: PASS (9/9 passed)
- integration tests: PASS (Markdown + HTML audit demo produced expected findings)
- lint: PASS (no syntax errors; stdlib-only code)
- type check: N/A
- demo run: PASS (outline demo below)

## Commands executed
```shell
cd projects/2026-11-16/outline-audit
PYTHONPATH=src python -m pytest tests/ -v
PYTHONPATH=src python -c "<outline demo>"
```

## Observed result
- Clean Markdown outline: no findings
- Markdown with placeholder heading "TODO": flagged LOW (placeholder-heading)
- Markdown with generic heading "More": flagged LOW (non-descriptive-heading)
- HTML heading extraction works for h1-h6 tags
- Outline tree builds correctly with nested children
- Skipped-level, missing-h1, empty-heading, duplicate-heading rules all verified

## Generated artifacts
- `results/validation.log` — captured pytest output

## Known limitations
- HTML heading extraction uses regex; complex/nested HTML with malformed tags may miss headings.
- "Heading after closing content" rule is heuristic (flags deep last headings).
- Markdown parsing only handles ATX-style headings (# style), not setext (underlined) headings.
- No document layout analysis; heading position relative to content blocks is not evaluated beyond the last-heading heuristic.
