"""Story #425 (F8, epic #86): `modes` and `merge-gate` read their flags, and off is always the safe side: modes off reads as
`manual`, merge-gate off refuses every merge ("the owner merges by hand"). A broken features file takes the same safe side and
prints the error. Real git in a tmp project, a fake gh that logs every call."""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MODE = ROOT / "scripts" / "mode.sh"
MERGE = ROOT / "scripts" / "review_merge.sh"


@pytest.fixture
def proj(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "dev", str(p)], check=True)
    (p / ".shipquick").mkdir()
    (p / ".shipquick" / "mode").write_text("auto\n", encoding="utf-8")
    return p


def flags(p, **f):
    (p / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": {k: {"on": v} for k, v in f.items()}}), encoding="utf-8")


def mode(p):
    return subprocess.run(["bash", str(MODE), "get"], cwd=p, capture_output=True, text=True)


def merge(p, tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir(exist_ok=True)
    log = tmp_path / "gh.log"
    g = bindir / "gh"
    g.write_text(f'#!/usr/bin/env bash\necho "$@" >> {log}\nexit 1\n', encoding="utf-8")
    g.chmod(0o755)
    r = subprocess.run(["bash", str(MERGE), "7", "acme/proj"], cwd=p, env=dict(os.environ, PATH=f"{bindir}:{os.environ['PATH']}"), capture_output=True, text=True)
    return r, (log.read_text(encoding="utf-8") if log.exists() else "")


def test_modes_on_or_no_file_reads_the_real_mode(proj):
    r = mode(proj)
    assert (r.returncode, r.stdout.strip()) == (0, "auto")
    flags(proj, modes=True)
    assert mode(proj).stdout.strip() == "auto"


def test_modes_off_reads_manual_whatever_the_file_says(proj):
    flags(proj, modes=False)
    r = mode(proj)
    assert (r.returncode, r.stdout.strip()) == (0, "manual")


def test_modes_off_is_manual_even_when_no_mode_is_set(proj):
    (proj / ".shipquick" / "mode").unlink()
    flags(proj, modes=False)
    r = mode(proj)
    assert (r.returncode, r.stdout.strip()) == (0, "manual")


def test_a_broken_features_file_reads_manual_and_prints_the_error(proj):
    (proj / ".shipquick" / "features.json").write_bytes(b"{oops")
    r = mode(proj)
    assert r.returncode == 0 and r.stdout.strip() == "manual" and "features" in r.stderr and "not valid JSON" in r.stderr


def test_merge_gate_off_refuses_every_merge_before_asking_github(proj, tmp_path):
    flags(proj, **{"merge-gate": False})
    r, log = merge(proj, tmp_path)
    assert r.returncode == 1 and "merge gate is off: the owner merges by hand" in r.stderr
    assert log == ""


def test_merge_gate_on_goes_on_to_the_normal_checks(proj, tmp_path):
    flags(proj, **{"merge-gate": True})
    r, log = merge(proj, tmp_path)
    assert "merge gate is off" not in r.stderr and log != "", "the normal path must reach gh"


def test_a_broken_features_file_refuses_the_merge_never_allows_it(proj, tmp_path):
    (proj / ".shipquick" / "features.json").write_bytes(b"{oops")
    r, log = merge(proj, tmp_path)
    assert r.returncode == 1 and "features" in r.stderr and "owner merges by hand" in r.stderr and log == ""


def test_the_scripts_say_off_is_the_safe_side():
    assert "safe side" in MODE.read_text(encoding="utf-8") and "safe side" in MERGE.read_text(encoding="utf-8")
