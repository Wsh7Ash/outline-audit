# outline-audit

## HTML and Markdown heading outline auditor with nine validation rules

A document's heading outline is the backbone of screen-reader navigation and skim-reading; when headings skip levels, nest too deeply, or duplicate labels, the structure silently breaks. **outline-audit** parses HTML and Markdown files, extracts the heading tree, and applies nine rules to produce a nested outline with severity-ranked findings.

- **Problem:** Authors and docs teams rarely check heading hierarchy; skipped levels and duplicate labels drift in over time.
- **Solution:** Offline parser that extracts headings from HTML or Markdown, runs rule checks, and renders a nested outline with inline findings.
- **Audience:** Content authors, docs maintainers, and accessibility reviewers.

## Quick start

```shell
# install from source
pip install -e .

# audit an HTML file
outline-audit page.html

# audit a Markdown file
outline-audit doc.md

# JSON output
outline-audit doc.md --format json
```

## Rules

1. **Skipped heading level** — e.g. h1 → h3 with no h2.
2. **Heading too deep** — nesting deeper than a configured max (default 6).
3. **Empty heading** — heading with no text content.
4. **Duplicate heading text** — same text used more than once at the same level.
5. **Placeholder heading** — headings containing "todo", "tbd", "lorem", etc.
6. **Single heading document** — only one heading present.
7. **Missing top-level heading** — no h1 in the document.
8. **Heading after closing content** — heading appearing after the main content closes.
9. **Non-descriptive heading** — very short or generic headings like "Intro" or "More".

## Outputs

- **Text report** — nested outline with rule violations inline.
- **JSON report** — machine-readable outline tree plus findings list.

## Tested with

- Python 3.12+
- Standard library only; no network calls.

## License

MIT
