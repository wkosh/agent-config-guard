# Try Agent Config Guard in CI

The scanner reads recognized configuration/instruction files and produces review signals. It does not execute MCP commands or contact their endpoints. Review findings manually; a clean scan is not a guarantee of safety. See THREAT_MODEL.md for limitations.

After 0.1.1 is published to PyPI, copy `examples/github-actions/agent-config-guard.yml` into your repository's `.github/workflows/` directory. The example pins the scanner version, uses read-only repository permissions, scans pull requests without privileged triggers, and retains a SARIF artifact even when high/critical findings fail the check. It does not require GitHub code-scanning permissions or upload source to a scanning service.

Before publication, install the built local wheel instead:

```console
python -m pip install --no-index --no-deps /path/to/wkosh_agent_config_guard-0.1.1-py3-none-any.whl
agent-config-guard /path/to/your/repository --format sarif --output report.sarif --fail-on high
```

Exit codes: 0 means no finding reached the selected threshold, 1 means the severity gate failed, and 2 indicates invalid command-line input. Operational failures may also terminate the program unsuccessfully; inspect logs as well as the report. If the repository contains no recognized files, it can complete without findings; this does not indicate that the entire source code was audited.

Only scan repositories you own, maintain or are authorized to assess. Keep fixtures synthetic and scope any exclusions narrowly. A fixture for dangerous configuration is data for static analysis: do not execute its commands.

## Feedback that helps

Open an issue with the scanner version, a minimal sanitized configuration, expected/observed output, and false-positive discussion. For vulnerabilities in this scanner, use the private reporting process in SECURITY.md. Never post real credentials or private repository contents.
