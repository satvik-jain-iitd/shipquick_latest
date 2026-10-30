# ShipQuick inbox: one line of feedback from a child project

A session working on a child project (job-search, GoServe, LinkRight, any project that carries ShipQuick as the `knowledge/shipquick_latest` submodule) often hits a ShipQuick gap mid-task: a rule that does not fit, a script that breaks, a check that is too strict. The child session does not know ShipQuick's own rules (branches, TDD, team blocks), so it should not open a full PR there itself.

Instead it runs, from the child repo:

```
knowledge/shipquick_latest/scripts/feedback.sh "<one line that names the gap>" --why "<why it matters>"
```

This opens one issue in `satvik-jain-iitd/shipquick_latest`, labelled `feedback`, with the project name (read from the git remote, or the folder name when there is none), the line and the why.

The ShipQuick coder session (`shipquick-dev`) turns a `feedback` issue into a proper story (its own issue, branch, red test, PR). The reviewer session reviews and merges it like any other story.

If there is no `gh` login for the build account on that machine, `feedback.sh` prints the text to paste by hand and exits 1 — nothing is lost, the child session just reports it in chat instead.

This came from story #111, raised after two full child-project PRs (#108, #110) hit ShipQuick's own CI and carried project-specific numbers into the generic kit.
