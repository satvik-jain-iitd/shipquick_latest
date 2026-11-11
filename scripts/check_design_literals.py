"""Story #133: a colour or font literal on an ADDED line of a web style file fails the PR. The look comes
from the tokens (`design/tokens.json` and what is generated from it), so app code says `var(--color-primary)`,
`theme.fonts.body` or a Tailwind token class, never `#6750a4`, `rgb(...)`, `hsl(...)` or `font-family: Inter`.
This reads the diff, so it also sees TSX inline styles and Tailwind arbitrary values (`bg-[#...]`) that
stylelint never sees. The token files themselves are allowlisted in `scripts/design_token_files.txt`
(a protected path: a PR cannot allowlist its own file to dodge the check in auto mode).

Usage: python3 scripts/check_design_literals.py --base <ref> [--repo <path>] [--allowlist <file>]...
       python3 scripts/check_design_literals.py --diff-file <f> [--allowlist <file>]...
Exit 0 and "no design literals on added lines", or exit 1 and one `path:line: <kind> literal: <text>` per hit.
"""
import argparse
import codecs
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWLIST_NAME = "scripts/design_token_files.txt"
WEB_EXT = re.compile(r"\.(css|ts|tsx|astro|vue|svelte)$")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
# `#` + 3, 4, 6 or 8 hex digits, not a private field (`this.#cafe`, `{ #cafe = 1 }`) or an HTML entity (`&#dead;`).
# shortcut: an id selector made only of hex letters (`#face {}`) is a false hit; rename it or allowlist the file.
HEX = re.compile(r"(?<![\w&.])#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b(?!\s*=)")
# PR #374 review: `// story #133` and `/* story #374 */` are references, not colours, so comment text is cut first.
# Round 3: `//` starts a comment only at the line start or after whitespace, so `url(//cdn...)` in a TSX string or a
# .vue/.svelte/.astro <style> block, and `url(https://...)`, never cut the line.
# shortcut: one line at a time, so a `/* ... */` that spans lines keeps its inner lines, and a ` //` inside a string is
# cut. Upgrade to a real tokenizer if a child hits either.
COMMENT = re.compile(r"/\*.*?\*/|(?:^|(?<=\s))//.*$")
# PR #374 review round 2: `//` is never a comment in CSS (`url(//cdn...)` is a protocol-relative URL), so a .css line
# loses only its `/* */` comments.
BLOCK_COMMENT = re.compile(r"/\*.*?\*/")
# Round 3: `rgb(var(--x) / 0.12)` is a token colour with alpha (M3 state layers, Tailwind `<alpha-value>`), not a literal.
FUNC = re.compile(r"\b(?:rgba?|hsla?)\((?!\s*var\()")
# a font-family value that is not a token reference or a CSS keyword
FONT_CSS = re.compile(r"font-family\s*:\s*(?!var\(|inherit\b|initial\b|unset\b|revert\b)\S")
# PR #374 review round 2: the `font:` shorthand sets the family too. In CSS any value that is not a keyword or a token
# fails; in TS only a quoted string fails (`font: theme.fonts.body` is a token reference), see FONT_TS.
# shortcut: CSS-only, so a bare `font: 16px Inter;` inside a TSX template literal passes; quote it or lint the .css.
FONT_SHORTHAND = re.compile(r"\bfont\s*:\s*(?!inherit\b|initial\b|unset\b|revert\b)(?![^;]*var\()\S")
FONT_TS = re.compile(r"\b(?:fontFamily|font)\s*:\s*['\"`]")   # the TSX inline-style twin: a string, not `theme.fonts.body`
TAILWIND_FONT = re.compile(r"\bfont-\[")           # `font-['Inter']`; `bg-[#...]` and `text-[rgb(...)]` hit HEX and FUNC
KINDS = (("hex", HEX), ("rgb/hsl", FUNC), ("font-family", FONT_CSS), ("font-family", FONT_TS), ("tailwind font", TAILWIND_FONT))
CSS_KINDS = (("font-family", FONT_SHORTHAND),)
# Round 3: a .vue, .svelte or .astro line may be <style> CSS or <script> TS, and a -U0 diff does not say which, so the
# shorthand fails there only when its value names a family (a quote or a generic family); `font: string;` passes.
# shortcut: a bare `font: 1rem Inter;` in a <style> block passes; lint the block with stylelint if a child hits it.
FONT_MIXED = re.compile(r"\bfont\s*:(?![^;]*var\()[^;]*(?:['\"]|\b(?:sans-serif|serif|monospace|system-ui|cursive|fantasy)\b)")
MIXED = re.compile(r"\.(astro|vue|svelte)$")
FIX = ("design literal(s) on added lines. Use a token (var(--x), theme.x, a Tailwind token class), "
       f"or list a real token file in {ALLOWLIST_NAME}:")


