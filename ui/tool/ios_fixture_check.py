#!/usr/bin/env python3
"""Story #221 (rule 38): prove the iOS lint on the fixture app. Run from the repo root (CI job ui-ios-lint).

Runs the CI tier of ui/tool/ios_lint.sh twice: the good screen must pass, the bad screen must fail and the
report must name each rule in BAD_RULES. Exit 0 when both hold, 1 otherwise. Stdlib only."""
import os
import subprocess
import sys

APP = "tests/fixtures/ios/FixtureApp/Sources/FixtureApp"
BAD_RULES = ("no_raw_color", "no_fixed_font_size", "no_custom_shape_or_style")


def lint(screen):
    env = {**os.environ, "CI": "1"}
    p = subprocess.run(["bash", "ui/tool/ios_lint.sh", f"{APP}/{screen}.swift"], env=env, capture_output=True, text=True)
    out = p.stdout + p.stderr
    print(f"--- {screen} (exit {p.returncode})\n{out}")
    return p.returncode, out


def main():
    ok = True
    rc, _ = lint("GoodScreen")
    if rc != 0:
        print("::error::the good screen failed the CI tier")
        ok = False
    rc, out = lint("BadScreen")
    if rc == 0:
        print("::error::the bad screen passed the CI tier")
        return 1
    for rule in BAD_RULES:
        if f"({rule})" in out:
            print(f"reported as wanted: {rule}")
        else:
            print(f"::error::rule not reported: {rule}")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
