# Changelog

All notable changes to this project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A D increment ships as a MINOR bump. So D4 ships as `v0.4.0`.
A hotfix ships as a PATCH bump. A breaking change ships as a MAJOR bump.

See `pm/agile/RELEASE_GUIDE.md` for the release steps.

## [Unreleased]

### Added
- `tests/test_sample_child_walk.py`: the kit's CI walks a generated child (TypeScript-style test names, the kit on its own branch, a screens list, its own workflow) through `adopt.sh`, the bump, `--gate-files`, the real hooks and `check_local.sh`. It runs in the Python test job in under a minute. A new check must be named in the walk (story #504, ADOPTION.md).

### Changed
- `scripts/review_merge.sh` counts only the PR's own, newest run of each workflow (story #496, epic #485 items 15 and 16): a manual or push run on the same head can no longer replace a red PR result, and a pull_request run counts only when its list names exactly this PR (two PRs on one head refuse), a stale row from a run a newer run replaced (a `test` cancelled before the matrix expanded, seen on #509) is not counted. The new helper is `scripts/check_pr_runs.py`. `shortcut-ledger` is in the `needs` of `gate` (still warn-only), and `tests/test_gate_needs.py` fails when a job of `ci.yml` is in neither the needs nor the exempt list.

## [0.14.2] - 2026-11-13
Tag `v0.14.2`, "the tdd check reads other runners' test names, and the screens wiring example runs the check". Notes: `docs/RELEASE_NOTES_v0.14.2.md`.

