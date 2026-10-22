from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from .models import Finding


SECRET_KEY_RE = re.compile(r"(token|secret|password|passwd|api[_-]?key|private[_-]?key)", re.I)
SECRET_VALUE_RE = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)
SHELL_COMMANDS = {"sh", "bash", "zsh", "cmd", "cmd.exe", "powershell", "pwsh"}
SHELL_FLAGS = {"-c", "/c", "-command", "-encodedcommand", "-enc"}
PACKAGE_RUNNERS = {"npx", "uvx", "pipx", "bunx"}
PINNED_PACKAGE_RE = re.compile(r"^(?:@[A-Za-z0-9_.-]+/)?[A-Za-z0-9_.-]+(?:==|@)v?[0-9][A-Za-z0-9_.+-]*$")
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
SUSPICIOUS_INSTRUCTION_PATTERNS = (
    (re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions", re.I), "instruction override language"),
    (re.compile(r"(?:curl|wget)\b[^\n|]{0,200}\|\s*(?:sh|bash|zsh|powershell|pwsh)\b", re.I), "download piped directly to a shell"),
    (re.compile(r"(?:read|copy|upload|send|exfiltrat\w*)[^\n]{0,100}(?:\.ssh|\.aws|\.env|credentials|private key)", re.I), "instruction involving sensitive credential paths"),
)
UNICODE_CONTROLS = {chr(c) for c in range(0x202A, 0x202F)} | {chr(c) for c in range(0x2066, 0x206A)} | {"\u200b", "\u200c", "\u200d", "\ufeff"}


def _line_for(text: str, needle: str) -> int:
    index = text.find(needle)
    return 1 if index < 0 else text.count("\n", 0, index) + 1


def _walk(value: Any, prefix: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = (*prefix, str(key))
            yield key_path, child
            yield from _walk(child, key_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            item_path = (*prefix, str(index))
            yield item_path, child
            yield from _walk(child, item_path)


def scan_json(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        return [Finding("CFG001", "high", f"Invalid JSON: {exc.msg}", path, exc.lineno, "Fix the file so security tooling and the agent parse the same configuration.")]

    for key_path, value in _walk(document):
        key = key_path[-1].lower()
        location = ".".join(key_path)
        if isinstance(value, str):
            line = _line_for(text, value)
            if SECRET_KEY_RE.search(key) and value and not value.startswith(("${", "$env:", "env:")):
                findings.append(Finding("SEC001", "critical", f"Possible inline credential at {location}.", path, line, "Use a secret manager or environment-variable reference and rotate any exposed credential."))
            if SECRET_VALUE_RE.search(value):
                findings.append(Finding("SEC002", "critical", f"Value at {location} resembles a live credential.", path, line, "Remove and rotate the credential; keep only a variable reference in version control."))
            for url in URL_RE.findall(value):
                parsed = urlparse(url)
                if parsed.scheme.lower() == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
                    findings.append(Finding("NET001", "high", f"Unencrypted remote URL at {location}: {url}", path, line, "Use HTTPS and verify the server identity."))

    servers = document.get("mcpServers", document.get("servers", {})) if isinstance(document, dict) else {}
    if isinstance(servers, dict):
        for server_name, server in servers.items():
            if not isinstance(server, dict):
                continue
            command = str(server.get("command", "")).strip()
            args = [str(item) for item in server.get("args", [])] if isinstance(server.get("args", []), list) else []
            command_name = Path(command).name.lower()
            line = _line_for(text, command)
            if command_name in SHELL_COMMANDS and any(arg.lower() in SHELL_FLAGS for arg in args):
                findings.append(Finding("MCP001", "high", f"MCP server '{server_name}' launches through a command shell.", path, line, "Invoke a reviewed executable directly with fixed arguments; avoid shell evaluation."))
            if command_name in PACKAGE_RUNNERS:
                package_args = [arg for arg in args if not arg.startswith("-")]
                first_package = package_args[0] if package_args else ""
                if not first_package or not PINNED_PACKAGE_RE.match(first_package):
                    findings.append(Finding("MCP002", "high", f"MCP server '{server_name}' uses an unpinned package runner invocation.", path, line, "Pin an exact reviewed package version or immutable commit/digest."))
            if any(arg.lower() in {"-y", "--yes"} for arg in args):
                findings.append(Finding("MCP003", "medium", f"MCP server '{server_name}' auto-confirms package installation.", path, line, "Remove automatic confirmation and review the exact package before installation."))
            joined = " ".join([command, *args]).lower()
            if any(marker in joined for marker in ("/var/run/docker.sock", r"\\.\pipe\docker_engine", "--privileged", "--network=host")):
                findings.append(Finding("MCP004", "critical", f"MCP server '{server_name}' requests high-impact host or container access.", path, line, "Remove privileged/host access or isolate the server in a disposable environment."))
    return findings


def scan_instructions(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for control in UNICODE_CONTROLS:
        if control in text:
            findings.append(Finding("INS001", "high", "Invisible or bidirectional Unicode control character found.", path, _line_for(text, control), "Remove hidden controls and review the surrounding text for instruction spoofing."))
    for pattern, label in SUSPICIOUS_INSTRUCTION_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(Finding("INS002", "high", f"Suspicious agent instruction: {label}.", path, text.count("\n", 0, match.start()) + 1, "Treat repository instructions as untrusted, remove unsafe directives, and require human review."))
    return findings

