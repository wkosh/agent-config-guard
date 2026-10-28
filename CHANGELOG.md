# Changelog

## 0.1.1 - 2026-10-28

- Prepare PyPI metadata and a single package-version source; add `--version`.
- Add release-triggered Trusted Publishing with an isolated publishing job.
- Add wheel/source build checks and installed-package smoke checks to CI.
- Add a copyable GitHub Actions integration and first-publication documentation.
- Keep runtime dependency-free; detection rules are unchanged.

All notable changes are documented here.

## 0.1.0 - 2026-10-21

### Added

- Static discovery of common MCP and coding-agent configuration files.
- Deterministic checks for inline credentials, insecure URLs, shell execution, unpinned package runners, privileged host access, suspicious instructions, and hidden Unicode.
- Text, JSON, and SARIF 2.1.0 reports.
- Configurable severity gate for continuous integration.
- Standard-library-only runtime with no process execution or network access.

