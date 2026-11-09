"""Story #162 part 2: the QA loop's tools live in the kit (scripts/qa/), generic, with no project facts."""
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "scripts" / "qa"
from PIL import Image   # CI installs pillow; a missing one must fail, never skip


def py(*args, cwd=None):
    return subprocess.run(["python3", *map(str, args)], capture_output=True, text=True, cwd=cwd)


def png(path, w=390, h=844):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (w, h), (240, 240, 240)).save(path)


def test_s162_scorecard_selftest_passes():
    r = py(QA / "scorecard.py", "--selftest")
    assert r.returncode == 0 and "selftest ok" in r.stdout, (r.stdout, r.stderr)


def test_s162_scorecard_reads_the_kit_params_and_an_empty_qa_home(tmp_path):
    r = py(QA / "scorecard.py", tmp_path)
    assert r.returncode == 0, r.stderr
    assert "0 of 2 clean full runs" in r.stdout and "keep going" in r.stdout


def test_s162_scorecard_flags_a_bug_without_a_passing_auto_test(tmp_path):
    (tmp_path / "runs.jsonl").write_text(json.dumps({"run": 1, "scope": "full", "case": "TC 1.1", "attack": "NET-OFF", "by": "owner", "result": "fail", "bug": 9, "escape": True}) + "\n")
    r = py(QA / "scorecard.py", tmp_path)
    assert "#9 (TC 1.1" in r.stdout and "Escapes (owner found outside the cases): #9" in r.stdout, r.stdout


def test_s162_flow_map_draws_every_board_and_an_arrow_per_tap(tmp_path):
    home, out = tmp_path / "qa", tmp_path / "out"
    png(home / "boards-1x" / "Welcome.png"); png(home / "boards-1x" / "Menu.png")
    (home / "controls.json").write_text(json.dumps({"Welcome": [{"text": "Start", "tag": "button", "to": "Menu", "box": [20, 700, 350, 56]}], "Menu": []}))
    flows = home / "flows.json"
    flows.write_text(json.dumps({"name": "First open", "start": "Welcome", "boards": ["Welcome", "Menu"],
                                 "edges": [{"from": "Welcome", "control": "Start", "to": "Menu", "status": "ok"}]}))
    r = py(QA / "flow_map.py", home, flows, out)
    assert r.returncode == 0, r.stderr
    page = (out / "index.html").read_text(encoding="utf-8")
    assert 'data-b="Welcome"' in page and 'data-b="Menu"' in page and 'data-e="1"' in page
    assert (out / "img" / "Menu.jpg").exists()


def test_s162_audit_report_numbers_findings_on_the_screen_image(tmp_path):
    png(tmp_path / "boards" / "Welcome.png")
    (tmp_path / "journey.json").write_text(json.dumps([{"row": "First open", "screens": ["Welcome"]}]))
    f = {"run": 1, "date": "2026-11-09", "screen": "Welcome", "kind": "issue", "lens": "P2", "severity": "Major", "box": [20, 700, 350, 56],
         "see": "The button text is pale.", "why": "Contrast under 4.5:1.", "fix": "Use the dark ink.", "impact": "high", "effort": "S"}
    (tmp_path / "design-audit.jsonl").write_text(json.dumps(f) + "\n")
    r = py(QA / "audit_report.py", tmp_path, "", "Example audit")
    assert r.returncode == 0, r.stderr
    page = (tmp_path / "report" / "index.html").read_text(encoding="utf-8")
    assert "The button text is pale." in page and "Example audit" in page and "now" in page.lower()
    assert (tmp_path / "report" / "img" / "Welcome.jpg").exists()


@pytest.mark.parametrize("name", ["render_boards.mjs", "board_controls.mjs", "check_layout.mjs", "board_html.mjs"])
def test_s162_the_node_helpers_parse(name):
    r = subprocess.run(["node", "--check", str(QA / name)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_s162_board_html_points_relative_and_root_paths_at_the_canvas_folder(tmp_path):
    (tmp_path / "Welcome.dc.html").write_text('<link href="theme.css"><img src="/_blob/a.png"><div data-theme="{{theme}}"></div>')
    js = f"import {{ prepare }} from '{QA / 'board_html.mjs'}'; console.log(prepare('{tmp_path}', 'Welcome'));"
    r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert f'href="file://{tmp_path}/theme.css"' in r.stdout and f'src="file://{tmp_path}/_blob/a.png"' in r.stdout
    assert 'data-theme="light"' in r.stdout


def test_s162_no_project_facts_in_the_kit_tools():
    for f in QA.iterdir():
        text = f.read_text(encoding="utf-8").lower()
        for word in ("goserve", "satvik", "fonts.googleapis", "/system/library"):
            assert word not in text, (f.name, word)


def test_s162_ci_installs_pillow_for_these_tests():
    assert "pillow" in (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
