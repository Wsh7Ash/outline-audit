# Usage — outline-audit

## Installation
```shell
pip install -e .
```
Or run directly with `PYTHONPATH=src python -m outline_audit.cli`.

## Audit a Markdown file
```shell
outline-audit doc.md
```

## Audit an HTML file
```shell
outline-audit page.html
```

## JSON output
```shell
outline-audit doc.md --format json
```

## Configure max depth
```shell
outline-audit doc.md --max-depth 4
```

## Rules applied
| Rule | Severity | Meaning |
|---|---|---|
| skipped-level | MEDIUM | Heading level jumps by more than 1 (e.g. h1 → h3) |
| too-deep | LOW | Heading deeper than max depth (default h6) |
| empty-heading | MEDIUM | Heading has no text content |
| duplicate-heading | LOW | Same text used more than once at the same level |
| placeholder-heading | LOW | Heading contains placeholder words (todo, tbd, lorem, etc.) |
| single-heading | LOW | Document has only one heading |
| missing-h1 | MEDIUM | Document has no top-level heading |
| deep-last-heading | LOW | Last heading is deep in the hierarchy |
| non-descriptive-heading | LOW | Heading is a generic word (intro, more, details, etc.) |

## Files accepted
- Markdown files (`.md`) with ATX-style headings (`#`, `##`, etc.)
- HTML files (`.htm`, `.html`) with h1-h6 tags