### Changed
- `scripts/check_tdd.py`: a `## Red` section may name a test file of other runners: `*_test.py`, `*.test.`/`*.spec.` for js, jsx, ts, tsx, mjs, cjs, `*_test.go`, `*Test(s).kt`, `*Test(s).swift`. One list, `TEST_NAMES`, one line per runner. A path in the diff that no name accepts says so (#502, feedback #501).

### Fixed
- `docs/SCREENS.md`: the "Wiring CI" example runs `screens.sh --check` before the upload step, as `check_screens_wired.py` requires, and says how to split a shared e2e run. The check's message names that section. A test runs the example through the check (#503, feedback #500).

## [0.14.1] - 2026-11-13
Tag `v0.14.1`, "a gate-files PR passes the tdd check, and a missing list file stops the check in one line". Notes: `docs/RELEASE_NOTES_v0.14.1.md`.

### Fixed
- `scripts/check_tdd.py`: a gate-files PR (only the files in `scripts/gate_files.txt`) is exempt from the tdd check, as a kit bump is. The exemption reads both lists, so none is typed twice (#491, feedback #490).
- `scripts/check_tdd.py`: a missing or empty `scripts/adopt_files.txt` or `scripts/gate_files.txt` stops the check with one line that names the file, not a traceback (#492 review).

## [0.14.0] - 2026-11-13
Tag `v0.14.0`, "gate files on every code branch of a kit-branch child, the no-config guard, and CI that does not wait for a macOS machine it does not need". Notes: `docs/RELEASE_NOTES_v0.14.0.md`.

### Added
- `adopt.sh --gate-files`: on a code branch of a kit-branch child (rule 24) it copies the gate files ("group A", one list in `scripts/gate_files.txt`) from the kit branch and stages them. No document is written. The git hooks then run on that branch instead of stopping every commit (#479, feedback #478, ADR-017).

### Changed
- `adopt.sh --check` on a code branch of a kit-branch child fails for each gate file that is missing or differs from the kit branch (the pin, the callers, the switches, the roles), and names the fix. It reads the hook config and the switches from the checked-out branch, never from the kit branch. A gate file only on the code branch is a drift too. The compare uses the file on disk (the index for the submodule pin, only the kit entry of `.gitmodules`), and reads the kit branch from `origin` before a local branch. A bump branch cut from the kit branch is read at HEAD and not compared. A child that kept only the caller on `main` reads "not adopted" until it runs `--gate-files` (#479).
- The hook config `adopt.sh` writes starts with a `shipquick-kit` hook: a kit folder that is not checked out stops the commit with one line that says `git submodule update --init`. `adopt.sh` adds it to a config from an older kit; `--check` fails until it is there (#479).
- `ci.yml`: a PR that only edits `ci.yml` no longer runs the phone jobs (`ui=false`, `ios=false`), and a new run of a PR cancels the old one (one concurrency group per PR; push and manual runs are never cancelled). A PR that edits the steps of a `ui-*` job needs one manual full run until #485 (#484).

### Fixed
- `plugin/hooks/git_guard.py` refuses a command that sets `PRE_COMMIT_ALLOW_NO_CONFIG` (as a prefix, with `export` or with `env`) and a `pre-commit` call with `--allow-missing-config`. Both let a commit pass with no hook run, the same as `--no-verify`. The same words as text (a `grep`, a quoted message) pass (#480, feedback #478).

## [0.13.3] - 2026-11-12
Tag `v0.13.3`, "the pre-push hook knows the kit branch, adopt.sh keeps a customised mode.md, and md-blocks ignores ignored files". Notes: `docs/RELEASE_NOTES_v0.13.3.md`.

### Fixed
- `check_local.sh` (the pre-push hook): with `BASE` not set, a branch that descends from the caller's `kit_branch` is compared with `origin/<kit_branch>`, not `dev`, so a rule-24 child's bump pushes without a hand-set `BASE` or `SKIP`. An explicit `BASE` still wins; a caller whose `kit_branch` cannot be parsed fails the run (#469, feedback #462).
- `check_md_blocks.py` reads only the markdown files git knows (tracked, or new and not ignored), so a gitignored file with a broken block no longer fails the local hook while CI passes; outside a git repo it reads every `.md` as before (#79).
- `adopt.sh` keeps a `.claude/commands/mode.md` that the child changed on purpose (`kept      .claude/commands/mode.md (yours; differs from the kit copy)`), as it keeps `roadmap.json`; a file equal to an older kit copy is still updated, and `--check` says nothing new (#470, feedback #359).

## [0.13.2] - 2026-11-12
Tag `v0.13.2`, "the environments job reads CLAUDE.md from the kit branch". Notes: `docs/RELEASE_NOTES_v0.13.2.md`.

### Fixed
- The `environments` job in `checks.yml` reads `CLAUDE.md` from the caller's `kit_branch` when one is set and differs from the PR's base branch (as `rule-copies` does), so a PR into a rule-24 child's `main`, which has no `CLAUDE.md`, or into a branch with an unfilled copy, is not failed for it (#463).

## [0.13.1] - 2026-11-12
Tag `v0.13.1`, "a kit bump passes the child's pre-push hook, `--check` reads the caller's milestone, and the Desk follow-ups". Notes: `docs/RELEASE_NOTES_v0.13.1.md`.

### Fixed
- `adopt.sh --check` runs the environments test at the caller's `milestone:` and, when the caller has none, at D1 (as `checks.yml` does); a bad `milestone:` line is refused. A child with no `CLAUDE.md` now fails the environments test, unless the child carries the rule-24 kit branch elsewhere. The "gate" message says it is one test only (#452, #453).
- A kit bump passes the child's pre-push hook with no `SKIP`: `check_tdd.py` exempts a PR whose only code changes are the ShipQuick pin and the files `adopt.sh` writes (the exact list is `scripts/adopt_files.txt`, a protected path); `check_local.sh secrets` scans only the commits since `origin/<base>` (#454, #455).
- The Desk deletes its throwaway local branch on every path, names the GitHub account in the PR body, and refuses the review-only account (`.shipquick/roles.yml`) (#456, #457).

### Changed
- `docs/children.md` records the four v0.13.0 bumps, and `docs/follow-ups.md` has the row for the rule-24 `CLAUDE.md` read in `--check` (#458, #459).

## [0.13.0] - 2026-11-11
Tag `v0.13.0`, "features as switches, the Desk with working switches, and a preflight for a child's bump". Notes: `docs/RELEASE_NOTES_v0.13.0.md`.

### Added
- Feature switches (epic #86): `.shipquick/features.json` holds one on or off per ShipQuick feature; one reader (`scripts/features.py`), the owner's setter (`scripts/features.sh`), plain words per feature in `scripts/features_default.json`, rule 39 and ADR-016. `adoption` and `gate` are locked on. CI reads the flags from the base branch (the `features` job, then every gated job); `check_local.sh`, the roadmap workflow, `check_closes.py`, `close_linked_issues.py`, `mode.sh` and `review_merge.sh` read them too, and off is always the safe side (#418 to #426).
- The Desk on the approved frame D (epic #91): every feature in groups, an error card when the file is broken, owner cards, the roadmap link, and working switches. A switch opens a PR for the owner's merge through one guarded write route (same origin plus a per-start token, `features.sh set` in a throwaway worktree); the page shows "Turning off, merge PR N" until it lands (#427, #428, #430).
- `adopt.sh` preflight (#446): it writes `.shipquick/features.json` and installs the git hooks when they are configured and missing; `adopt.sh --check` also fails on uninstalled hooks, on commit subjects over 72 characters since the base, and on empty or placeholder Dev and Production links at the caller's milestone. The plugin's session-start hook warns about uninstalled hooks.
- `checks.yml` gains a `commit-subjects` job, in the gate, behind its own feature flag `commit-subjects` (default on): no commit subject over 72 characters on the PR's own commits (`check_commit_subjects.py`; Dependabot and git's exact `Revert "<subject>"` form are exempt). `check_local.sh` runs it too.
- Bench results (#312): the full kit-against-no-kit run and the vibe baseline are recorded in `docs/research/experiments.md`.

### Changed
- `close-on-merge` and `merge-gate` are read at the PR's base ref through `features.py remote`, never from the checkout; an unreadable or broken file refuses the merge (#440, #442).

### Children, read this before you bump
- New `commit-subjects` job in the gate: a PR with a commit subject over 72 characters fails. Reword it before you push, or switch the feature off (`scripts/features.sh set commit-subjects off`, a PR the owner merges). Dependabot and `Revert "..."` titles are exempt.
- `adopt.sh` now writes `.shipquick/features.json` (a protected path) and installs the git hooks. Run `adopt.sh . --check` before you push a bump branch and paste its output in the PR.
- `adopt.sh --check` now fails on uninstalled hooks, on a subject over 72 since the base, and on empty Dev or Production links past milestone D0.

## [0.12.0] - 2026-11-11
Tag `v0.12.0`, "D7: the iOS library, the live roadmap and the design checks". Notes: `docs/RELEASE_NOTES_v0.12.0.md`.

### Changed
- Children warning: after the pin bump the `adoption` job fails any child job with no `timeout-minutes`. Fix: add `timeout-minutes: 10` per job; `python3 knowledge/shipquick_latest/scripts/check_timeouts.py .github/workflows` lists them (#174).
- `check_timeouts.py` names and fails a workflow file that has zero jobs (for example a root-indented `jobs:`), instead of passing it silently (#174).
- PR checks re-run when a PR body is edited: `edited` is in the `pull_request` types of `ci.yml` and `checks.yml`, and `adopt.sh` writes it into a child's caller (#92).

### Added
- `checks.yml` gains a `story` job, in the gate: every user story a child's PR links must carry `Who does it:` (and `Done when:` for stories made from 10 Nov 2026). `adopt.sh --check` reports a caller without `issues: read` (#175).
- `checks.yml` gains a `design-tokens` job, in the gate: no colour or font literal on an added web style line, then stylelint on the changed CSS (#133).
- iOS library: a Swift contract emitter with a drift check and one generated struct per contract (#222), shared Android and iOS props in the contract core (#215), the Button Android topic follows Material 3 exactly (#223), a two-tier SwiftLint runner with a protected baseline and a fixture app (#218, #221), snapshot tests with Prefire on a pinned macOS job (#219), an XCUITest accessibility audit per template (#220).
- The six iOS catch-all modifier docs are split by control or task into 18 docs; each catch-all holds only rows no doc fits (#296).
- The live roadmap page: golden tests, times, milestones and priority in the model, timeline, You are here, the dependency map, an HTML page and Cloudflare Pages inputs (#81, #82, #83, #84).
- The ui MCP server (`scripts/ui_mcp.py`, evals in `ui/mcp/evals.xml`) and `ui/llms.txt`, so an agent can read the component library (#190).
- Design system board built from the registry (#188). Vibe tests, ten fixed screen prompts per platform, `bench/vibe.py` (#189).

### Children, read this before you bump
- The `story` job needs `issues: read` from your caller. Without it the whole ShipQuick checks run fails at startup with `The nested job 'story' is requesting 'issues: read', but is only allowed 'issues: none'`, and no gate check appears. Run `bash knowledge/shipquick_latest/scripts/adopt.sh .` after the bump to fix it. A story without `Who does it:` turns the gate red too: add the line to the issue, then re-run the job.
- Every job in a child's own workflows needs `timeout-minutes`, or the `adoption` job fails.
- `ui/llms.txt` is generated by `python3 scripts/ui_mcp.py llms`. A doc or registry change must regenerate it, or the `ui-llms` drift check fails (#190).
- The `design-tokens` job fails a PR that adds a hex, `rgb()`, `hsl()` or `font-family` literal on a web style line. Put the value in a token file, or list the file in `scripts/design_token_files.txt`.

## [0.11.1] - 2026-11-10
Tag `v0.11.1`, "a child sets its milestone". Notes: `docs/RELEASE_NOTES_v0.11.1.md`.

### Added
- `checks.yml` input `milestone` (default `D1`) for the `environments` job; `adopt.sh --milestone D0..D6` writes it into the child's caller and refuses a malformed existing line (#357, PR #358).
- Children bump notes (#356).

## [0.11.0] - 2026-11-10
Tag `v0.11.0`, "the kit measures itself and enforces at runtime". Notes: `docs/RELEASE_NOTES_v0.11.0.md`.

### Added
- Hook plugin: mode and rules at session and subagent start, codebase map, protected-path warning, scratch markdown warning, git bypass block, loop and cost guard (#313, #314, #315, #320, #321, #322).
- CI checks: rule-copy canary (#316), TDD evidence (#319), workflow security lint (#325), shortcut ledger, warn only (#327); all also in `check_local.sh`.
- Bench: selftest harness, ten tasks, cell runner, report (#311, #331, #312; the live run was cancelled by the owner).
- Review finding shape and a Verdict and Not checked gate (#317, #318); `Done when:` line for user stories (#310).
- Component-request gate and parity report (#186); `adopt.sh --platforms` (#187); `adopt.sh --check` reads the Ponytail switch (#326).
- ShipQuick Desk, localhost server and page (#307) with a spend column (#323); `scripts/release.sh` (#324); path-scoped rules spike (#328).

### Changed
- `checks.yml` gains the `rule-copies` and `component-registry` jobs, both in the gate. `adopt.sh` writes the kit rule block into a child's `CLAUDE.md`.

## [0.10.0] - 2026-11-09
Tag `v0.10.0`, "every library entry is documented". Notes: `docs/RELEASE_NOTES_v0.10.0.md`.

### Added
- Full UI coverage from each library's public API: every row of the M3 1.4.0 list (319) and the SwiftUI list (848) is covered by a structured doc field; `--strict-api` is on in CI (#231; PRs #236, #239, #255, #282, #284, #287 for Android; #241, #277-#280 for iOS).
- Own-family and own-kind rules for Android coverage; topic name clashes fail (#231).
- Framework topic docs for both platforms: widgets, notifications, pull to refresh, Swift Charts, web view and more (#231).
- Every iOS alternative of a not-on-iOS entry is checked, and a "none" needs a reason (#241).
- Child enforcement: `adopt.sh` prints a ruleset that requires the gate from the GitHub Actions app; `--check` fails when the gate is not required; the scan reports skipped private children (#260, PR #268).

### Changed
- `scripts/ui_api_lists.py` is a protected path (kit PRs only).

## [0.9.0] - 2026-11-09
Tag `v0.9.0`, "library first, and children can pin today's gates". Notes: `docs/RELEASE_NOTES_v0.9.0.md`.

### Added
- Rule 38, "Library first": `docs/COMPONENT_LIBRARY.md`, ADR-012, `docs/templates/component-request.md` (#181, PRs #193, #195, #200).
- Protected PRs need a second review and an owner yes line (#180, PR #196).
- The UI spec layer: `ui/schema/`, `ui/components/`, `scripts/check_ui_docs.py` (#182, PR #198).
- The `ui` lookup CLI: Astryx CLI pinned in `ui/tool/`, `scripts/ui.sh`, `scripts/ui_topics.py` (#183, PR #202).
- Android library: the 30 M3 components, docs and contracts in `ui/components/`, topics in `ui/integration/docs/`, 5 templates in `ui/android/` (#134, PRs #210, #212-#214).
- iOS library: the counted SwiftUI list, iOS-only docs in `ui/components/`, 5 templates and `Package.swift` in `ui/ios/` (#135, PRs #209, #211).
- Coverage gate `scripts/check_ui_coverage.py` (#216, PR #226).
- Platform-matched topics with a cross-platform leak check (#228, PRs #229, #230).
- API lists generated from M3 1.4.0 and Apple's SwiftUI data, with zero exclusions (#231, PR #233).
- `kit_branch` for rule-24 children, with kit-branch protection checks (#225, PR #227).
- Screen-render gate (#146, PR #152), story actor line (#155), CI timeouts (#154), session checker (#139), qa-loop (#162), canvas columns and publish list (#163, #165), step-flow rule (#164), options differ in copy (#148), review names board (#153).

### Fixed
- Parser hardening (#194, PR #197). Children list parse (#156, PR #166).

## [0.8.0] - 2026-11-05
Tag `v0.8.0` (cd.yml tag-check greps for this exact text, so keep it), "the kit enforces itself" (epic #130's first stories, plus the feedback inbox and environments work that led into it). Notes: `docs/RELEASE_NOTES_v0.8.0.md`.

### Added
- `docs/DESIGN_PROCESS.md` and `scripts/canvas_stage.py`, the stdlib tool that lays a design canvas out from a manifest, with `tests/test_canvas_stage.py` (#105).
- `docs/MODEL_LOAD.md` (model-load rules), `scripts/model_calls.sh --check`, `docs/research/prompt-techniques.md`, CLAUDE.md rule 32 (#107).
- The ShipQuick feedback inbox: `scripts/feedback.sh`, the nine-section template, a duplicate-issue check, and the `shipquick-feedback` skill, so a child project raises one issue here instead of a PR (#111, #118).
- Dev and production links from day one: a `## UAT on dev` checklist gate on every `dev -> main` PR (`scripts/check_uat.py`), `docs/ENVIRONMENTS.md` (#120).
- Design first: a PR touching a project's own frontend paths must name its approved board and approval date, or `scripts/check_frontend_design.sh` fails it (#121).
- Adoption is never silent: a reusable `checks.yml` with an `adoption` job, `scripts/adoption_scan.py` (daily, opens a `feedback` issue for an unwired or stale child), private-child support via `SHIPQUICK_CHILD_TOKEN` (#124).
- A release freeze is a mechanism: `scripts/freeze.sh on/off/status`, `.shipquick/freeze` as a protected path, `scripts/check_freeze.py` (#126).
- Provenance, not recency, decides a Production design board vs. a live-app disagreement: `scripts/canvas_stage.py` requires `{"board", "pr", "approved"}` on a Production board entry (#125).
- The merge gate hardened before enforcing anything new: a required `gate` status check, `scripts/protected_paths.txt` (a PR can never loosen the rules judging it), `scripts/check_adoption_ancestor.py`, `scripts/check_disable_comments.py` (#131).
- Per-role accounts and a protected mode store: `.shipquick/roles.yml` (`scripts/roles.py`, `scripts/role.sh`) names which GitHub accounts may code, review and own a project — no account name lives in any gate script; `.shipquick/mode` is a tracked, protected mode file; `mode.sh set auto` refuses when one account plays both roles (#140).

### Fixed
- `team-block` exempts Dependabot and Dependabot's bumps target `dev`, not `main` (#113).
- `review_merge.sh` counts only the latest run per check name, instead of an older stale run shadowing a fresh green one (#112).
- `scripts/freeze.sh` on/off used to switch the caller's own checkout to a new branch before checking whether there was anything to do, leaving a stray branch on a refusal; they now work in a scratch `git worktree`, and `status` reads `origin/main` instead of the local checkout (#142).

### Changed
- `pm/agile/` Definition of Done names the approved design board for a story that changes a screen.

## [0.7.0] - 2026-10-27
Tag `v0.7.0` (cd.yml tag-check greps for this exact text, so keep it), "ShipQuick is the whole protocol" (epic #97, first three stories). Notes: `docs/RELEASE_NOTES_v0.7.0.md`.

### Added
- The roles are written in the source: the coder opens every PR, dev to main too, and the reviewer never does. In Auto the reviewer merges dev to main with `scripts/review_merge.sh`; the dev to main PR title starts with `release:` (#96).
- `docs/CLAUDE.project.template.md`: what a child project fills in (stack, folders, decisions) plus one pointer line to the protocol (#99).
- `scripts/adopt.sh` puts that pointer line in the child's `CLAUDE.md`. It makes the file from the template if there is none, keeps every line of an existing one, and changes nothing on a second run (#101).

### Fixed
- The commit-message check (CI, `scripts/check_local.sh`, `scripts/check_commit_msg.py`, `COMMIT_GUIDELINES.md`) allows the `release:` type, which the release rules already use.

### Changed
- `CLAUDE.md` holds the protocol only. Rules 6, 9 and 10 were project facts and are gone. Rule numbers do not change, so those three numbers stay free (#99).

## [0.6.1] - 2026-10-27
Tag `v0.6.1` (cd.yml tag-check greps for this exact text, so keep it), a patch release of the merge gate (story #93). Notes: `docs/RELEASE_NOTES_v0.6.1.md`.

### Added
- `scripts/review_merge.sh --method squash|rebase|merge`. With no flag the gate squashes when the base branch requires linear history, and merges as before otherwise (#87).

### Fixed
- The scripts read the default branch of the repo named by `GH_REPO`, not of the current folder (#88).

## [0.6.0] - 2026-10-26
Tag `v0.6.0` (cd.yml tag-check greps for this exact text, so keep it), "Auto mode" (milestone D6, epic #66). Notes: `docs/RELEASE_NOTES_v0.6.0.md`.

### Added
- Three modes, Manual, Semi and Auto, with `scripts/mode.sh`, `/mode`, and `docs/MODES.md`. Only the owner sets the mode (#67).
- The merge gate `scripts/review_merge.sh`: in Auto, agents merge only through it (#67). It closes the linked story issues at merge time (#70).
- CI fails a PR body without `Closes #n`. Release, chore and Dependabot PRs are exempt (#70).
- `scripts/adopt.sh`: one command adopts ShipQuick in a child project (#68).
- The clone path is tested against the README, and `scripts/check_placeholders.py` lists leftover template tokens (#69).
- Parallel lanes: rule 23 allows up to 3 stacks, `merge=union` for the append-only logs, and a sprint-lanes template (#59, #64).

### Fixed
- The roadmap no longer writes "the checks checks" (#62).
- `adopt.sh` reads a single-quoted CI name, `check_closes.py` exempts Dependabot under both logins, and `check_placeholders.py` also flags the `roadmap.json` stub (#76).

## [0.5.0] - 2026-10-26
Tag `v0.5.0` (cd.yml tag-check greps for this exact text, so keep it), "Process v2" (milestone D5, epic #41). Notes: `docs/RELEASE_NOTES_v0.5.0.md`. It also carries the untagged D4 work below.

### Added
- CI must-haves: secret scan, read-only token, SHA-pinned actions with Dependabot, dependency review, local checks (#43).
- Live roadmap on GitHub Actions: a reusable workflow writes `ROADMAP.md` on a `roadmap` branch (#49).
- Rules 20 to 30 in `CLAUDE.md` and the two-session pattern in `docs/TEAM_ROSTER.md` (#42).
- PM and agile layer under `pm/agile/` (guides and templates).
- `CHANGELOG.md` and the release guide.
- Machine-enforced PR merge gates: `gate` CI job, `docs/PR_RULES.md`, `docs/PR_COVERAGE.md`, ADR-002.
- Development flow: a Mermaid diagram in the README and a plain-word walkthrough in `docs/development-flow.md`.

### Changed
- Renamed `architecture/` to `backend/`.
- CD now checks the changelog for `v*` release tags.
- PR size and file-size checks ignore renames. A moved file is not new review surface.

## [0.0.0] - skeleton
### Added
- Initial template: docs, CI, branch rules, labs.
