from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import SEVERITY_ORDER
from .reporters import as_json, as_sarif, as_text
from .scanner import scan


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Statically audit coding-agent and MCP configuration without executing it.")
    result.add_argument("path", nargs="?", default=".", help="Repository or directory to scan (default: current directory).")
    result.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    result.add_argument("--output", type=Path, help="Write the report to a file instead of stdout.")
    result.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="Exclude a relative path or glob; may be repeated.")
    result.add_argument("--fail-on", choices=tuple(SEVERITY_ORDER), default="high", help="Return exit code 1 at this severity or above.")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: directory not found: {root}", file=sys.stderr)
        return 2
    findings = scan(root, tuple(args.exclude))
    render = {"text": as_text, "json": as_json, "sarif": as_sarif}[args.format]
    report = render(findings, root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    threshold = SEVERITY_ORDER[args.fail_on]
    return 1 if any(SEVERITY_ORDER[item.severity] >= threshold for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

