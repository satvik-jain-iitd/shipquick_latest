"""Story #187 (S9, ADR-012): adopt.sh --platforms android,ios[,web] wires a child to the kit's UI libraries.
Real git in a throwaway child repo; no network, nothing installed (owner rule 21: no installs on the Mac)."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ADOPT = ROOT / "scripts" / "adopt.sh"
HEAD = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
SNIP = "ui/platforms"


def adopt(child, *args):
    return subprocess.run(["bash", str(ADOPT), str(child), *args], capture_output=True, text=True)


@pytest.fixture
def child(tmp_path):
    c = tmp_path / "my-child"
    (c / ".github" / "workflows").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "dev", str(c)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=c, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=c, check=True)
    (c / ".github" / "workflows" / "ci.yml").write_text("name: Child CI\non:\n  push:\n", encoding="utf-8")
    return c


def test_s187_android_and_ios_write_the_snippets_and_the_lint_copies(child):
    r = adopt(child, "--platforms", "android,ios")
    assert r.returncode == 0, r.stderr
    gradle = (child / SNIP / "android-settings.snippet.kts").read_text(encoding="utf-8")
    assert 'includeBuild("knowledge/shipquick_latest/ui/android")' in gradle
    spm = (child / SNIP / "ios-package.snippet.swift").read_text(encoding="utf-8")
    assert '.package(path: "knowledge/shipquick_latest/ui/ios")' in spm
    for name in ["detekt.yml", "detekt-ci.yml", "UiRulesKonsistTest.kt"]:
        assert (child / SNIP / "lint" / name).read_bytes() == (ROOT / "ui" / "android" / "lint" / name).read_bytes(), name
    assert (child / SNIP / "lint" / "swiftlint.yml").read_bytes() == (ROOT / "ui" / "ios" / "lint" / "swiftlint.yml").read_bytes()


def test_s187_the_protected_list_for_the_child_names_the_lint_paths(child):
    adopt(child, "--platforms", "android,ios")
    prot = (child / SNIP / "PROTECTED.txt").read_text(encoding="utf-8")
    for glob in ["ui/platforms/lint/*", ".swiftlint.yml", "detekt*.yml"]:
        assert glob in prot.splitlines(), glob


def test_s187_ios_only_writes_no_android_files(child):
    r = adopt(child, "--platforms", "ios")
    assert r.returncode == 0, r.stderr
    assert (child / SNIP / "ios-package.snippet.swift").exists()
    assert not (child / SNIP / "android-settings.snippet.kts").exists()
    assert not (child / SNIP / "lint" / "detekt.yml").exists()


def test_s187_web_writes_the_astryx_note_and_the_ci_only_command(child):
    r = adopt(child, "--platforms", "web")
    assert r.returncode == 0, r.stderr
    note = (child / SNIP / "web-astryx.md").read_text(encoding="utf-8")
    assert "ui.sh init" in note and "CI" in note


def test_s187_an_unknown_platform_is_refused_and_nothing_is_written(child):
    r = adopt(child, "--platforms", "android,windows")
    assert r.returncode == 2 and "windows" in r.stderr
    assert not (child / SNIP).exists()


def test_s187_run_prints_the_ui_init_command_for_ci_and_runs_nothing(child):
    r = adopt(child, "--platforms", "android,ios")
    assert r.returncode == 0, r.stderr
    assert "ui.sh init" in r.stdout and "CI" in r.stdout
    assert not (child / "ui" / "tool" / "node_modules").exists()


def test_s187_a_second_run_changes_nothing(child):
    adopt(child, "--platforms", "android,ios")
    r = adopt(child, "--platforms", "android,ios")
    assert r.returncode == 0 and "created" not in r.stdout and "updated" not in r.stdout


def test_s187_check_reports_the_platform_verdict_for_an_adopted_child(child):
    adopt(child, "--platforms", "android,ios")
    r = adopt(child, "--check", "--platforms", "android,ios")
    assert "platforms: OK android,ios" in r.stdout


def test_s187_check_names_a_missing_platform_file(child):
    adopt(child, "--platforms", "android,ios")
    (child / SNIP / "lint" / "detekt.yml").unlink()
    r = adopt(child, "--check", "--platforms", "android,ios")
    assert "platforms: not ready" in r.stdout and "detekt.yml" in r.stdout


