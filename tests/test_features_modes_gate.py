"""Story #425 (F8, epic #86): `modes` and `merge-gate` read their flags, and off is always the safe side: modes off reads as
`manual`, merge-gate off refuses every merge ("the owner merges by hand"). A broken features file takes the same safe side and
prints the error. Real git in a tmp project, a fake gh that logs every call."""
import base64
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


def merge(p, tmp_path, features=None):
    """The fake gh answers `pr view` and the base branch's features file. features: None = 404, "rate" = other failure, else text."""
    bindir = tmp_path / "bin"
    bindir.mkdir(exist_ok=True)
    log = tmp_path / "gh.log"
    if features is None:
        feat = 'echo "gh: Not Found (HTTP 404)" >&2; exit 1'
    elif features == "rate":
        feat = 'echo "gh: rate limited" >&2; exit 1'
    else:
        (tmp_path / "feat.b64").write_text(base64.b64encode(features.encode()).decode(), encoding="utf-8")
        feat = f"cat {tmp_path}/feat.b64"
    g = bindir / "gh"
    g.write_text(f'''#!/usr/bin/env bash
echo "$@" >> {log}
case "$*" in
  *contents/.shipquick/features.json?ref=dev*) {feat} ;;
  "pr view"*) echo '{{"state":"CLOSED","isDraft":false,"mergeable":"MERGEABLE","baseRefName":"dev","headRefOid":"x","title":"t","author":{{"login":"a"}},"body":"","reviews":[],"statusCheckRollup":[]}}' ;;
  *) exit 1 ;;
esac
''', encoding="utf-8")
    g.chmod(0o755)
    r = subprocess.run(["bash", str(MERGE), "7", "acme/proj"], cwd=p, env=dict(os.environ, PATH=f"{bindir}:{os.environ['PATH']}"), capture_output=True, text=True)
    return r, (log.read_text(encoding="utf-8") if log.exists() else "")


def feats(**f):
    return json.dumps({"version": 1, "features": {k: {"on": v} for k, v in f.items()}})


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


def test_merge_gate_off_on_the_base_ref_refuses_the_merge(proj, tmp_path):
    r, log = merge(proj, tmp_path, features=feats(**{"merge-gate": False}))
    assert r.returncode == 1 and "merge gate is off: the owner merges by hand" in r.stderr
    assert "contents/.shipquick/features.json?ref=dev" in log


def test_merge_gate_on_or_no_file_at_the_base_goes_on_to_the_normal_checks(proj, tmp_path):
    for f in (None, feats(**{"merge-gate": True})):
        r, _ = merge(proj, tmp_path, features=f)
        assert "merge gate is off" not in r.stderr and "owner merges by hand" not in r.stderr, r.stderr
        assert "is not open" in r.stderr, "the normal path must reach the open check"


def test_the_local_features_file_is_never_read_by_the_gate(proj, tmp_path):
    flags(proj, **{"merge-gate": False})   # local copy says off: base has no file, so the gate is on
    r, _ = merge(proj, tmp_path)
    assert "merge gate is off" not in r.stderr
    flags(proj, **{"merge-gate": True})    # local copy says on: base says off, so it refuses
    r, _ = merge(proj, tmp_path, features=feats(**{"merge-gate": False}))
    assert "merge gate is off" in r.stderr


def test_an_unreadable_or_broken_base_file_refuses_the_merge_never_allows_it(proj, tmp_path):
    for f in ("rate", "{oops"):
        r, _ = merge(proj, tmp_path, features=f)
        assert r.returncode == 1 and "owner merges by hand" in r.stderr and "features" in r.stderr, r.stderr


def test_the_scripts_say_off_is_the_safe_side():
    assert "safe side" in MODE.read_text(encoding="utf-8") and "safe side" in MERGE.read_text(encoding="utf-8")
