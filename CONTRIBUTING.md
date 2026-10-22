# Contributing

Contributions are welcome through pull requests and issues.

## Development

No third-party test dependency is required:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

On PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Adding a rule

Every new rule must include:

1. A stable rule ID and severity.
2. A minimal unsafe fixture.
3. A safe fixture that demonstrates a non-finding.
4. Automated tests.
5. A clear remediation.
6. Documentation of expected false positives and limitations.

Never commit real secrets, malware, exploit payloads, private source code, or data obtained without authorization.

## Review principles

- Prefer deterministic checks over opaque scoring.
- Preserve the no-execution and no-network guarantees.
- Avoid reproducing secret values in reports.
- Keep findings actionable and narrowly scoped.

