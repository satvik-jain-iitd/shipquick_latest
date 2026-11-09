"""Story #183 (S3, ADR-012): the kit runs Meta's Astryx CLI as shipped, pinned in ui/tool/, through a thin
`scripts/ui.sh` wrapper. The CLI prints some errors with exit 0 (spike, 9 Nov 2026: "Error: Could not find
@astryxdesign/core package", exit 0), so the wrapper must fail on those itself. Native components are served
as reference topics generated from the S2 docs (`scripts/ui_topics.py`), never as stub web components."""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
UI = ROOT / "scripts" / "ui.sh"
TOPICS = ROOT / "scripts" / "ui_topics.py"


def stub(tmp_path, out, code=0):
    s = tmp_path / "astryx"
    s.write_text(f"#!/usr/bin/env bash\necho \"cwd=$PWD\" >&2\ncat <<'OUT'\n{out}\nOUT\nexit {code}\n", encoding="utf-8")
    s.chmod(0o755)
    return s


def ui(tmp_path, out, code=0, *args):
    env = {**os.environ, "UI_ASTRYX_BIN": str(stub(tmp_path, out, code))}
    return subprocess.run(["bash", str(UI), *args], capture_output=True, text=True, env=env)


def test_s183_a_good_answer_passes_through_with_exit_0(tmp_path):
    r = ui(tmp_path, "# Button (Android, Compose Material 3)", 0, "docs", "android-button", "--dense")
    assert r.returncode == 0, r.stderr
    assert "Button (Android" in r.stdout


def test_s183_a_non_zero_exit_fails(tmp_path):
    assert ui(tmp_path, "boom", 3, "doctor").returncode == 3


def test_s183_an_error_line_with_exit_0_fails(tmp_path):
    r = ui(tmp_path, "Error: Could not find @astryxdesign/core package", 0, "component", "--list")
    assert r.returncode == 1 and "Could not find" in r.stdout + r.stderr


def test_s183_a_json_envelope_with_an_error_code_fails(tmp_path):
    body = json.dumps({"apiVersion": 1, "error": "Could not find @astryxdesign/core package", "code": "ERR_CORE_NOT_FOUND"})
    assert ui(tmp_path, body, 0, "component", "Button", "--json").returncode == 1


def test_s183_a_json_doc_that_mentions_err_in_its_text_passes(tmp_path):
    body = json.dumps({"apiVersion": 1, "type": "docs.detail", "data": {"text": "an Error: line inside prose"}})
    assert ui(tmp_path, body, 0, "docs", "x", "--json").returncode == 0


def test_s183_the_cli_runs_in_ui_tool_with_the_integration_linked(tmp_path):
    r = ui(tmp_path, "ok", 0, "doctor")
    assert r.returncode == 0, r.stderr
    assert f"cwd={ROOT / 'ui' / 'tool'}" in r.stderr
    link = ROOT / "ui" / "tool" / "node_modules" / "shipquick-ui"
    assert link.is_symlink() and link.resolve() == (ROOT / "ui" / "integration").resolve()


def test_s183_the_tool_package_pins_exact_versions_with_a_lockfile():
    pkg = json.loads((ROOT / "ui/tool/package.json").read_text())
    deps = {**pkg["dependencies"], **pkg["devDependencies"]}
    assert deps["@astryxdesign/cli"] == deps["@astryxdesign/core"] == "0.7.11"
    assert all(v[0].isdigit() for v in deps.values()), deps
    lock = json.loads((ROOT / "ui/tool/package-lock.json").read_text())
    assert lock["packages"][""]["dependencies"] == pkg["dependencies"]


