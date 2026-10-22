from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_config_guard.reporters import as_sarif
from agent_config_guard.scanner import discover, scan


class ScannerTests(unittest.TestCase):
    def test_unsafe_fixture_finds_expected_rules(self) -> None:
        findings = scan(ROOT / "tests" / "fixtures" / "unsafe")
        rule_ids = {finding.rule_id for finding in findings}
        self.assertTrue({"MCP001", "MCP002", "MCP003", "NET001", "SEC001", "INS002"}.issubset(rule_ids))

    def test_safe_fixture_has_no_findings(self) -> None:
        self.assertEqual([], scan(ROOT / "tests" / "fixtures" / "safe"))

    def test_sarif_is_valid_json_and_has_locations(self) -> None:
        root = ROOT / "tests" / "fixtures" / "unsafe"
        payload = json.loads(as_sarif(scan(root), root))
        self.assertEqual("2.1.0", payload["version"])
        self.assertTrue(payload["runs"][0]["results"][0]["locations"])

    def test_discovery_ignores_node_modules(self) -> None:
        paths = discover(ROOT / "tests" / "fixtures")
        self.assertFalse(any("node_modules" in path.parts for path in paths))

    def test_exclude_omits_matching_fixture(self) -> None:
        root = ROOT / "tests" / "fixtures"
        self.assertEqual([], scan(root, ("unsafe",)))


if __name__ == "__main__":
    unittest.main()

