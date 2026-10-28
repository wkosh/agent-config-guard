"""Exercise a built wheel in a temporary environment outside the source checkout."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import venv
from zipfile import ZipFile
from email.parser import BytesParser


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve()
    with ZipFile(wheel) as archive:
        metadata_path = next(name for name in archive.namelist() if name.endswith('.dist-info/METADATA'))
        metadata = BytesParser().parsebytes(archive.read(metadata_path))
    expected_version = metadata['Version']
    assert not metadata.get_all('Requires-Dist'), 'Runtime must remain dependency-free'
    with tempfile.TemporaryDirectory(prefix='agent-config-guard-package-') as temp:
        root = Path(temp)
        env_path = root / 'venv'
        venv.EnvBuilder(with_pip=True).create(env_path)
        python = env_path / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        cli = env_path / ('Scripts/agent-config-guard.exe' if os.name == 'nt' else 'bin/agent-config-guard')
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        env.pop('PYTHONHOME', None)
        def run(command: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
            result = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True)
            if result.returncode != expected:
                raise AssertionError(f'{command!r}: expected {expected}, got {result.returncode}\n{result.stdout}\n{result.stderr}')
            return result
        run([str(python), '-m', 'pip', 'install', '--no-index', '--no-deps', str(wheel)])
        assert run([str(cli), '--version']).stdout.strip() == f'agent-config-guard {expected_version}'
        safe = root / 'safe'
        unsafe = root / 'unsafe'
        safe.mkdir(); unsafe.mkdir()
        (safe / '.mcp.json').write_text('{"mcpServers": {}}', encoding='utf-8')
        (unsafe / '.mcp.json').write_text('{"mcpServers": {"demo": {"command": "bash", "args": ["-c", "echo synthetic-test"]}}}', encoding='utf-8')
        assert json.loads(run([str(cli), str(safe), '--format', 'json']).stdout)['findings'] == []
        report = root / 'reports' / 'findings.sarif'
        run([str(cli), str(unsafe), '--format', 'sarif', '--output', str(report)], expected=1)
        payload = json.loads(report.read_text(encoding='utf-8'))
        assert payload['version'] == '2.1.0'
        assert payload['runs'][0]['tool']['driver']['version'] == expected_version
        assert any(f['ruleId'] == 'MCP001' for f in payload['runs'][0]['results'])
        run([str(cli), str(root / 'missing')], expected=2)
        print(f'PASS: {wheel.name}: metadata, installed entry point, version, safe scan, severity exit code, SARIF, missing path')


if __name__ == '__main__':
    main()
