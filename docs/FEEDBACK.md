# ShipQuick inbox: the whole story, in nine sections

A session working on a child project (job-search, GoServe, LinkRight, any project that carries ShipQuick as the `knowledge/shipquick_latest` submodule) often hits a ShipQuick gap mid-task: a rule that does not fit, a script that breaks, a check that is too strict. The child session does not know ShipQuick's own rules (branches, TDD, team blocks), so it should not open a full PR there itself.

The easiest way in is the `shipquick-feedback` skill (say "send this to ShipQuick"): it fills the template from the session, shows it to the owner, runs `feedback.sh`, and reports the issue number. Install it once per machine: `knowledge/shipquick_latest/scripts/install_skill.sh` (links `skills/shipquick-feedback` into `~/.claude/skills`, safe to run twice).

By hand, fill `docs/templates/feedback.md` (or the `.github/ISSUE_TEMPLATE/feedback.yml` form on GitHub) and run, from the child repo:

```
knowledge/shipquick_latest/scripts/feedback.sh --title "<one line>" --body-file <the filled file> [--new]
```

The script fills the header itself (project, ShipQuick commit, date) — never write it yourself. Every section below is required and none may be empty — `feedback.sh` refuses and names the one you skipped, so nothing half-told reaches ShipQuick:

1. **Situation**: project, tool and version, what was being done, ids (PR, issue, run), the exact error text.
2. **Expected vs seen**: what was expected, what happened, and who or what noticed it.
3. **Steps to reproduce**: 3 to 5 numbered steps, and the one command that shows it.
4. **Impact**: how often, time lost, what was blocked.
5. **Root cause**: a five-whys chain — at least three "Why" lines, ending at the real cause. Fewer than three refuses too.
6. **Why ShipQuick did not catch it**: the rule, check or script that was missing or wrong.
7. **How big teams avoid it**: the industry practice, with a source, its tier (A, B, C, K, P) and a confidence from 0 to 1.
8. **Generic fix for ShipQuick**: the change, plus "Applies when" and "Does not apply to"; no project facts.
9. **Stop the repeat**: the test or CI check that fails if it happens again, and the workaround the project uses today.

If an open `feedback` issue already has a similar title, `feedback.sh` comments the new body there instead of opening a second one — pass `--new` to force a fresh issue anyway. The target repo (`$SHIPQUICK_REPO`, default `satvik-jain-iitd/shipquick_latest`) and the build account (`$SHIPQUICK_BUILD_USER`, default `klickbae8yt-star`) can both be overridden, for a fork.

The ShipQuick coder session (`shipquick-dev`) turns a `feedback` issue into a proper story (its own issue, branch, red test, PR). The reviewer session reviews and merges it like any other story.

If there is no `gh` login for the build account on that machine, `feedback.sh` prints the title and the full body to paste by hand and exits 1 — nothing is lost, the child session just reports it in chat instead.

This came from story #111 (one line, free-form), raised after two full child-project PRs (#108, #110) hit ShipQuick's own CI and carried project-specific numbers into the generic kit. Story #118 (30 Oct 2026) replaced that with these nine required sections, a duplicate check, and the `shipquick-feedback` skill, so every mistake becomes a framework rule, check or script, not a lost line in chat. Neither one-line form still works.
