"""Story #314 (A9): the SessionStart hook appends a codebase map: names per folder, skips, budget.

The map code is plugin/hooks/map.py, a Python twin of ponytail's ponytail-map.js (MIT).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "plugin" / "hooks"
sys.path.insert(0, str(HOOKS))
from map import BUDGET, build_map  # noqa: E402


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture(root):
    write(root, "scripts/alpha.py", "def make_alpha():\n    pass\n\nclass AlphaThing:\n    pass\n\ndef _hidden():\n    pass\n")
    write(root, "scripts/test_alpha.py", "def test_scripts_case():\n    pass\n")
    write(root, "plugin/beta.sh", "#!/bin/sh\ngreet() {\n  echo hi\n}\n")
    write(root, "app/gamma.swift", "public struct GammaView: View {\n}\nfunc gammaHelper() {\n}\n")
    write(root, "web/delta.ts", "export function deltaRun() {}\nexport const DELTA_LIMIT = 3\n")
    write(root, "ui/eps.kt", "class EpsScreen\nfun epsRender() {}\n")
    write(root, "tests/test_x.py", "def test_secret_case():\n    pass\n")
    write(root, "node_modules/lib/index.js", "export function vendoredThing() {}\n")
    write(root, "knowledge/k.py", "def knowledge_only():\n    pass\n")
    write(root, ".hidden/h.py", "def hidden_dir_name():\n    pass\n")
    return root


def test_names_come_from_each_language_and_private_ones_are_left_out(tmp_path):
    out = build_map(fixture(tmp_path))
    assert "scripts/: make_alpha, AlphaThing" in out
    assert "plugin/: greet" in out
    assert "app/: GammaView, gammaHelper" in out
    assert "web/: deltaRun, DELTA_LIMIT" in out
    assert "ui/: EpsScreen, epsRender" in out
    assert "_hidden" not in out


def test_tests_vendored_and_hidden_folders_are_skipped(tmp_path):
    out = build_map(fixture(tmp_path))
    for skipped in ("test_secret_case", "test_scripts_case", "vendoredThing", "knowledge_only", "hidden_dir_name"):
        assert skipped not in out, skipped


def test_scripts_and_plugin_are_listed_first(tmp_path):
    write(tmp_path, "zeta/z.py", "def zeta_fn():\n    pass\n")
    fixture(tmp_path)
    lines = build_map(tmp_path).split("\n")[1:]
    order = [line.split("/")[0] for line in lines]
    assert order[:2] == ["scripts", "plugin"]
    assert order.index("app") < order.index("zeta")


def test_the_map_stays_within_the_budget_and_says_what_it_left_out(tmp_path):
    for i in range(80):
        write(tmp_path, f"pkg{i:02d}/mod.py", "".join(f"def function_{i}_{j}_with_a_long_name():\n    pass\n" for j in range(6)))
    out = build_map(tmp_path)
    assert len(out) <= BUDGET
    assert "more folders not listed" in out
    assert out.startswith("Codebase map")


def test_a_folder_with_no_source_gives_an_empty_map(tmp_path):
    write(tmp_path, "docs/readme.md", "# nothing to list\n")
    assert build_map(tmp_path) == ""


def test_the_map_of_this_repo_lists_scripts_within_budget():
    out = build_map(ROOT)
    assert len(out) <= BUDGET
    assert any(line.startswith("scripts/: ") and len(line) > len("scripts/: ") for line in out.split("\n"))


def test_session_start_appends_the_map_to_the_rules(tmp_path):
    fixture(tmp_path)
    p = subprocess.run([sys.executable, str(HOOKS / "session_start.py")],
                       input=json.dumps({"cwd": str(tmp_path)}), capture_output=True, text=True,
                       cwd=tmp_path, timeout=10)
    assert p.returncode == 0
    text = json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "Radar first" in text
    assert "scripts/: make_alpha, AlphaThing" in text


def test_a_map_failure_never_blocks_the_session(tmp_path):
    p = subprocess.run([sys.executable, str(HOOKS / "session_start.py")],
                       input=json.dumps({"cwd": str(tmp_path / "missing")}), capture_output=True,
                       text=True, cwd=tmp_path, timeout=10)
    assert p.returncode == 0
    assert "Radar first" in json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]
