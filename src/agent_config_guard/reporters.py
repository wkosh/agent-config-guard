from __future__ import annotations

import json
from pathlib import Path

from .models import Finding
from . import __version__


def as_json(findings: list[Finding], root: Path) -> str:
    return json.dumps({"version": __version__, "findings": [finding.to_dict(root) for finding in findings]}, indent=2, ensure_ascii=False)


def as_sarif(findings: list[Finding], root: Path) -> str:
    levels = {"critical": "error", "high": "error", "medium": "warning", "low": "note", "info": "note"}
    rules: dict[str, dict[str, object]] = {}
    results: list[dict[str, object]] = []
    for finding in findings:
        rules.setdefault(finding.rule_id, {"id": finding.rule_id, "shortDescription": {"text": finding.message}, "help": {"text": finding.recommendation}})
        item = finding.to_dict(root)
        results.append({
            "ruleId": finding.rule_id,
            "level": levels[finding.severity],
            "message": {"text": finding.message},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": item["path"]}, "region": {"startLine": finding.line}}}],
        })
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{"tool": {"driver": {"name": "Agent Config Guard", "version": __version__, "rules": list(rules.values())}}, "results": results}],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def as_text(findings: list[Finding], root: Path) -> str:
    if not findings:
        return "Agent Config Guard: no findings."
    lines = [f"Agent Config Guard: {len(findings)} finding(s)"]
    for finding in findings:
        item = finding.to_dict(root)
        lines.append(f"{finding.severity.upper():8} {finding.rule_id} {item['path']}:{finding.line} {finding.message}")
        if finding.recommendation:
            lines.append(f"         Fix: {finding.recommendation}")
    return "\n".join(lines)

