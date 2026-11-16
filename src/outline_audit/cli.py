"""Command-line interface for outline-audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .parser import audit_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="outline-audit",
        description="Heading outline auditor for HTML and Markdown",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to an HTML or Markdown file to audit",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=6,
        help="Maximum heading depth before flagging",
    )
    args = parser.parse_args(argv)

    if not args.file:
        parser.print_help()
        return 2

    path = Path(args.file)
    if not path.exists():
        print(f"outline-audit: file not found: {path}", file=sys.stderr)
        return 2

    result = audit_file(path, max_depth=args.max_depth)

    if args.format == "json":
        import json
        print(json.dumps(result.to_json(), indent=2))
    else:
        print(result.to_text())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
