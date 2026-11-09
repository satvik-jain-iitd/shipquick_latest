"""Story #153 (part 2 of #146) and #161: the approving review must say the render was compared with the
named board. A correct `Render:` link can still be approved on the code diff alone; this closes that."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_design_reviewed.py"
PR = "## What\nA screen.\n\nDesign board: Production / C1 Welcome\nApproved: 2026-11-08\nRender: https://github.com/o/r/actions/runs/1\n\nCloses #1\n"


def run(pr_body, review_body, tmp_path):
    p, r = tmp_path / "pr.md", tmp_path / "review.md"
    p.write_text(pr_body, encoding="utf-8"); r.write_text(review_body, encoding="utf-8")
    return subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(p), "--review-body-file", str(r)], capture_output=True, text=True)


@pytest.mark.parametrize("review", [
    "Looks right.\nRender: Production / C1 Welcome -- matches\n",
    "render: production / c1 welcome — Matching, all four edges\n",
    "1. ok\nRender: Production / C1 Welcome - match\n",
])
def test_s153_an_approval_naming_the_board_and_saying_matches_passes(review, tmp_path):
    r = run(PR, review, tmp_path)
    assert r.returncode == 0, r.stdout


@pytest.mark.parametrize("review", [
    "LGTM\n",                                                  # code-diff approval only
    "Render: Production / C1 Welcome\n",                       # board named, no comparison verdict
    "Render: Production / C2 Menu -- matches\n",               # a different board
    "Render: <board> -- matches\n",                            # template placeholder
])
def test_s153_an_approval_without_the_compared_line_fails_and_says_why(review, tmp_path):
    r = run(PR, review, tmp_path)
    assert r.returncode == 1 and "Render: Production / C1 Welcome -- matches" in r.stdout, r.stdout


@pytest.mark.parametrize("pr_body", ["## What\nBackend only.\n\nCloses #1\n", "Design board: <name>\nCloses #1\n"])
def test_s153_a_pr_with_no_design_board_needs_no_compared_line(pr_body, tmp_path):
    assert run(pr_body, "LGTM\n", tmp_path).returncode == 0


def test_s161_the_pr_template_asks_for_board_image_render_and_measurements():
    t = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
    for line in ("Design board:", "Approved:", "Render:", "Board image:", "Measurements"):
        assert line in t, line


def test_s161_the_design_process_says_build_from_the_board_and_baselines_never_from_the_first_build():
    d = (ROOT / "docs" / "DESIGN_PROCESS.md").read_text(encoding="utf-8")
    s = (ROOT / "docs" / "SCREENS.md").read_text(encoding="utf-8")
    assert "Build from the board" in d
    assert "never from the first build" in s and "-- matches" in s


def test_s153_a_crlf_body_from_the_github_web_editor_still_matches(tmp_path):
    # The CLI reads files in text mode, which turns CRLF into LF; check() itself must not rely on that.
    import importlib.util
    spec = importlib.util.spec_from_file_location("cdr", SCRIPT); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    assert mod.check(PR.replace("\n", "\r\n"), "Render: Production / C1 Welcome -- matches\r\n") is None
    r = run(PR.replace("\n", "\r\n"), "Render: Production / C1 Welcome -- matches\r\n", tmp_path)
    assert r.returncode == 0, r.stdout


# Story #194: lows from the PR #173 second review.
def test_s194_a_board_name_in_backticks_matches(tmp_path):
    r = run(PR, "Render: `Production / C1 Welcome` -- matches\n", tmp_path)
    assert r.returncode == 0, r.stdout


def test_s194_a_refusal_says_match_failed_and_names_both_sides(tmp_path):
    r = run(PR, "Render: Production / C2 Menu -- matches\n", tmp_path)
    assert r.returncode == 1
    assert "match failed" in r.stdout and "Production / C1 Welcome" in r.stdout and "Production / C2 Menu" in r.stdout
