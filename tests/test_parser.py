"""Tests for heading extraction and outline auditing."""

from __future__ import annotations

from outline_audit.parser import extract_headings, build_outline, audit_file, run_rules
from outline_audit.core import Severity
from pathlib import Path
import tempfile


def test_extract_markdown_headings():
    text = "# Title\n\n## Section\n\n### Subsection\n"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text)
        p = Path(f.name)
    try:
        headings = extract_headings(p)
        assert len(headings) == 3
        assert headings[0].level == 1
        assert headings[0].text == "Title"
        assert headings[1].level == 2
        assert headings[2].level == 3
    finally:
        p.unlink()


def test_extract_html_headings():
    html = "<h1>Title</h1>\n<h2>Section</h2>\n<h3>Subsection</h3>\n"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        p = Path(f.name)
    try:
        headings = extract_headings(p)
        assert len(headings) == 3
        assert headings[0].level == 1
        assert headings[0].html_tag == "h1"
    finally:
        p.unlink()


def test_build_outline():
    headings = [
        type("H", (), {"level": 1, "text": "T1", "source_line": 1})(),
        type("H", (), {"level": 2, "text": "T2", "source_line": 2})(),
        type("H", (), {"level": 3, "text": "T3", "source_line": 3})(),
        type("H", (), {"level": 2, "text": "T4", "source_line": 4})(),
    ]
    # Use simple objects
    from dataclasses import dataclass
    @dataclass
    class H:
        level: int
        text: str
        source_line: int = 0
    headings = [H(1, "T1", 1), H(2, "T2", 2), H(3, "T3", 3), H(2, "T4", 4)]
    root = build_outline(headings)
    assert root is not None
    assert root.heading.text == "T1"
    assert len(root.children) == 2
    assert root.children[0].heading.text == "T2"
    assert len(root.children[0].children) == 1
    assert root.children[0].children[0].heading.text == "T3"
    assert root.children[1].heading.text == "T4"
    assert len(root.children[1].children) == 0


def test_skipped_level_rule():
    from dataclasses import dataclass
    @dataclass
    class H:
        level: int
        text: str
        source_line: int = 0
    headings = [H(1, "T1", 1), H(3, "T3", 3)]
    root = build_outline(headings)
    findings = run_rules(headings, root)
    assert any(f.rule == "skipped-level" for f in findings)
    assert any(f.severity == Severity.MEDIUM for f in findings)


def test_missing_h1_rule():
    from dataclasses import dataclass
    @dataclass
    class H:
        level: int
        text: str
        source_line: int = 0
    headings = [H(2, "T2", 1)]
    root = build_outline(headings)
    findings = run_rules(headings, root)
    assert any(f.rule == "missing-h1" for f in findings)


def test_empty_heading_rule():
    from dataclasses import dataclass
    @dataclass
    class H:
        level: int
        text: str
        source_line: int = 0
    headings = [H(1, "", 1), H(2, "T2", 2)]
    root = build_outline(headings)
    findings = run_rules(headings, root)
    assert any(f.rule == "empty-heading" for f in findings)


def test_duplicate_heading_rule():
    from dataclasses import dataclass
    @dataclass
    class H:
        level: int
        text: str
        source_line: int = 0
    headings = [H(2, "Section", 1), H(2, "Section", 3)]
    root = build_outline(headings)
    findings = run_rules(headings, root)
    assert any(f.rule == "duplicate-heading" for f in findings)


def test_audit_file_markdown(tmp_path):
    from conftest import write_file
    md = write_file(tmp_path, "doc.md", "# Title\n\n## Section\n\n### Subsection\n")
    result = audit_file(md)
    assert len(result.headings) == 3
    assert result.max_depth == 3


def test_audit_file_html(tmp_path):
    from conftest import write_file
    html = write_file(tmp_path, "page.html", "<h1>Title</h1>\n<h2>Section</h2>\n")
    result = audit_file(html)
    assert len(result.headings) == 2
    assert result.headings[0].html_tag == "h1"
