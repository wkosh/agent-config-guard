# Agent Config Guard

Agent Config Guard is an offline, static security scanner for coding-agent and Model Context Protocol (MCP) configuration files.

It helps maintainers review repository-controlled instructions and MCP configuration before those files reach an AI agent with access to a shell, source code, credentials, or external tools.

## Safety properties

- Never starts an MCP server.
- Never makes a network request.
- Never evaluates configuration commands.
- Reads only recognized configuration and instruction files under the selected directory.
- Uses deterministic rules and produces reviewable findings.
- Has no runtime dependencies.

## What it detects

| Rule | Severity | Condition |
|---|---:|---|
| `CFG001` | High | Invalid JSON that tools may interpret inconsistently |
| `CFG002` | Medium | Configuration larger than the scan limit |
| `CFG003` | Medium | Non-UTF-8 configuration |
| `SEC001` | Critical | Credential-like field containing an inline value |
| `SEC002` | Critical | Value matching a high-confidence credential pattern |
| `NET001` | High | Non-local remote MCP URL using HTTP |
| `MCP001` | High | MCP process launched through a command shell |
| `MCP002` | High | Package-runner invocation without an exact version |
| `MCP003` | Medium | Automatic package-install confirmation |
| `MCP004` | Critical | Privileged container or host control access |
| `INS001` | High | Invisible or bidirectional Unicode control characters |
| `INS002` | High | Suspicious overrides, shell downloads, or credential instructions |

These findings are review signals, not proof of malicious intent. See [the threat model](docs/THREAT_MODEL.md) for scope and limitations.

## Quick start

Python 3.10 or later is required.

```bash
python -m pip install agent-config-guard
agent-config-guard .
```

Run directly from a checkout without installing:

```bash
PYTHONPATH=src python -m agent_config_guard .
```

PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m agent_config_guard .
```

## Reports and CI gates

```bash
agent-config-guard . --format json --output reports/agent-config-guard.json
agent-config-guard . --format sarif --output reports/agent-config-guard.sarif
agent-config-guard . --fail-on high
agent-config-guard . --exclude tests/fixtures/unsafe
```

Exit codes:

- `0`: scan completed and no finding met the failure threshold.
- `1`: at least one finding met the failure threshold.
- `2`: invalid command-line input.

## Files scanned

- `.mcp.json` and `mcp.json`
- `settings.json` and `settings.local.json`
- `AGENTS.md`
- `CLAUDE.md`
- `copilot-instructions.md`

Common dependency, build, virtual-environment, and version-control directories are excluded.
Additional relative paths or globs can be excluded explicitly with repeatable `--exclude` options. Exclusions should be narrowly scoped and reviewed in pull requests.

## Responsible use

Scan only repositories you own, maintain, or are authorized to assess. Do not place real credentials in test fixtures or bug reports. If you discover a security problem in this project, follow [SECURITY.md](SECURITY.md).

## Contributing

Rule proposals should include a safe fixture, a triggering fixture, tests, a remediation, and a false-positive discussion. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).

