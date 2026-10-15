"""S0.6: a teammate block is checked by code before it is relayed."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_block.py"

GOOD = """To reviewer, from coder, re PR #40:
1. Added check_block.py and its tests.
2. CI job team-block reads the PR body.
Need from you: review 40.
"""


def check(text):
    proc = subprocess.run([sys.executable, str(SCRIPT)], input=text,
                          capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def test_good_block_passes():
    assert check(GOOD) == (0, "Block OK")


def test_nothing_needed_last_line_passes():
    code, _ = check(GOOD.replace("Need from you: review 40.", "Nothing needed from you."))
    assert code == 0


def test_block_inside_fences_with_chat_around_it_passes():
    text = "Owner lines yahan.\n\n```\n" + GOOD + "```\n\nmore chat\n"
    assert check(text)[0] == 0


def test_empty_block_fails():
    code, why = check("\n\n")
    assert code == 1 and why == "empty block"


def test_bad_header_fails():
    code, why = check("hello\n1. do it\nNeed from you: x.\n")
    assert code == 1 and why.startswith("bad header")


def test_no_numbered_line_fails():
    code, why = check("To owner, from coder, re PR #1:\nplease merge\nNeed from you: a yes.\n")
    assert code == 1 and why == "no numbered line"


def test_bad_last_line_fails():
    code, why = check("To owner, from coder, re PR #1:\n1. Merge it.\nThanks!\n")
    assert code == 1 and why.startswith("bad last line")


def test_over_120_words_fails():
    long = "To owner, from coder, re PR #1:\n1. " + "word " * 125 + "\nNeed from you: a yes.\n"
    code, why = check(long)
    assert code == 1 and why.startswith("over 120 words")


def test_secret_fails():
    code, why = check("To owner, from coder, re PR #1:\n1. Token is ghp_" + "a" * 30 + "\nNeed from you: x.\n")
    assert code == 1 and why == "looks like a secret"


def test_placeholder_from_pr_template_fails():
    code, _ = check("To reviewer, from coder, re PR #N:\n1.\nNeed from you:\n")
    assert code == 1
