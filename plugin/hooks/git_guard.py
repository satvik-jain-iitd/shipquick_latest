#!/usr/bin/env python3
"""PreToolUse (Bash): block git hook bypasses (story #320, A5a).

Blocks `git commit --no-verify` (and `-n`), `git push --no-verify`, and any `core.hooksPath` redirect
(`git -c core.hooksPath=... ` or `git config core.hooksPath`). Story #480: also blocks setting
`PRE_COMMIT_ALLOW_NO_CONFIG` and `pre-commit ... --allow-missing-config`, which pass with no hook run. Exit 2 with the reason on stderr is how
Claude Code blocks a tool call. Everything else exits 0 and prints nothing. Any error exits 0 (fail open).

Idea borrowed from ECC `scripts/hooks/block-no-verify.js` (MIT, read in the study clone, 10 Nov 2026):
a list of bypass flags, a check that the git command is a real command and not text, and a split on
shell separators. Rewritten in stdlib Python.
"""
import json
import os
import shlex
import sys

SEPARATORS = {";", "&&", "||", "|", "&", "(", ")"}
GIT_VALUE_OPTIONS = {"-C", "--git-dir", "--work-tree", "--namespace"}
CONFIG_READ_OPTIONS = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l",
                       "--show-origin", "--show-scope"}
NO_CONFIG_VAR = "PRE_COMMIT_ALLOW_NO_CONFIG="
ASSIGNERS = {"export", "env", "declare", "typeset"}


def no_config_reason(seg):
    """Story #480: a segment that lets pre-commit pass with no config, so no hook runs."""
    for tok in seg:   # only the leading VAR=value words, with or without export / env in front
        if tok.startswith(NO_CONFIG_VAR):
            return "PRE_COMMIT_ALLOW_NO_CONFIG lets a commit pass with no config, so no hook runs"
        if tok not in ASSIGNERS and ("=" not in tok or tok.startswith("-")):
            break
    if "--allow-missing-config" in seg and any(os.path.basename(t) in ("pre-commit", "pre_commit") for t in seg):
        return "pre-commit --allow-missing-config installs hooks that pass with no config, so no hook runs"
    return None


def tokens_of(command):
    # shortcut: a line continuation is joined first, then newlines become separators by a text swap;
    # a shell heredoc is not parsed. Upgrade to a real shell parser when a bypass gets through.
    try:
        lex = shlex.shlex(command.replace("\\\n", " ").replace("\n", " ; "), posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        return list(lex)
    except ValueError:
        return command.split()


def segments_of(tokens):
    seg = []
    for tok in tokens:
        if tok in SEPARATORS:
            if seg:
                yield seg
            seg = []
        else:
            seg.append(tok)
    if seg:
        yield seg


def git_args_of(seg):
    """(words after `git`, VAR=value prefixes) when the segment starts with a git call, else (None, None)."""
    i = 0
    while i < len(seg) and "=" in seg[i] and not seg[i].startswith("-"):
        i += 1
    if i >= len(seg) or os.path.basename(seg[i]) != "git":
        return None, None
    return seg[i + 1:], seg[:i]


def is_no_verify(tok):
    # git accepts any unambiguous prefix of a long option; 6+ chars skips the ambiguous "--no-".
    return len(tok) >= 6 and "--no-verify".startswith(tok)


def split_git_args(args):
    """(-c settings, subcommand, words after the subcommand)."""
    configs = []
    i = 0
    while i < len(args):
        tok = args[i]
        if tok == "-c" and i + 1 < len(args):
            configs.append(args[i + 1])
            i += 2
        elif tok.startswith("--config-env="):
            configs.append(tok.split("=", 1)[1])
            i += 1
        elif tok == "--config-env" and i + 1 < len(args):
            configs.append(args[i + 1])
            i += 2
        elif tok in GIT_VALUE_OPTIONS and i + 1 < len(args):
            i += 2
        elif tok.startswith("-"):
            i += 1
        else:
            return configs, tok, args[i + 1:]
    return configs, None, []


def is_hooks_redirect(setting):
    return setting.split("=", 1)[0].strip().lower() == "core.hookspath"


def block_reason(command):
    for seg in segments_of(tokens_of(command)):
        reason = no_config_reason(seg)
        if reason:
            return reason
        args, prefixes = git_args_of(seg)
        if args is None:
            continue
        if any("core.hookspath" in t.lower() for t in prefixes):
            return "GIT_CONFIG_* env vars move the hooks folder"
        configs, sub, rest = split_git_args(args)
        if any(is_hooks_redirect(c) for c in configs):
            return "git -c core.hooksPath moves the hooks folder"
        if sub == "commit" and (any(is_no_verify(t) for t in rest) or "-n" in rest):
            return "git commit --no-verify skips the pre-commit hooks"
        if sub == "push" and any(is_no_verify(t) for t in rest):
            return "git push --no-verify skips the pre-push hook"
        if sub == "config" and not CONFIG_READ_OPTIONS.intersection(rest):
            if any(is_hooks_redirect(t) for t in rest if not t.startswith("-")):
                return "git config core.hooksPath changes where git finds the hooks"
    return None


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
            return 0
        tool_input = payload.get("tool_input")
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        if not isinstance(command, str):
            return 0
        reason = block_reason(command)
    except Exception:
        return 0
    if reason:
        sys.stderr.write(f"git_guard: blocked. {reason}. Hooks must run: remove the flag, or ask the owner.\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
