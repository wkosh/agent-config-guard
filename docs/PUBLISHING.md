# Publishing 0.1.1

Status: prepared locally; not uploaded to PyPI or pushed to GitHub by this work.
The existing public v0.1.0 release is preserved. Do not move its tag or replace its assets.

## First-time setup

1. Sign in to your own PyPI account and complete its account/email and two-factor requirements.
2. Open https://pypi.org/manage/account/publishing/ and add a pending GitHub publisher:
   - PyPI project name: `kosh-config-guard`
   - Owner: `wkosh`
   - Repository: `agent-config-guard`
   - Workflow filename: `publish.yml`
   - Environment: `pypi`
3. In your GitHub repository settings, create an environment named `pypi`. Configure release approvals and tag restrictions where your plan supports them. The publisher grants this repository/workflow permission to upload the package; check every value before saving.
4. Review and push these source changes to your repository and let CI pass.
5. Create a NEW tag `v0.1.1` pointing to the reviewed commit and publish a non-prerelease GitHub release for it. This triggers `.github/workflows/publish.yml`.
6. The workflow checks the tag/version, runs tests, builds and validates artifacts, tests an installed wheel, and publishes the exact built artifacts through the `pypi` environment. Only the publishing job can request an OIDC token. No permanent API token is required.
7. Confirm the successful workflow result, https://pypi.org/project/kosh-config-guard/0.1.1/ and an installation from the public index before describing the package as published.

A pending publisher does not reserve the project name. If another owner already controls the name, stop and choose a legitimate available name rather than changing credentials or bypassing ownership.

Official references:
- https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
- https://docs.pypi.org/trusted-publishers/using-a-publisher/

## Local verification

```console
python -m pip install build twine
python -m unittest discover -s tests -v
python -m build
python -m twine check --strict dist/*
python scripts/verify_distribution.py dist/kosh_config_guard-0.1.1-py3-none-any.whl
```

The distribution check installs the local wheel without an index or runtime dependencies into a disposable environment outside the checkout. It exercises the installed command, version, safe and unsafe synthetic configurations, SARIF output, severity failure and missing-path errors.

## Adoption and CVP evidence

Publication is distribution infrastructure, not proof that other people depend on the project. Test installs and maintainer downloads must not be represented as independent users. Keep public links to genuine external integrations and feedback. Use only adoption figures actually supported by the CVP form and their source; GitHub release-download counts are not package-registry monthly-download figures.

## Distribution-name update

The PyPI form rejected `agent-config-guard` as too similar to an existing project. The proposed distribution name is now `kosh-config-guard`, identifying the maintainer explicitly. The user registered the pending publisher successfully on 28 October 2026; the package itself is not published yet. The GitHub repository, Python import and CLI command retain their existing names.
