# Threat model

## Objective

Agent Config Guard identifies repository-controlled configuration that can increase the impact of a compromised, manipulated, or overly trusted coding agent. It is intended for pre-commit checks, code review, and continuous integration.

## Assets

- Source code and unreleased intellectual property.
- Developer and workload credentials.
- Repository integrity and release pipelines.
- Local files accessible to an agent or MCP server.
- Auditability of tool execution.

## Trust boundaries

The scanner treats agent instruction files, MCP configuration, package references, URLs, and embedded command arguments as untrusted data. The scanner itself must not cross the execution boundary: it parses text but does not start processes, resolve packages, contact endpoints, or interpolate environment variables.

## Threats in scope

1. A committed MCP configuration launches a shell that evaluates attacker-controlled text.
2. A package runner fetches an unpinned package that later changes or is taken over.
3. A credential is stored directly in version-controlled configuration.
4. A remote MCP endpoint is contacted without transport encryption.
5. An MCP server receives privileged container or host control.
6. Repository instructions contain hidden Unicode or common instruction-override patterns.
7. Different tools parse invalid or ambiguous configuration differently.

## Threats out of scope

- Proving that an MCP server or package is benign.
- Dynamic analysis of tool descriptions or server responses.
- Detecting every form of natural-language prompt injection.
- General source-code vulnerability scanning.
- Secret revocation or incident response.
- Authorization decisions on behalf of a human reviewer.

## Security design

- Standard-library-only runtime reduces dependency supply-chain exposure.
- Recognized files are read as UTF-8 with a 2 MiB limit.
- No configuration value is executed, expanded, imported, or fetched.
- Output contains file locations and remediation without reproducing suspected secrets.
- Deterministic rule IDs support baselines and code review.

## Known limitations

String-based instruction checks can produce false positives in educational documents. Credential-key checks intentionally prefer recall and may flag placeholders that are not live secrets. Exact package pin formats vary among ecosystems; maintainers should treat the finding as a request for review, not an automatic allegation.

