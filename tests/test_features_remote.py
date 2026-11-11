"""Story #424 review fix: `features.py remote <id> --repo R --ref REF` reads one flag from the file AS IT IS ON the base
branch of a GitHub repo (gh api). 404 = no file = the default. Any other failure or a bad file = exit 2, never "on" (0)."""
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEATURES = ROOT / "scripts" / "features.py"


def run(tmp_path, answer, fid="close-on-merge"):
    b = tmp_path / "bin"; b.mkdir(exist_ok=True)
    (b / "gh").write_text(f'#!/usr/bin/env bash\necho "$@" >> {tmp_path}/log\n{answer}\n', encoding="utf-8")
    (b / "gh").chmod(0o755)
    env = dict(os.environ, PATH=f"{b}:{os.environ['PATH']}")
    r = subprocess.run([sys.executable, str(FEATURES), "remote", fid, "--repo", "o/r", "--ref", "dev"], env=env, capture_output=True, text=True)
    return r, (tmp_path / "log").read_text(encoding="utf-8")


def b64(d):
    return base64.b64encode(json.dumps(d).encode()).decode()


def test_remote_reads_the_file_at_the_ref_and_says_on_or_off(tmp_path):
    r, log = run(tmp_path, f"echo {b64({'version': 1, 'features': {'close-on-merge': {'on': False}}})}")
    assert r.returncode == 1 and r.stdout.strip() == "off"
    assert "repos/o/r/contents/.shipquick/features.json?ref=dev" in log


def test_remote_a_404_means_the_default(tmp_path):
    r, _ = run(tmp_path, 'echo "gh: Not Found (HTTP 404)" >&2; exit 1')
    assert r.returncode == 0 and r.stdout.strip() == "on"


def test_remote_any_other_gh_failure_is_exit_2(tmp_path):
    r, _ = run(tmp_path, 'echo "gh: rate limited" >&2; exit 1')
    assert r.returncode == 2 and "features.py" in r.stderr


def test_remote_a_broken_file_or_unknown_id_is_exit_2(tmp_path):
    r, _ = run(tmp_path, f"echo {base64.b64encode(b'{oops').decode()}")
    assert r.returncode == 2
    r, _ = run(tmp_path, "exit 1", fid="nope")
    assert r.returncode == 2
