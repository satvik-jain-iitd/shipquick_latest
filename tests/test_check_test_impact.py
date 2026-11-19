"""Test-impact manifest validator (ADR-023)."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_test_impact.py"


def run(*args, cwd=None):
    return subprocess.run(["python3", str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd or ROOT)


VALID = """version: 1
languages:
  - id: python
    source: ["src/**/*.py"]
    tests: ["tests/test_*.py"]
    runner: pytest
    command: "pytest {tests}"
global_impact:
  - "pyproject.toml"
mappings:
  - source: "src/foo.py"
    tests: ["tests/test_foo.py"]
contract_groups:
  - id: api
    tests: ["tests/test_api.py"]
full_suite_commands:
  python: "pytest --tb=short"
"""


def test_a_valid_manifest_passes(tmp_path):
    f = tmp_path / "m.yml"; f.write_text(VALID)
    r = run("--file", str(f))
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout + r.stderr


def test_a_missing_manifest_without_require_passes(tmp_path):
    r = run("--file", str(tmp_path / "nope.yml"))
    assert r.returncode == 0, r.stdout + r.stderr


def test_a_missing_manifest_with_require_fails(tmp_path):
    r = run("--file", str(tmp_path / "nope.yml"), "--require")
    assert r.returncode == 1, r.stdout + r.stderr


@pytest.mark.parametrize("bad,needle", [
    ("version: 2\n", "version must be 1"),
    ("foo: bar\nversion: 1\n", "unknown top-level keys"),
    ("version: 1\nlanguages: []\n", None),  # empty languages allowed
])
def test_top_level_validation(tmp_path, bad, needle):
    f = tmp_path / "m.yml"; f.write_text(bad)
    r = run("--file", str(f))
    if needle:
        assert r.returncode == 1 and needle in r.stdout, r.stdout
    else:
        assert r.returncode == 0, r.stdout


def test_duplicate_language_id_fails(tmp_path):
    body = "version: 1\nlanguages:\n  - id: py\n    source: ['a.py']\n    tests: ['t.py']\n    runner: pytest\n    command: 'pytest'\n  - id: py\n    source: ['b.py']\n    tests: ['t2.py']\n    runner: pytest\n    command: 'pytest'\n"
    f = tmp_path / "m.yml"; f.write_text(body)
    r = run("--file", str(f))
    assert r.returncode == 1 and "duplicate language id" in r.stdout


def test_missing_required_language_key_fails(tmp_path):
    body = "version: 1\nlanguages:\n  - id: py\n    source: ['a.py']\n    tests: ['t.py']\n    runner: pytest\n"
    f = tmp_path / "m.yml"; f.write_text(body)
    r = run("--file", str(f))
    assert r.returncode == 1 and "missing keys" in r.stdout


def test_empty_tests_fails(tmp_path):
    body = "version: 1\nlanguages:\n  - id: py\n    source: ['a.py']\n    tests: []\n    runner: pytest\n    command: 'pytest'\n"
    f = tmp_path / "m.yml"; f.write_text(body)
    r = run("--file", str(f))
    assert r.returncode == 1 and "must not be empty" in r.stdout


def test_duplicate_mapping_source_fails(tmp_path):
    body = VALID + "\nmappings:\n  - source: 'src/foo.py'\n    tests: ['tests/test_foo.py']\n  - source: 'src/foo.py'\n    tests: ['tests/test_foo2.py']\n"
    # replace the mappings section properly
    body = "version: 1\nmappings:\n  - source: 'src/foo.py'\n    tests: ['tests/test_foo.py']\n  - source: 'src/foo.py'\n    tests: ['tests/test_foo2.py']\n"
    f = tmp_path / "m.yml"; f.write_text(body)
    r = run("--file", str(f))
    assert r.returncode == 1 and "duplicate mapping source" in r.stdout


def test_invalid_global_impact_fails(tmp_path):
    body = "version: 1\nglobal_impact: 'not-a-list'\n"
    f = tmp_path / "m.yml"; f.write_text(body)
    r = run("--file", str(f))
    assert r.returncode == 1 and "global_impact must be a list" in r.stdout


def test_json_output_valid(tmp_path):
    f = tmp_path / "m.yml"; f.write_text(VALID)
    r = run("--file", str(f), "--json")
    import json
    d = json.loads(r.stdout)
    assert d["ok"] is True
