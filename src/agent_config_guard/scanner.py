from __future__ import annotations

from pathlib import Path

from .models import Finding
from .rules import scan_instructions, scan_json


JSON_NAMES = {".mcp.json", "mcp.json", "settings.json", "settings.local.json"}
INSTRUCTION_NAMES = {"agents.md", "claude.md", "copilot-instructions.md"}
IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}
MAX_FILE_SIZE = 2 * 1024 * 1024


def discover(root: Path, exclude: tuple[str, ...] = ()) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
            continue
        relative = path.relative_to(root).as_posix()
        if any(Path(relative).match(pattern) or relative.startswith(pattern.rstrip("/") + "/") for pattern in exclude):
            continue
        lowered = path.name.lower()
        if lowered in JSON_NAMES or lowered in INSTRUCTION_NAMES:
            files.append(path)
    return sorted(files)


def scan(root: Path, exclude: tuple[str, ...] = ()) -> list[Finding]:
    findings: list[Finding] = []
    for path in discover(root, exclude):
        if path.stat().st_size > MAX_FILE_SIZE:
            findings.append(Finding("CFG002", "medium", "Configuration file exceeds the 2 MiB scan limit.", path, 1, "Review unusually large agent configuration files manually."))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(Finding("CFG003", "medium", "File is not valid UTF-8.", path, 1, "Use UTF-8 so hidden or ambiguous content can be reviewed consistently."))
            continue
        if path.name.lower().endswith(".json"):
            findings.extend(scan_json(path, text))
        else:
            findings.extend(scan_instructions(path, text))
    return sorted(findings, key=lambda item: (item.path.as_posix(), item.line, item.rule_id))

