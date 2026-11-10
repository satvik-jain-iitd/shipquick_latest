"""Story #133: scripts/check_design_literals.py -- a hex, rgb(), hsl() or font-family literal on an ADDED
line of a web style file fails with the file and the line; a token file in the allowlist passes."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_design_literals as cdl  # noqa: E402

SCRIPT = ROOT / "scripts" / "check_design_literals.py"


def diff_with_added(path, *lines, start=7):
    """A -U0 diff that adds `lines` to `path` starting at new-file line `start`."""
    body = "".join(f"+{ln}\n" for ln in lines)
    return (
        f"diff --git a/{path} b/{path}\nindex 000..111 100644\n--- a/{path}\n+++ b/{path}\n"
        f"@@ -{start - 1},0 +{start},{len(lines)} @@\n{body}"
    )


# ---- each literal kind fails, with file and line ----
def test_a_hex_colour_in_added_css_fails_with_file_and_line():
    why = cdl.check(diff_with_added("src/app.css", "color: #ff0033;", start=12), [])
    assert why and "src/app.css:12" in why and "hex" in why


def test_rgb_and_rgba_in_added_tsx_inline_style_fail():
    diff = diff_with_added("src/Card.tsx", "style={{ background: 'rgb(1, 2, 3)' }}", "x", "const c = 'rgba(0,0,0,.5)';")
    why = cdl.check(diff, [])
    assert why and "src/Card.tsx:7" in why and "src/Card.tsx:9" in why and "rgb" in why


def test_hsl_in_added_vue_svelte_and_astro_fails():
    for path in ("src/A.vue", "src/B.svelte", "src/C.astro"):
        why = cdl.check(diff_with_added(path, "  background: hsl(210 40% 50%);"), [])
        assert why and f"{path}:7" in why and "hsl" in why, path


def test_a_font_family_literal_fails_in_css_and_in_tsx():
    assert "src/a.css:7" in (cdl.check(diff_with_added("src/a.css", "font-family: 'Inter', sans-serif;"), []) or "")
    assert "src/A.tsx:7" in (cdl.check(diff_with_added("src/A.tsx", 'fontFamily: "Inter",'), []) or "")


def test_a_tailwind_arbitrary_colour_or_font_fails():
    line = "<div className=\"bg-[#1e293b] text-[rgb(0,0,0)] font-['Inter']\">"
    why = cdl.check(diff_with_added("src/Page.tsx", line), [])
    assert why and "src/Page.tsx:7" in why
    assert cdl.check(diff_with_added("src/Page.tsx", "<p className=\"font-['Inter']\">"), []), "a Tailwind arbitrary font family"


# ---- what passes ----
def test_token_references_and_keywords_pass():
    diff = diff_with_added(
        "src/app.css",
        "color: var(--color-primary);",
        "font-family: var(--font-body);",
        "font-family: inherit;",
        "background: theme('colors.primary');",
    ) + diff_with_added(
        "src/A.tsx",
        "style={{ color: tokens.color.primary, fontFamily: theme.fonts.body }}",
        'className="bg-primary text-on-primary font-body"',
    )
    assert cdl.check(diff, []) is None


def test_a_token_file_in_the_allowlist_passes():
    diff = diff_with_added("src/styles/tokens.css", ":root { --color-primary: #6750a4; --font-body: 'Roboto'; }")
    why = cdl.check(diff, [])
    assert why and "tokens.css" in why
    assert cdl.check(diff, ["src/styles/tokens.css"]) is None
    assert cdl.check(diff, ["*tokens.css"]) is None   # one shell glob per line, like protected_paths.txt


def test_a_removed_line_and_a_non_web_file_are_never_a_hit():
    removed = "diff --git a/x.css b/x.css\n--- a/x.css\n+++ b/x.css\n@@ -1,1 +0,0 @@\n-color: #fff;\n"
    assert cdl.check(removed, []) is None
    assert cdl.check(diff_with_added("scripts/check_design_literals.py", 'HEX = re.compile(r"#abc")'), []) is None
    assert cdl.check(diff_with_added("docs/x.md", "color: #fff"), []) is None
    assert cdl.check(diff_with_added("roadmap/a.js", "const c = '#fff';"), []) is None   # not a file type the story names


def test_a_private_field_an_html_entity_and_an_id_selector_with_letters_are_not_hex():
    assert cdl.check(diff_with_added("src/a.ts", "this.#cafe = 1; const s = '&#dead;';"), []) is None
    assert cdl.check(diff_with_added("src/a.css", "#main-nav { display: flex }"), []) is None


def test_a_story_reference_in_a_comment_is_not_a_hex_colour():
    # PR #374 review: `// story #133` and `/* story #374 */` are references, not colours; a `#cafe = 1` field is not either
    assert cdl.check(diff_with_added("src/a.ts", "export const x = 1;  // story #133"), []) is None
    assert cdl.check(diff_with_added("src/a.css", "/* story #374 */ color: var(--c);"), []) is None
    assert cdl.check(diff_with_added("src/a.css", "color: var(--c); /* was #abc, story #1234 */"), []) is None
    assert cdl.check(diff_with_added("src/a.ts", "class A { #cafe = 1 }"), []) is None
    # a literal outside the comment still fails, and `//` inside a url() is not a comment
    assert cdl.check(diff_with_added("src/a.ts", "const c = '#abc';  // story #133"), [])
    assert cdl.check(diff_with_added("src/a.css", "background: url(https://x.test/a.png) #abcdef;"), [])


def test_line_numbers_follow_the_hunk_header_across_hunks():
    diff = (
        "diff --git a/s.css b/s.css\n--- a/s.css\n+++ b/s.css\n"
        "@@ -1,0 +2,1 @@\n+a: b;\n"
        "@@ -9,0 +30,2 @@\n+x: y;\n+color: #000;\n"
    )
    why = cdl.check(diff, [])
    assert why and "s.css:31" in why and "s.css:2" not in why


def test_the_allowlist_file_reads_globs_and_skips_comments_and_blanks(tmp_path):
    f = tmp_path / "design_token_files.txt"
    f.write_text("# token files\n\n*tokens.css\ndesign/*\n", encoding="utf-8")
    assert cdl.read_allowlist(f) == ["*tokens.css", "design/*"]
    assert cdl.read_allowlist(tmp_path / "missing.txt") == []


def test_the_kit_allowlist_is_protected_and_check_local_names_the_check():
    protected = (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines()
    assert "scripts/design_token_files.txt" in protected
    assert (ROOT / "scripts" / "design_token_files.txt").is_file()
    local = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    usage = next(ln for ln in local.splitlines() if ln.startswith("#   checks:"))
    unknown = next(ln for ln in local.splitlines() if "unknown check:" in ln)
    assert "design-tokens" in usage and "design-tokens" in unknown and "check_design_literals.py" in local


def test_a_design_tokens_job_sits_in_ci_and_checks_and_both_gates_wait_for_it():
    for name in ("ci.yml", "checks.yml"):
        text = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
        assert "\n  design-tokens:\n" in text, name
        job = re.split(r"\n  [a-z][a-z-]*:\n", text.split("\n  design-tokens:\n", 1)[1], maxsplit=1)[0]
        assert "check_design_literals.py" in job, name
        # stylelint only when a css file changed, pinned, needless disables reported, no committed dependency
        assert "npx --yes stylelint@16.26.1" in job and "--report-needless-disables" in job, name
        assert "no css changed" in job, name
        gate = text.split("\n  gate:\n", 1)[1]
        assert re.search(r"needs: \[[^\]]*\bdesign-tokens\b", gate), name
        assert "design-tokens: ${{ needs.design-tokens.result }}" in gate, name


def test_stylelint_installs_the_child_dependencies_and_prefers_the_local_binary():
    # PR #374 review: stylelint resolves `extends` and `plugins` from the project's node_modules, so a child whose
    # config extends stylelint-config-standard fails under bare npx; a config may also live in package.json
    for text in [(ROOT / ".github" / "workflows" / n).read_text(encoding="utf-8") for n in ("ci.yml", "checks.yml")] + [
        (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    ]:
        job = text.split("check_design_literals.py", 1)[1].split("--report-needless-disables", 1)[0]
        assert "npm ci --ignore-scripts" in job and "package-lock.json" in job
        assert 0 < job.find("node_modules/.bin/stylelint") < job.find("npx --yes stylelint@16.26.1"), "local binary first, pinned npx as the fallback"
        assert "package.json" in job and '"stylelint"' in job, "a config in package.json counts"


def test_the_cli_reads_a_diff_file_and_exits_1_with_the_hits(tmp_path):
    d = tmp_path / "d.diff"
    none = str(tmp_path / "none.txt")
    d.write_text(diff_with_added("src/a.css", "color: #123456;"), encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "--diff-file", str(d), "--allowlist", none], capture_output=True, text=True)
    assert r.returncode == 1 and "src/a.css:7" in r.stdout
    d.write_text(diff_with_added("src/a.css", "color: var(--c);"), encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "--diff-file", str(d), "--allowlist", none], capture_output=True, text=True)
    assert r.returncode == 0 and "no design literals" in r.stdout