def added_lines(diff_text: str):
    """(path, new line number, text) for every truly-added line of a unified diff (never the +++ header)."""
    path, n = None, 0
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            p = line[4:].strip()
            # PR #374 review round 4: git quotes a path with a non-ASCII byte (`"b/src/caf\303\251.css"`); unquote
            # it before the b/ strip, so a saved --diff-file with quoted headers is checked too.
            if p.startswith('"') and p.endswith('"'):
                p = codecs.escape_decode(p[1:-1])[0].decode("utf-8")
            path = None if p == "/dev/null" else re.sub(r"^b/", "", p)
            continue
        m = HUNK.match(line)
        if m:
            n = int(m.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            if path:
                yield path, n, line[1:]
            n += 1
        elif line.startswith(" "):   # a context line (none with -U0, but a diff file may carry them)
            n += 1


def read_allowlist(path) -> list[str]:
    """One shell glob per line; `#` comments and blank lines are ignored; a missing file is an empty list."""
    p = Path(path)
    if not p.is_file():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.lstrip().startswith("#")]


def check(diff_text: str, allow: list[str]) -> str | None:
    hits = []
    for path, n, text in added_lines(diff_text):
        if not WEB_EXT.search(path) or any(fnmatch.fnmatchcase(path, g) for g in allow):
            continue
        if "fixtures" in path.split("/")[:-1]:   # test data, bad on purpose; a release PR diffs against main and would count it as added
            continue
        css = path.endswith(".css")
        code = (BLOCK_COMMENT if css else COMMENT).sub("", text)
        extra = CSS_KINDS if css else (("font-family", FONT_MIXED),) if MIXED.search(path) else ()
        kinds = list(dict.fromkeys(k for k, rx in KINDS + extra if rx.search(code)))
        if kinds:
            hits.append(f"{path}:{n}: {', '.join(kinds)} literal: {text.strip()[:80]}")
    return None if not hits else FIX + "\n" + "\n".join(hits)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="the branch this PR is diffed against, e.g. origin/dev")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--diff-file", help="a saved unified diff, instead of running git")
    ap.add_argument("--allowlist", action="append", help=f"glob file(s); default: the kit's and the repo's {ALLOWLIST_NAME}")
    a = ap.parse_args()
    if not a.base and not a.diff_file:
        ap.error("give --base <ref> or --diff-file <f>")
    if a.diff_file:
        diff = Path(a.diff_file).read_text(encoding="utf-8")
    else:
        cmd = ["git", "-c", "core.quotePath=false", "diff", "--unified=0", f"{a.base}...HEAD"]
        diff = subprocess.run(cmd, cwd=a.repo, capture_output=True, text=True, check=True).stdout
    files = a.allowlist or list(dict.fromkeys([str(HERE / "design_token_files.txt"), str(Path(a.repo).resolve() / ALLOWLIST_NAME)]))
    allow = [g for f in files for g in read_allowlist(f)]
    why = check(diff, allow)
    print(why or "no design literals on added lines")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
