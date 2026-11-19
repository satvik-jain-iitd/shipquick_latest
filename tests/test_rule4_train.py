"""Story #596: rule 4 names the train branch as a second way to land a feature PR (words only)."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _rule4(path, prefix):
    return next(ln for ln in (ROOT / path).read_text(encoding="utf-8").splitlines() if ln.startswith(prefix))


def test_rule_4_names_the_train_and_keeps_its_old_words():
    r = _rule4("CLAUDE.md", "4. ")
    assert "`train/<date>`" in r and "Light CI and the train" in r and "docs/PR_RULES.md" in r
    assert "Closes #N" in r
    assert "Work only from GitHub issues" in r and "PR feat -> dev" in r


def test_the_dense_rule_4_names_the_train():
    r = _rule4("plugin/rules-dense.md", "- Rule 4:")
    assert "train/<date>" in r and "Light CI and the train" in r and "Closes #N" in r
    assert "Work only from GitHub issues" in r and "PR feat -> dev" in r


def test_pr_rules_lists_the_train_steps_in_order():
    text = (ROOT / "docs" / "PR_RULES.md").read_text(encoding="utf-8")
    sec = text.split("## 17. Light CI and the train", 1)[1]
    sec = re.split(r"\n## \d+\.", sec)[0]
    order = ["from `dev`", "targets the train", "reviewer approves each", "git merge --no-ff",
             "opens one PR", "CI runs once", "second reviewer", "owner's yes", "scripts/review_merge.sh"]
    pos = [sec.find(w) for w in order]
    assert -1 not in pos, dict(zip(order, pos))
    assert pos == sorted(pos), pos
    assert sec.find("second reviewer") < sec.find("owner's yes")
    assert "section 13" in sec and ".shipquick/*" in sec and "owner's own merge" in sec


def test_the_rule_copies_check_still_passes():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_rule_copies.py")], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
