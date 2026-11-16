"""Heading extraction from HTML and Markdown for outline-audit."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from .core import AuditResult, Finding, Heading, OutlineNode, Severity, PLACEHOLDER_PATTERNS, SHORT_GENERIC_PATTERNS


class _HTMLHeadings(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.headings: list[Heading] = []
        self._current_line = 1

    def handle_data(self, data: str) -> None:
        pass

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._current_line += 1  # approximate

    def handle_endtag(self, tag: str) -> None:
        pass

    def get_headings(self, html: str) -> list[Heading]:
        # Use a simpler regex approach for reliability
        return _extract_headings_html_regex(html)


def _extract_headings_html_regex(html: str) -> list[Heading]:
    headings: list[Heading] = []
    # Find all heading tags with their content
    for m in re.finditer(r"<(h[1-6])[\s>](.*?)</\1>", html, re.IGNORECASE | re.DOTALL):
        tag = m.group(1).lower()
        level = int(tag[1])
        inner = m.group(2)
        # Strip tags from inner content
        text = re.sub(r"<[^>]+>", "", inner)
        text = re.sub(r"&[a-z]+;", "", text)
        text = text.strip()
        headings.append(Heading(level=level, text=text, html_tag=tag))
    return headings


def _extract_headings_markdown(text: str) -> list[Heading]:
    headings: list[Heading] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if m:
            level = len(m.group(1))
            text_content = m.group(2).strip()
            headings.append(Heading(level=level, text=text_content, source_line=lineno))
    return headings


def extract_headings(path: Path) -> list[Heading]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in (".html", ".htm"):
        return _extract_headings_html_regex(text)
    return _extract_headings_markdown(text)


def build_outline(headings: list[Heading]) -> OutlineNode | None:
    """Build a nested outline tree from a flat heading list."""
    if not headings:
        return None
    root = OutlineNode(heading=headings[0])
    stack: list[OutlineNode] = [root]
    for h in headings[1:]:
        node = OutlineNode(heading=h)
        while stack and stack[-1].heading.level >= h.level:
            stack.pop()
        if stack:
            stack[-1].children.append(node)
        else:
            root.children.append(node)
        stack.append(node)
    return root


def run_rules(headings: list[Heading], root: OutlineNode | None,
              max_depth: int = 6) -> list[Finding]:
    findings: list[Finding] = []

    if not headings:
        findings.append(
            Finding(rule="no-headings", severity=Severity.HIGH,
                    detail="Document has no headings at all",
                    heading_text=""))
        return findings

    # Rule 1: skipped heading levels
    for i in range(1, len(headings)):
        prev = headings[i - 1].level
        curr = headings[i].level
        if curr > prev + 1:
            findings.append(
                Finding(rule="skipped-level", severity=Severity.MEDIUM,
                        detail=f"Heading level jumps from h{prev} to h{curr}",
                        line=headings[i].source_line,
                        heading_text=headings[i].text))

    # Rule 2: too deep
    for h in headings:
        if h.level > max_depth:
            findings.append(
                Finding(rule="too-deep", severity=Severity.LOW,
                        detail=f"Heading h{h.level} exceeds max depth h{max_depth}",
                        line=h.source_line,
                        heading_text=h.text))

    # Rule 3: empty headings
    for h in headings:
        if not h.text or not h.text.strip():
            findings.append(
                Finding(rule="empty-heading", severity=Severity.MEDIUM,
                        detail="Heading has no text content",
                        line=h.source_line,
                        heading_text="(empty)"))

    # Rule 4: duplicate heading text at same level
    seen: dict[tuple[int, str], int] = {}
    for h in headings:
        key = (h.level, h.text.lower().strip())
        if key in seen:
            findings.append(
                Finding(rule="duplicate-heading", severity=Severity.LOW,
                        detail=f"Duplicate heading text at h{h.level}: {h.text!r}",
                        line=h.source_line,
                        heading_text=h.text))
        else:
            seen[key] = h.source_line

    # Rule 5: placeholder headings
    for h in headings:
        if h.text and PLACEHOLDER_PATTERNS.search(h.text):
            findings.append(
                Finding(rule="placeholder-heading", severity=Severity.LOW,
                        detail=f"Heading contains placeholder text: {h.text!r}",
                        line=h.source_line,
                        heading_text=h.text))

    # Rule 6: single heading document
    if len(headings) == 1:
        findings.append(
            Finding(rule="single-heading", severity=Severity.LOW,
                    detail="Document has only one heading",
                    line=headings[0].source_line,
                    heading_text=headings[0].text))

    # Rule 7: missing top-level heading
    if not headings or headings[0].level != 1:
        findings.append(
            Finding(rule="missing-h1", severity=Severity.MEDIUM,
                    detail="Document has no h1 heading",
                    heading_text=""))

    # Rule 8: heading after closing content (heuristic: last heading is h1-h3 but document has content after)
    # Simplified: flag if last heading is not h1-h3
    if headings:
        last = headings[-1]
        if last.level >= 4:
            findings.append(
                Finding(rule="deep-last-heading", severity=Severity.LOW,
                        detail=f"Last heading is h{last.level}, deep in document",
                        line=last.source_line,
                        heading_text=last.text))

    # Rule 9: non-descriptive heading
    for h in headings:
        if h.text and SHORT_GENERIC_PATTERNS.match(h.text.strip()):
            findings.append(
                Finding(rule="non-descriptive-heading", severity=Severity.LOW,
                        detail=f"Generic/non-descriptive heading: {h.text!r}",
                        line=h.source_line,
                        heading_text=h.text))

    return findings


def audit_file(path: Path, max_depth: int = 6) -> AuditResult:
    headings = extract_headings(path)
    root = build_outline(headings)
    findings = run_rules(headings, root, max_depth)

    # Attach findings to nodes
    if root:
        _attach_findings_to_nodes(root, findings)

    max_depth_actual = max((h.level for h in headings), default=0)
    return AuditResult(file=str(path), headings=headings, root=root,
                       findings=findings, max_depth=max_depth_actual)


def _attach_findings_to_nodes(node: OutlineNode, findings: list[Finding]) -> None:
    for f in findings:
        if f.line == node.heading.source_line or (
           f.heading_text and f.heading_text == node.heading.text):
            node.findings.append(f)
    for child in node.children:
        _attach_findings_to_nodes(child, findings)
