# Security

## Purpose
outline-audit is an **accessibility and documentation quality tool**. It parses local HTML and Markdown files to audit heading outline structure.

## Authorized use
Use outline-audit to review documents you own or are authorized to inspect. It is intended for local file review in documentation and accessibility workflows.

## Safe design
- No network access: outline-audit reads local files only.
- No content exfiltration: it does not send document content anywhere.
- No credentials required.

## Limitations
- Heading extraction uses regex for HTML and line-based parsing for Markdown; complex or malformed documents may not be fully parsed.
- Rule findings are heuristics, not definitive accessibility verdicts. A clean result does not guarantee WCAG conformance; a flagged result is a signal for manual review.
- Only ATX-style Markdown headings are parsed; setext-style headings are not supported.

## Handling files
If you audit documents containing sensitive content, treat the files as confidential. Do not commit raw source documents to the repository; the `.gitignore` excludes generated artifacts.
