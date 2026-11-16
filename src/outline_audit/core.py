"""Core models: heading tree, rules, and report output."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Heading:
    level: int
    text: str
    source_line: int = 0
    html_tag: str = ""


@dataclass
class Finding:
    rule: str
    severity: Severity
    detail: str
    line: int = 0
    heading_text: str = ""


@dataclass
class OutlineNode:
    heading: Heading
    children: list[OutlineNode] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


@dataclass
class AuditResult:
    file: str
    headings: list[Heading] = field(default_factory=list)
    root: OutlineNode | None = None
    findings: list[Finding] = field(default_factory=list)
    max_depth: int = 0

    def to_text(self) -> str:
        lines: list[str] = []
        lines.append(f"outline-audit report — {self.file}")
        lines.append("=" * 60)
        lines.append(f"Headings found: {len(self.headings)}")
        lines.append(f"Max depth: {self.max_depth}")
        lines.append(f"Findings: {len(self.findings)}")
        if self.findings:
            lines.append("")
            for sev in reversed(list(Severity)):
                items = [f for f in self.findings if f.severity == sev]
                if not items:
                    continue
                lines.append(f"{sev.value.upper()} ({len(items)}):")
                for f in items:
                    loc = f" (line {f.line})" if f.line else ""
                    h = f" '{f.heading_text}'" if f.heading_text else ""
                    lines.append(f"  - {f.rule}{loc}{h}: {f.detail}")
        if self.root:
            lines.append("")
            lines.append("Outline:")
            self._render_node(self.root, lines, 0)
        return "\n".join(lines)

    def _render_node(self, node: OutlineNode, lines: list[str], depth: int) -> None:
        indent = "  " * depth
        tag = node.heading.html_tag or f"h{node.heading.level}"
        text = node.heading.text or "(empty)"
        prefix = "[!] " if node.findings else "    "
        lines.append(f"{indent}{prefix}{tag}: {text}")
        for child in node.children:
            self._render_node(child, lines, depth + 1)

    def to_json(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "heading_count": len(self.headings),
            "max_depth": self.max_depth,
            "finding_count": len(self.findings),
            "findings": [
                {
                    "rule": f.rule,
                    "severity": f.severity.value,
                    "detail": f.detail,
                    "line": f.line,
                    "heading_text": f.heading_text,
                }
                for f in self.findings
            ],
            "outline": self._node_to_json(self.root),
        }

    def _node_to_json(self, node: OutlineNode | None) -> dict[str, Any] | None:
        if node is None:
            return None
        return {
            "tag": node.heading.html_tag or f"h{node.heading.level}",
            "text": node.heading.text,
            "level": node.heading.level,
            "line": node.heading.source_line,
            "findings": [
                {
                    "rule": f.rule,
                    "severity": f.severity.value,
                    "detail": f.detail,
                }
                for f in node.findings
            ],
            "children": [self._node_to_json(c) for c in node.children],
        }


PLACEHOLDER_PATTERNS = re.compile(
    r"\b(todo|tbd|lorem|ipsum|placeholder|filler|sample|example|xxx|test|dummy)\b",
    re.IGNORECASE,
)

SHORT_GENERIC_PATTERNS = re.compile(
    r"^(intro|more|details|info|overview|summary|click here|read more|learn more|toggle|menu|nav|footer|header|content|section|article|page)$",
    re.IGNORECASE,
)
