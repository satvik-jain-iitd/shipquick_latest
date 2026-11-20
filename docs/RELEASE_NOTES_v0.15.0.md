# ShipQuick v0.15.0 (20 Nov 2026)

A minor release (`pm/agile/RELEASE_GUIDE.md`). It brings the team's new gates to a child project, adds a light CI for work that lands through a train, and adds small tools that print numbers about the work. Everything that is new is on by default except where it says otherwise.

## What a child gains

- **The intent gate runs in a child's CI.** Job `intent-verify` of `checks.yml` checks that a reviewer wrote `Intent verified by QA: <date>` on a story before its PR passes (ADR-021, story #576). The check is strict only for stories made on or after 2026-11-19. Older stories, and PRs that link no story, pass as before.
- **The AC trace runs in a child's CI.** Job `ac-trace` checks that every AC of a linked story names a real test (story #577). It is strict for stories made on or after 2026-11-19 too.
- **The reviewer list is read from the base branch.** In `checks.yml` the jobs `roles` and `intent-verify` read `.shipquick/roles.yml` from the branch a PR goes into, through the API, so a PR cannot add its own login to the list that judges it (story #589). The first PR that adds `roles.yml`, when the base branch has none, reads its own.
- **A child reads its own change map** with the kit's reader (PR #515).
- **Local checks.** `check_local.sh tests` runs only the tests a change names. `check_local.sh coverage` judges two coverage reports you give it. `check_local.sh graph-fresh` warns when the code graph is old. A flaky-test list with an expiry date is checked.
- **Numbers.** `scripts/sprint_metrics.py` prints a table of one day's merged PRs. `scripts/child_bump.py` prints which children pin another kit commit, and a new workflow prints that plan on every `v` tag.

## The kit's own CI (not a child's)

- **Light CI.** A feature PR opened into a `train/<date>` branch skips `test` and the five phone jobs. The train's one PR into `dev` runs everything (ADR-023, `docs/PR_RULES.md` section 17). Rule 4 names the train.
- **The check named `gate`** exists only on a PR into exactly `dev` or `main`, or on a run that is not a PR. A train base gives `gate-light`; any other base gives `gate-other`; a base that differs only by case fails.

## What breaks for children on the bump

- A child PR that links a story made on or after 2026-11-19 with no intent comment, or with an AC that names no test, now fails `checks.yml`.
- Rule 4 in `CLAUDE.md` has a new sentence. A child whose copy of the rule block is older fails its own rule-copies check after the bump (`docs/ADOPTION.md` says how a child takes the new block).
- A child that has no `.shipquick/roles.yml` on its base branch fails the `roles` job, as it did when the file was missing before.

## What a child does after the bump

1. Run `bash knowledge/shipquick_latest/scripts/adopt.sh . --ref v0.15.0`, then take the new rule block into `CLAUDE.md`.
2. Make sure the base branch has `.shipquick/roles.yml`.
3. For a story made after 2026-11-19, ask the reviewer to write the intent comment before the PR.

## Not yet

- **Coverage in CI is not in this release.** `check_local.sh coverage` is local only. The CI step and the number for a new file come in a later story.
- The workflow `child-bump-plan.yml` has not run on GitHub yet. After the release, the owner starts it once by hand with the tag.
- Light CI has run for real only on the kit's own feature PRs into a train. A child with no heavy jobs keeps opening PRs into `dev`; nothing changes for it.
- The gate name rule is for the kit's `ci.yml`. A child's own check (`shipquick-checks / gate`) has the same class of gap and needs its own story.
- The second review of train #603 found follow-ups; they are written as one story after this release.