def test_s183_topics_are_generated_from_the_s2_docs_and_are_current():
    r = subprocess.run(["python3", str(TOPICS), "--check"], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    topic = (ROOT / "ui/integration/docs/android-button.doc.mjs").read_text()
    assert "androidx.compose.material3.Button" in topic and "'primary' | 'secondary' | 'ghost' | 'destructive'" in topic
    assert "HTML form submission" not in topic   # a webOnly prop never reaches a native topic
    assert (ROOT / "ui/integration/docs/ios-button.doc.mjs").exists()


def test_s183_the_integration_registers_no_web_component():
    m = (ROOT / "ui/integration/astryx.integration.mjs").read_text()
    assert "components:" not in m and "docs: './docs'" in m and "agentDocs" in m


def test_s183_a_stale_topic_fails_the_check(tmp_path):
    f = ROOT / "ui/integration/docs/android-button.doc.mjs"
    old = f.read_text()
    try:
        f.write_text(old + "\n// edited by hand\n")
        r = subprocess.run(["python3", str(TOPICS), "--check"], capture_output=True, text=True, cwd=ROOT)
        assert r.returncode == 1 and "android-button" in r.stdout
    finally:
        f.write_text(old)


def test_s183_an_error_on_stderr_with_exit_0_fails(tmp_path):
    s = tmp_path / "astryx"
    s.write_text("#!/usr/bin/env bash\necho 'Warning: shipquick-ui has 1 integration issue(s).' >&2\n"
                 "echo 'Error: Could not find @astryxdesign/core package' >&2\nexit 0\n", encoding="utf-8")
    s.chmod(0o755)
    r = subprocess.run(["bash", str(UI), "component", "--list"], capture_output=True, text=True,
                       env={**os.environ, "UI_ASTRYX_BIN": str(s)})
    assert r.returncode == 1 and "Could not find" in r.stderr


def test_s183_every_topic_list_block_has_a_style_the_cli_accepts():
    # CI on PR #202: the real CLI refused a list with no style ("expected one of ordered|unordered|do|dont").
    import re as _re
    for f in (ROOT / "ui/integration/docs").glob("*.doc.mjs"):
        doc = json.loads(_re.sub(r"^.*?export default ", "", f.read_text(), flags=_re.S).rstrip().rstrip(";"))
        for s in doc["sections"]:
            for block in s["content"]:
                if block["type"] == "list":
                    assert block.get("style") in {"ordered", "unordered", "do", "dont"}, (f.name, s["title"])


def test_s135_a_doc_with_no_dont_line_writes_no_empty_list():
    # CI on PR #209: the real CLI refused ios-stepper ("sections.2.content.1.items: Too small: expected array to have >=1 items").
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from ui_topics import topic
    doc = {"name": "X", "platforms": {"ios": "SwiftUI.X"}, "props": [],
           "usage": {"description": "d", "bestPractices": [{"guidance": True, "description": "do this"}]}}
    for s in topic(doc, {"core": {}}, "ios")["sections"]:
        assert s["content"], s["title"]
        for block in s["content"]:
            assert block["type"] != "list" or block["items"], (s["title"], block)
            assert block["type"] != "table" or block["rows"], (s["title"], block)


# PR #202 second review: scan every line and both streams, and walk the whole JSON.
def run_stub(tmp_path, stdout, stderr="", *args):
    s = tmp_path / "astryx"
    s.write_text(f"#!/usr/bin/env bash\ncat <<'OUT'\n{stdout}\nOUT\ncat >&2 <<'ERR'\n{stderr}\nERR\nexit 0\n", encoding="utf-8")
    s.chmod(0o755)
    return subprocess.run(["bash", str(UI), *args], capture_output=True, text=True, env={**os.environ, "UI_ASTRYX_BIN": str(s)})


@pytest.mark.parametrize("stdout,stderr", [
    ("Loading config\nError: boom", ""),
    ("ok", "note\nError: later on stderr"),
    ("error: lower case", ""),
    ("ERROR something broke", ""),
])
def test_s183_an_error_line_anywhere_fails(tmp_path, stdout, stderr):
    assert run_stub(tmp_path, stdout, stderr, "doctor").returncode == 1


@pytest.mark.parametrize("stdout", ["not json", "", 'Warning: w\n{"error":"x"}'])
def test_s183_json_mode_output_that_will_not_parse_fails(tmp_path, stdout):
    assert run_stub(tmp_path, stdout, "", "docs", "x", "--json").returncode == 1


@pytest.mark.parametrize("stdout", ['{"data":{"error":"boom"}}', '[{"error":"x"}]', '{"ok":false}', '{"data":{"code":"ERR_X"}}'])
def test_s183_a_nested_error_fails(tmp_path, stdout):
    assert run_stub(tmp_path, stdout, "", "docs", "x", "--json").returncode == 1


def test_s183_a_null_error_passes(tmp_path):
    assert run_stub(tmp_path, '{"apiVersion":1,"error":null,"data":{}}', "", "docs", "x", "--json").returncode == 0


def test_s183_json_equals_true_is_json_mode(tmp_path):
    assert run_stub(tmp_path, '{"error":"x"}', "", "docs", "x", "--json=true").returncode == 1


def test_s183_the_ci_smoke_steps_run_with_pipefail():
    ci = (ROOT / ".github/workflows/ci.yml").read_text()
    step = ci[ci.index("The CLI serves the kit's integration as shipped"):].split("run: |")[0]
    assert "shell: bash" in step
