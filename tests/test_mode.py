"""S0.15: the three modes and where the choice is kept (story #67). Real git in a throwaway repo; text checks for the docs."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MODE = ROOT / "scripts" / "mode.sh"


def sh(cwd, *args):
    return subprocess.run(["bash", str(MODE), *args], cwd=cwd, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "dev", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@example.com"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "T"], check=True)
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "docs: base"], check=True)
    return tmp_path


def test_s15_an_unset_mode_exits_3_and_says_to_ask_the_owner(repo):
    r = sh(repo, "get")
    assert r.returncode == 3 and "ask the owner" in r.stderr


@pytest.mark.parametrize("mode", ["manual", "semi", "auto"])
def test_s15_set_then_get_gives_the_same_word(repo, mode):
    assert sh(repo, "set", mode).returncode == 0
    r = sh(repo, "get")
    assert r.returncode == 0 and r.stdout.strip() == mode


def test_s15_a_wrong_word_or_no_word_is_refused_and_changes_nothing(repo):
    sh(repo, "set", "semi")
    for args in (("set", "turbo"), ("set",), ("set", "AUTO "), ()):
        assert sh(repo, *args).returncode == 2, args
    assert sh(repo, "get").stdout.strip() == "semi"


def test_s15_every_worktree_shares_the_choice_and_git_does_not_track_it(repo, tmp_path_factory):
    sh(repo, "set", "auto")
    other = tmp_path_factory.mktemp("wt") / "wt"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "-b", "side", str(other)], check=True)
    assert sh(other, "get").stdout.strip() == "auto"
    sh(other, "set", "manual")
    assert sh(repo, "get").stdout.strip() == "manual"
    assert subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True).stdout == ""
    assert (repo / ".git" / "shipquick-mode").read_text(encoding="utf-8").strip() == "manual"


def test_s15_outside_a_git_repo_it_fails_clearly(tmp_path):
    r = sh(tmp_path, "get")
    assert r.returncode == 2 and "git" in r.stderr


def test_s15_the_mode_command_runs_the_script_in_both_places_and_tells_the_peer():
    text = (ROOT / ".claude" / "commands" / "mode.md").read_text(encoding="utf-8")
    assert "scripts/mode.sh" in text and "knowledge/shipquick_latest/scripts/mode.sh" in text and "SendMessage" in text
    for word in ("manual", "semi", "auto"):
        assert word in text


def test_s15_rule_0_asks_for_the_mode_at_session_start():
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    rule0 = [l for l in claude.splitlines() if l.startswith("0. ")]
    assert rule0 and "mode.sh get" in rule0[0] and "ask the owner" in rule0[0]


def test_s15_modes_doc_names_who_reviews_who_merges_and_what_still_stops_in_auto():
    text = (ROOT / "docs" / "MODES.md").read_text(encoding="utf-8")
    for needle in ("Manual", "Semi", "Auto", "reviews", "merges", "money", "secrets", "posts or messages", "review_merge.sh"):
        assert needle in text, needle
