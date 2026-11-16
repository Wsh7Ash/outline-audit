"""Shared test fixtures for outline-audit."""

from __future__ import annotations

from pathlib import Path


def write_file(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p
