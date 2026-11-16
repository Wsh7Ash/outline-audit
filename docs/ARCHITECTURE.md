# Architecture — outline-audit

## Overview
outline-audit parses HTML or Markdown files, extracts a flat list of headings, builds a nested outline tree, runs nine validation rules, and renders a report. It uses only the Python standard library.

## Components

### `src/outline_audit/core.py`
- `Severity`, `Heading`, `Finding`, `OutlineNode`, `AuditResult` dataclasses
- `PLACEHOLDER_PATTERNS` and `SHORT_GENERIC_PATTERNS` regexes
- `AuditResult.to_text()` — nested outline rendering with inline findings
- `AuditResult.to_json()` — machine-readable outline and findings

### `src/outline_audit/parser.py`
- `extract_headings()` — dispatches to HTML regex extractor or Markdown parser by file extension
- `_extract_headings_html_regex()` — finds h1-h6 tags and strips inner markup
- `_extract_headings_markdown()` — parses ATX-style `#` headings with line numbers
- `build_outline()` — builds nested tree from flat heading list using a stack
- `run_rules()` — applies nine rules: skipped-level, too-deep, empty-heading, duplicate-heading, placeholder-heading, single-heading, missing-h1, deep-last-heading, non-descriptive-heading
- `_attach_findings_to_nodes()` — attaches findings to outline nodes for display
- `audit_file()` — top-level entry: extract, build, run rules

### `src/outline_audit/cli.py`
- argparse CLI with `file`, `--format`, `--max-depth`

## Data flow
1. CLI resolves file path and format
2. `extract_headings()` parses the file into a flat heading list
3. `build_outline()` builds a nested tree
4. `run_rules()` evaluates nine rules against the headings
5. Findings are attached to outline nodes
6. Report is rendered as text or JSON

## Design decisions
- **Stdlib only**: `re`, `html.parser`, `dataclasses`, `pathlib`.
- **Two parsers**: HTML via regex (reliable for common tags), Markdown via line regex (ATX-style only).
- **Stack-based outline tree**: standard algorithm for building a hierarchy from a flat ordered list.
- **Nine rules**: a mix of structural (skipped levels, depth), content (placeholder, generic), and document-level (missing h1, single heading) checks.
