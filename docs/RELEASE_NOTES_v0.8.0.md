# ShipQuick v0.8.0 (5 Nov 2026)

A minor release, so it ships as `v0.8.0` (`pm/agile/RELEASE_GUIDE.md`). The kit starts enforcing its own
rules by machine, not only by document.

## New

- **The feedback inbox.** A child project that finds a ShipQuick gap says "send this to ShipQuick"
  (`scripts/feedback.sh`, the `shipquick-feedback` skill) instead of opening its own PR here. It fills a
  nine-section template (situation, expected vs seen, steps, impact, five-whys root cause, how big teams
  avoid it, the generic fix) and refuses a blank or too-short section. A similar open issue gets a comment
  instead of a duplicate.
- **The UAT gate.** Every `dev -> main` promotion carries a `## UAT on dev (<link>)` checklist: one box per
  story, with exact steps and an **Expected:** line, so a new user can follow it. `scripts/review_merge.sh`
  refuses the PR while a box is unticked or a story isn't followable.
- **The design-first gate.** A PR that touches a project's own frontend paths must name its approved board
  and approval date in the PR body, or `scripts/check_frontend_design.sh` fails it. A `dev -> main` promotion
  is exempt.
- **Dev and production from day one.** Every project runs two live links from the start; both sit in the
  project's own `CLAUDE.md` and the live roadmap.
- **Adoption is never silent.** A child's own CI fails loudly when its ShipQuick pin doesn't match the
  submodule, or its pre-commit hooks are missing. A child with no caller at all gets caught too: a daily scan
  opens one issue here, naming the child.
- **The release freeze.** `scripts/freeze.sh on "<reason>" --until <date>` writes `.shipquick/freeze` through
  its own PR; while it exists, every merge into `main` refuses, with the reason and until-date in the
  refusal. Lifting it is the owner's call too — never an auto-merge exemption.
- **Provenance over recency.** When a Production design board and the live app disagree, the app is the
  drift and the board stands, unless the PR that changed the app named that approved board. A board can
  never be silently rewritten from whatever the app happens to do.
- **The merge gate, hardened.** A PR can no longer loosen the rules judging it: a required `gate` status
  check must itself succeed, and a fixed list of protected paths (CI config, lint baselines, the gate's own
  enforcers) can never be touched by an auto-mode merge — the owner merges those by hand.
- **Roles and mode, in the source.** `.shipquick/roles.yml` names which GitHub accounts may code, review and
  own a project. No account name lives in any script that decides who may code, review or merge — a PR
  author who isn't a listed coder, or an approval from the author's own account, is refused by CI and by the
  merge gate. The mode itself (`manual`/`semi`/`auto`) can move to a tracked, protected `.shipquick/mode`
  file, so no agent's shell command can flip it to Auto; one account playing both coder and reviewer can
  never set Auto.

## Fixed

- Dependabot's own pull requests are exempt from the team-block check, and its bumps now target `dev`, not
  `main`.
- The merge gate now counts only the latest CI run per check name, so an older stale run can no longer
  shadow a fresh green one.
- `scripts/freeze.sh` no longer leaves a stray branch on the caller's own checkout when there's nothing to
  do; `freeze.sh status` reads `origin/main`, not a possibly-stale local file.

## For child projects

1. Move the submodule to `v0.8.0`.
2. Run `bash knowledge/shipquick_latest/scripts/adopt.sh . --coder <acct> --reviewer <acct> --owner <acct>`
   once, to fill `.shipquick/roles.yml` — CI's `roles` job and `scripts/review_merge.sh` both refuse to merge
   until it exists.
3. If your project has a design board or canvas, read `docs/DESIGN_PROCESS.md` before the next frontend PR.
4. Nothing else changes automatically: the mode stays wherever you last set it, and no existing PR is
   retroactively re-judged.
