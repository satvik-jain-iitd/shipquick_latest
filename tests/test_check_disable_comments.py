"""Story #131: scripts/check_disable_comments.py -- a disable comment or ignore-file entry added on a
new line fails, unless the PR body names the ADR that justifies it."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_disable_comments as cdc  # noqa: E402

DIFF_HEADER = "diff --git a/src/x.ts b/src/x.ts\nindex 000..111 100644\n--- a/src/x.ts\n+++ b/src/x.ts\n@@ -1,0 +1,1 @@\n"


def diff_with_added(path, line):
    return (
        f"diff --git a/{path} b/{path}\n"
        f"index 000..111 100644\n"
        f"--- a/{path}\n"
        f"+++ b/{path}\n"
        f"@@ -1,0 +1,1 @@\n"
        f"+{line}\n"
    )


def test_a_plain_added_line_is_fine():
    assert cdc.check(diff_with_added("src/x.ts", "const x = 1;"), "") is None


def test_an_eslint_disable_on_an_added_line_fails_with_no_adr():
    why = cdc.check(diff_with_added("src/x.ts", "// eslint-disable-next-line"), "")
    assert why and "eslint-disable" in why


def test_an_eslint_disable_is_fine_when_the_body_names_an_adr():
    diff = diff_with_added("src/x.ts", "// eslint-disable-next-line")
    assert cdc.check(diff, "Some text.\nADR: docs/decisions/ADR-012.md\n") is None


def test_stylelint_disable_swiftlint_disable_ts_nocheck_and_suppress_all_fail():
    for path, line in [
        ("src/a.css", "/* stylelint-disable */"),
        ("src/A.swift", "// swiftlint:disable force_cast"),
        ("src/b.ts", "// @ts-nocheck"),
        ("src/C.kt", "@Suppress(\"UNCHECKED_CAST\")"),
    ]:
        why = cdc.check(diff_with_added(path, line), "")
        assert why, (path, line)


def test_a_new_entry_in_an_ignore_file_fails():
    why = cdc.check(diff_with_added(".eslintignore", "legacy/**"), "")
    assert why and "ignore-file entry" in why


def test_a_blank_or_comment_line_in_an_ignore_file_is_fine():
    assert cdc.check(diff_with_added(".eslintignore", ""), "") is None
    assert cdc.check(diff_with_added(".gitignore", "# a comment"), "") is None


def test_a_removed_line_is_never_a_hit():
    diff = "diff --git a/x.ts b/x.ts\nindex 000..111 100644\n--- a/x.ts\n+++ b/x.ts\n@@ -1,1 +0,0 @@\n-// eslint-disable-next-line\n"
    assert cdc.check(diff, "") is None


def test_the_file_header_line_itself_is_never_mistaken_for_an_added_line():
    diff = "diff --git a/x.ts b/x.ts\nnew file mode 100644\nindex 000..111\n--- /dev/null\n+++ b/x.ts\n@@ -0,0 +1,1 @@\n+// eslint-disable-next-line\n"
    why = cdc.check(diff, "")
    assert why and "x.ts" in why   # the +++ header line is skipped, only the real +line counts


def test_added_lines_helper_pairs_each_plus_line_with_its_own_file():
    diff = diff_with_added("a.ts", "one") + diff_with_added("b.ts", "two")
    assert cdc.added_lines(diff) == [("a.ts", "one"), ("b.ts", "two")]


def test_this_check_s_own_source_and_docs_mentioning_the_patterns_are_never_a_hit():
    # scripts/check_disable_comments.py and docs/PR_RULES.md have to contain these literal strings
    # as data (defining and documenting the pattern), not as a real disable directive -- PR #141's
    # own CI run tripped on exactly this before the CODE_EXT scope was added.
    for path, line in [
        ("scripts/check_disable_comments.py", 'DISABLE = re.compile(r"eslint-disable|stylelint-disable")'),
        ("docs/PR_RULES.md", "fails a PR that adds an `eslint-disable`, `stylelint-disable`"),
        ("tests/test_check_disable_comments.py", 'why = cdc.check(diff_with_added("src/x.ts", "// eslint-disable-next-line"), "")'),
    ]:
        assert cdc.check(diff_with_added(path, line), "") is None, path
