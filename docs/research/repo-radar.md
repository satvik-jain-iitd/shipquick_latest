# Radar log (rule 20)

One block per run. Never delete a row.

## 26 Oct 2026, story #43: secret scanning for git commits in CI
- Need: find a secret in a commit before it is merged, free, no account.
- Run: `scout.py --need "secret scanning for git commits in CI"`. The keyword search gave only unrelated repos (score 0, ignored).
- Adopted by name: `gitleaks/gitleaks`. MIT, about 30k stars, last push 23 Oct 2026, release v8.30.1 (GitHub API, tier A for the numbers).
  Named in `docs/research/ci-checks.md`.
- How it is used: the pinned Linux binary, SHA-256 checked in the `secret-scan` job, not `gitleaks-action` (that action needs a license key for
  organization accounts). Locally: `scripts/check_local.sh secrets` (`brew install gitleaks`).
- Result on this repo: full history, 38 commits, 0 findings.
- Confidence that it fits: 0.85. Test: a planted key must go red once on GitHub (shown in the PR).

## 26 Oct 2026, story #44: live roadmap page on n8n
- Need: turn GitHub issues and pull requests into one plain-words roadmap page (Vision, Delivered, Now, Next, Board), served free by n8n.
- Run: `scout.py --need "render a live project roadmap page from GitHub issues and pull requests (epics, stories, kanban board), served by n8n"` found no repos (score list empty).
  Then `gh search repos` for: `topic:roadmap topic:github-issues`, `topic:kanban topic:github-issues topic:static-site`, `github issues roadmap static page generator`,
  `n8n github issues dashboard webhook html`, `public roadmap github issues`. Only big project tools came back (plane, openproject, wekan, onedev, vibe-kanban) or nothing.
- Read: the `makeplane/plane` README (top hit). It is a whole project-management app with its own issues. We would have to move our issues into it. It does not fit.
- Also checked: the GitHub Projects roadmap view (the platform, tier A). It needs a GitHub login on the phone, shows issue titles not the plain Business line, and has no private link.
- Decision: build from scratch, small. We port GoServe `scripts/roadmap.py` (our own working code, 172 lines, same need) to JavaScript so it runs in an n8n Code node. Nothing on the Mac.
- Confidence that nothing fits: 0.75. Test: if a better tool turns up, swap only `roadmap/render.js`.

## 26 Oct 2026, story #49: live roadmap on GitHub Actions (no n8n)
- Need: a GitHub Actions workflow that turns a repo's issues and pull requests into a roadmap page, reusable by child projects, no outside tool.
- Run: `scout.py --need "GitHub Actions workflow that turns a repo's issues and PRs into a roadmap page"` found no repos.
  Then `gh search repos` for: `github action roadmap markdown issues`, `github action generate roadmap from issues`, `topic:github-actions topic:roadmap`,
  `issues to markdown action`, `roadmap generator github`, `github-issues roadmap action`, `issues export markdown github action`, `release-drafter`.
  Hits: `nektos/act`, `awesome-actions` (not tools for this), `stevefaulkner/issues-to-markdown-action` (0 stars, README is "experiment workflows1", empty), `release-drafter/release-drafter` (3.9k stars, ISC, pushed 25 Oct 2026).
- Read: `issues-to-markdown-action` README (nothing in it) and `release-drafter` README. release-drafter writes release notes from merged pull requests. It has no epics, no stories, no Now/Next, no board. It does not fit.
- Decision: build from scratch, small. Reuse our own `roadmap/render.js` (`build`, `fromGraphql`, `plain`) as the owner said; add only a Markdown writer and one reusable workflow.
- Confidence that nothing fits: 0.75. Test: if a better action turns up, swap only the writer.

## 26 Oct 2026, story #59: parallel stories with few merge conflicts
- Need: sprint lane planning and conflict-free append-only logs for parallel git branches, with nothing extra for a kit user to install.
- Run: `scout.py --need "sprint lane planning and conflict-free append-only logs for parallel git branches"` found no repos. Long search phrases returned nothing; short ones worked:
  `towncrier` (twisted/towncrier, MIT, 926 stars, pushed 9 Oct 2026), `changie` (miniscruff/changie, MIT, 920 stars, pushed 24 Oct 2026), `scriv` (nedbat/scriv, Apache, 306 stars),
  `changelog fragments` (only tiny repos), `merge driver` (Ataraxy-Labs/weave, Apache, 1334 stars; npm-merge-driver, 271 stars, last push 2021).
- Read: towncrier README (news fragments: one small file per change, so developers never write to one shared file), changie README (the same idea in Go), weave README (a semantic merge for code, per function; it is a separate install and aimed at code, not at log tables).
- Decision: use what Git already has. `merge=union` in `.gitattributes` for the three append-only logs (`docs/process-trace.md`, `docs/LEARNINGS.md`, `docs/ideas.md`): no tool, no install, works in every child project.
  Fragments (towncrier, changie) are rejected for now: they add a Python or Go tool for a kit user, and `CHANGELOG.md` is written only in the release PR, so stories do not touch it. Revisit if two stories need to edit the changelog at once.
  weave is rejected: it targets code, and it is one more tool to install.
- Open risk: GitHub's own merge button may not apply `merge=union`. Tested on 26 Oct 2026 with a throwaway pull request (branch t2 into branch t1, each added a row at the end of `docs/process-trace.md`; nothing touched dev): GitHub said `CONFLICTING / DIRTY`. After `git merge t1` on the Mac in t2 (union applied, both rows kept) and a push, GitHub said `MERGEABLE`. So GitHub ignores the attribute and Git on the Mac honours it. Throwaway PR closed, both branches deleted.
- Result: the daily rule stands (merge `dev` into every open branch with Git on the Mac), and a branch is merged with `dev` once more right before its merge if `dev` moved. Tier A for "GitHub said so" (my own run); confidence 0.85 that this holds for the other two logs (same driver, same file shape).

- Correction after the review of PR #61 (26 Oct 2026): `docs/ideas.md` is NOT on the union list. Its rows get status edits (open, taken), and two edits of one row would be kept twice with no conflict shown. The list is `docs/process-trace.md` and `docs/LEARNINGS.md`. (The Decision line above is kept as written.)

## 26 Oct 2026, story #67: three agent modes and a coded merge gate
- Need: a per-project agent autonomy mode switch, and a merge gate script for GitHub pull requests, with nothing extra to install or host.
- Run: `scout.py --need "per-project agent autonomy mode switch and a merge gate script for GitHub PRs"` found no repos. Short searches: `kodiak` (chdsbd/kodiak, AGPL-3.0, 1,116 stars, pushed 23 Oct 2026), `mergify`, `auto merge bot` (palantir/bulldozer, Apache-2.0, 812 stars, pushed 23 Oct 2026),
  `bors-ng` (1,527 stars, last push Apr 2024), `merge queue` (funador/claude-code-merge-queue, MIT, 131 stars, pushed Aug 2026; uber/submitqueue), `pr merge gate` (tiny repos).
- Read: kodiak, bulldozer and claude-code-merge-queue READMEs. Kodiak and bulldozer are GitHub Apps: they merge when checks and approvals pass, but they must be installed or self-hosted, they know nothing about our two accounts, our mode, or "approved by the review account", and Kodiak is AGPL. claude-code-merge-queue serializes local landing for parallel agents (an npm tool); it is not an approval gate and has no mode.
- Decision: build two small bash scripts (`scripts/mode.sh`, `scripts/review_merge.sh`) that use only git, gh and jq. The gate needs rules no tool has: mode is auto, approved by `satvik-jain-iitd` on the latest commit, zero open threads, every check green, `Closes #n`. A hosted app would be one more thing every child project must install.
- Confidence that nothing fits: 0.8. Test: if a kit user already runs Kodiak or bulldozer, they can skip `review_merge.sh`; the mode file still works.

## 26 Oct 2026, story #70: the pull request body must link its issue (Closes #n)
- Need: fail a pull request whose body has no `Closes #n`, with exemptions for release, sync and Dependabot pull requests, free and with no extra app.
- Run: no scout run; the need is one regular expression on text we already have in CI (the PR title, author and body come in through `github.event.pull_request`). Checked by name what exists: GitHub's own keywords close an issue only when the PR merges into the default branch, so they do not check anything; the `team-block` job already reads the PR body with `scripts/check_block.py` in this repo.
- Decision: a 20-line `scripts/check_closes.py` next to `check_block.py`, run as one more step of the `team-block` job. No new tool, no new job.
- Confidence that nothing fits better: 0.85.

## 26 Oct 2026, story #68: one command to adopt ShipQuick in a child project
- Need: one command that copies and updates a few template files into a child git repository, never overwrites the child's own files, and is safe to run twice.
- Run: `scout.py --need "one command that copies and updates template files into a child git repository"` found no repos. Short searches: `copier` (copier-org/copier, MIT, 3,658 stars, pushed 26 Oct 2026), `cruft` (cruft/cruft, MIT, 1,590 stars, last push Dec 2024), `cookiecutter` (25k stars, BSD-3, pushed Apr 2026), `template sync` (AndreasAugustin/actions-template-sync, MIT, 328 stars, a GitHub Action that opens PRs), `projen` (Apache-2.0, 2,958 stars).
- Read: copier README (renders templates from a path or Git URL, updates a project, does not overwrite unless told) and cruft README (keeps a project in step with a cookiecutter template).
- Decision: build `scripts/adopt.sh`, about 100 lines of bash. Copier is the closest fit and is the tool to switch to if the list of files grows past about ten or the child needs a three-way merge of its edits. For five files it is one more thing to install in every child (`pipx install copier`), the SHA and the child's CI name would have to be passed in as answers anyway, and the files are not templates with many variables. cruft and cookiecutter are for first-time project generation, projen owns the whole repo, and actions-template-sync needs a sync PR flow and a token.
- Confidence that adopt.sh is enough: 0.75. Revisit if a child asks to keep its own edits of a copied file.
- One more line (asked by the reviewer, 26 Oct 2026): the global skill `/shipquick-mode` (owner only, runs `mode.sh set` for him): scout found no repos. Nothing to adopt.
- Story #107 (29 Oct 2026, raised from job-search): `scripts/model_calls.sh`, a grep that lists model call sites and checks them against a table. The scout ran with "list LLM API call sites in a repo": no repos found. Built from scratch, about 20 lines of bash.

## 2026-10-29 · need: lay out design artboards from a manifest with background boards sized to content, no overlaps, state prefixes (story #105)
Runs: `scout.py --need "lay out design artboards on an infinite canvas from a manifest..."`: no repos found. GitHub search "canvas layout artboards json positions auto-layout" and `topic:auto-layout topic:canvas`: Swift UI layout libraries (EasyPeasy, Cassowary, BonMot), none for the claude.ai Design canvas format (canvas.json boards, notes, order). Built from scratch: `scripts/canvas_stage.py` (stdlib), 235 lines (listed by the reviewer).

## 30 Oct 2026, story #124: a reusable GitHub Actions workflow a child must call, with a drift check
- Need: a `workflow_call` reusable workflow a child repo calls (pinned to a commit), with a job that
  verifies the caller's pin equals the child's own submodule commit and fails CI otherwise, so
  adoption is never silent.
- Run: `scout.py --need "reusable GitHub Actions workflow (workflow_call) that a child repo calls pinned to a commit SHA, with a job that verifies the caller's pin matches a git submodule commit and fails CI otherwise"`: no repos found. GitHub search "topic:github-actions topic:reusable-workflow drift" and "submodule outdated check github action": full platforms (gitea, act) and curated lists (awesome-actions), nothing for this narrow need.
- Built from scratch: `.github/workflows/checks.yml` (reusable, mirrors the existing `roadmap.yml` two-checkout pattern already in this repo) plus `adopt.sh --check` and a scheduled registry scan. Confidence that nothing fits: 0.85.

## 30 Oct 2026, story #111: ShipQuick inbox, one-line feedback from a child project
- Need: a CLI command that opens a labelled GitHub issue in a parent repo from a child repo, as a lightweight feedback inbox.
- Run: `scout.py --need "CLI command that opens a labeled GitHub issue in a parent repo from a child repo as a lightweight feedback inbox"`: no repos found. `gh search repos "gh issue create wrapper feedback script"`: nothing. `gh search repos "topic:feedback topic:cli github-issue"`: whole feedback platforms (forem, fider), not a one-call wrapper.
- Built from scratch: `scripts/feedback.sh`, about 20 lines of bash around `gh issue create` (the project already has `gh`; this is thinner than any tool on the list).
- Confidence that nothing fits: 0.85.

## 30 Oct 2026, story #126: a release freeze that is a mechanism, not a sentence
- Need: a CLI to set/read a release-freeze flag file in a git repo (on/off/status, a reason, an
  until-date), and a merge-gate script that refuses a PR into `main` while frozen, with a stale
  freeze (past its until-date) failing loudly instead of silently lifting.
- Run: `scout.py --need "CLI to set a release freeze flag file in a git repo, with status/on/off
  and a stale-date check, used by a merge-gate script"`: no repos found. This mirrors story #120's
  `has_dev_link.sh`/`check_environments.sh` shape exactly (a flag file read through the contents
  API with `?ref=`, refused by `review_merge.sh`) — no general tool reads a repo's own flag file
  and feeds a GitHub Actions gate; freeze/change-management tools that exist (ServiceNow, Jira
  change freeze) are whole platforms, not a two-line file check.
- Decision: build `scripts/freeze.sh` (bash, mirrors `scripts/feedback.sh`'s size) + wire
  `review_merge.sh` and `checks.yml`, same contents-API pattern already proven in #120/#122.
- Confidence that nothing fits better: 0.85.

## 30 Oct 2026, story #125: provenance, not recency, decides board vs app drift
- Need: refuse to move or rewrite a Production design-canvas board from the app unless the manifest
  entry cites the PR that changed the app and its approval date (provenance over recency).
- Run: `scout.py --need "refuse to overwrite an approved design canvas board from code unless the PR
  that changed the code cites the board and its approval date, provenance over recency"`: no repos
  found. This is a one-field addition to `scripts/canvas_stage.py`'s own manifest validation (story
  #105), not a separate concern — no general tool validates provenance on a design-canvas manifest.
- Decision: extend `canvas_stage.py`'s existing refusal checks (overlap, outside-board) with one more:
  a Production `boards` entry with no `{"pr", "approved"}` is a refusal, same as any other.
- Confidence that nothing fits better: 0.85.

## 30 Oct 2026, story #131 (epic #130): harden the merge gate
- Need: a required GitHub Actions "gate" status check review_merge.sh verifies is SUCCESS, a
  protected-paths list that refuses an auto-mode merge touching CI config or lint baselines, an
  adoption-ancestor check (pinned SHA must be merged or tagged), and a disable-comment guard.
- Run: `scout.py --need "a required GitHub Actions status check named gate that review_merge.sh
  verifies is SUCCESS, plus a protected-paths list that blocks auto-merge when a PR touches CI
  config or lint baselines"`: no repos found. This is ShipQuick's own merge-gate script and its
  reusable workflow, not a general tool — a branch-protection "required status check" exists on
  GitHub itself, but review_merge.sh runs outside Actions (an agent, not GitHub, decides the merge),
  so the check still has to be read and enforced in the script.
- Decision: extend `review_merge.sh` (protected paths, required gate check) and `checks.yml`/`ci.yml`
  (gate job, disable-comment guard job); a new small stdlib script for the adoption-ancestor check
  (`scripts/check_adoption_ancestor.py`, pure logic + a thin network-calling CLI, same shape as
  `adoption_scan.py`'s injected `fetch`).
- Confidence that nothing fits better: 0.85.

## 31 Oct 2026, story #140 (epic #130): per-role accounts and a protected mode store
- Need: a per-repo file naming which GitHub accounts may code, review, and own a project, read by a
  merge-gate script that must never embed an account name itself; a sourced shell helper that exports
  the right `GH_TOKEN` for one role per session.
- Run: `scout.py --need "per-repo roles.yml listing which GitHub accounts may code vs review vs own a
  project, read by a merge-gate script, with a sourced shell helper to export the right GH_TOKEN for a
  role"`: no repos found. GitHub's own CODEOWNERS and branch protection decide who *may* approve, but
  neither drives a gate script run outside Actions, and neither can be sourced into a shell to switch
  `gh`'s active account for one role — that half is ShipQuick's own `scripts/review_merge.sh`/`mode.sh`
  concern, not a general tool's.
- Decision: a small fixed-shape parser (`scripts/roles.py`, no YAML dependency — the file never needs
  more than two keys and two lists), a sourced helper (`scripts/role.sh`), and a CI job
  (`scripts/check_roles.py`) that all read `.shipquick/roles.yml` instead of a literal account name.
- Confidence that nothing fits better: 0.85.

## 31 Oct 2026, story #146 (epic #130, GoServe feedback #146): render the screen before the gate passes
- Need: render a list of named URLs/viewports headless in CI, write PNGs, upload as a CI artifact; no
  custom baseline-diff tool needed yet (Part 3 is explicitly deferred, see PR body).
- Run: `scout.py --need "render a list of named URLs/viewports headless in CI, write PNGs, upload as a
  CI artifact, optional baseline diff against committed images"`: no repos found. The issue itself
  names the right tool (Tier A, the tool's own docs, confidence 0.9): Playwright already ships a
  `screenshot` CLI command (`npx playwright screenshot --viewport-size=WxH <url> <file>`) and
  `toHaveScreenshot()` for baselines. GoServe (the project that filed this) already has Playwright
  installed. ShipQuick itself has no frontend of its own and must not bundle Playwright as its own
  dependency; `scripts/screens.sh` only orchestrates a project's own already-installed `npx playwright`,
  the same way `scripts/check_frontend_design.sh` only ever reads a project's own config, never ships a
  renderer.
- Decision: `scripts/screens.sh` (reads `docs/screens.txt`, calls the project's own `npx playwright
  screenshot`, skips when unconfigured -- same opt-in shape as `docs/frontend-paths.txt`); a `Render:`
  line requirement added to `scripts/check_frontend_design.sh`, opt-in on the same file existing.
- Confidence that nothing fits better: 0.85.

## 9 Nov 2026, story #155 (GoServe feedback #155): a story names who does it
- Need: fail a story issue that has no "who does it" line (actor, app or screen, how often).
- Run: `scout.py --need "lint a GitHub issue body for a required user-story actor field"`: no repos found.
  `scout.py --need "issue template required field checker"`: one unrelated repo (score 0, ignore).
  `gh search repos --topic issue-form`: one browser form generator, not a checker.
- Decision: reuse GitHub's own issue form (`required: true` on a new field) for stories made in the UI,
  and a small `scripts/check_story.py` for stories made with `gh issue create --body` (agents do this,
  and it skips the form). It reuses the `LINK` regex of `close_linked_issues.py`.

## 9 Nov 2026, story #153 and #161 (epic #130): the approval says the render matches the board
- Need: a merge gate that reads the approving review body and checks it says the screenshot was compared
  with the named design board.
- Run: `scout.py --need "merge gate that checks a pull request approval review body says the screenshot
  matches the design"`: no repos found. Visual review tools (Chromatic, Percy) compare a build with an
  older build, not with the design, which is the gap #161 names.
- Decision: a small `scripts/check_design_reviewed.py` (pure `check()` + CLI, the `check_closes.py`
  shape), called from `scripts/review_merge.sh` on the review it already resolves. #161's build rule is
  text (DESIGN_PROCESS.md, SCREENS.md, the PR template); the approval line is its machine check.
- Confidence that nothing fits better: 0.8.
## 9 Nov 2026, story #163 (GoServe feedback): publish the canvas from canvas.json, then verify the listing
- Need: derive the exact list of files to publish from a JSON manifest, and check a deploy listing holds every file it names.
- Run: `scout.py --need "derive the exact list of files to publish from a JSON manifest and verify a deploy listing contains every referenced asset"`: no repos found.
- The idea is old and plain (a bundler's asset manifest read by the deploy step; a link check after a static-site deploy). It is a set difference. A tool for it would be bigger than the code.
- Decision: two modes in `scripts/canvas_stage.py` (`--publish-list`, `--verify <listing>`), about 15 lines, standard library only.
- Confidence that nothing fits better: 0.9.

## 9 Nov 2026, story #165 (GoServe feedback): stages as columns, and a Design learnings board
- Need: lay out design canvas stage sections as kanban columns, left to right, and render a design decision log board from JSON.
- Run: `scout.py --need "lay out design canvas stage sections as kanban columns left to right and render a design decision log board from json"`: no repos found.
- Kanban tools (Trello, Jira, GitHub Projects) show the idea; none writes boards for the claude.ai Design canvas. The layout is one x offset in the existing loop.
- Decision: a `"layout": "columns"` key and a learnings board inside `scripts/canvas_stage.py`, reusing its board template and contrast check.
- Confidence that nothing fits better: 0.85.

## 9 Nov 2026, story #148 (GoServe feedback): options differ in copy, rejections carry a reason
- Need: lint a design options manifest so each option names its copy difference and each rejected option carries a reason.
- Run: `scout.py --need "lint a design options manifest so each option names its copy difference and each rejected option carries a reason"`: no repos found.
- Content-design guides exist (Material 3 content design, Shopify Polaris content; Tier A, the vendors' own docs). They are rules to read, not a check to run.
- Decision: two checks in the existing manifest loop of `scripts/canvas_stage.py`, read from the manifest only, no render.
- Confidence that nothing fits better: 0.85.

## 9 Nov 2026, story #162: a QA loop with a design audit and the Elephant-Goldfish model
- Need: tools for a QA loop over an app's approved screens: a scorecard (attack yield, coverage debt,
  escapes, stop rule), a flow map of every tap, a design-audit report with highlight boxes, a board render.
- Run: `scout.py --need "QA loop scorecard flow map design audit report for app screens with elephant
  goldfish review"`: no repos found. `scout.py --need "exploratory QA skill for coding agents with bug
  taxonomy"`: no repos found. `gh search repos --topic exploratory-testing`: top 3 READMEs read:
  `srbarrios/agentic-test-explorer` (LangGraph swarm drives a browser, writes Playwright repros; web only),
  `willcoliveira/qualiow-exploratory-testing-skills` (Claude Code skills, web plus iOS and Android through
  a Maestro shim), `loukan42/chaosfolk` (simulated users, replayable browser evidence; web only).
  Also checked: `google/elephant-goldfish-model` (Apache-2.0, pushed 8 Nov 2026, about 15k stars) and
  `garrytan/gstack` `/qa` (MIT, pushed 9 Nov 2026).
- Decision: none of them compares the app with the design, keeps an escape log, or writes a design audit
  as a roadmap. So the kit takes the owner's own `qa-loop` skill (already written, already used) and makes
  it generic. EGM is used as is for plans (adopt, never fork). `qualiow` is named in `docs/QA_LOOP.md` as
  the mobile probe driver to borrow. gstack's issue taxonomy shaped the severity list.

## 9 Nov 2026, story #154: every workflow job has a time limit
- Need: fail CI when a GitHub Actions job has no `timeout-minutes`.
- Run: `scout.py --need "lint GitHub Actions workflows: fail when a job has no timeout-minutes"` and
  `scout.py --need "github actions workflow linter timeout"`: no repos found. `gh search repos "topic:github-actions linter"`:
  act, gitea, ruff, shellcheck; none checks job timeouts. actionlint checks syntax and expressions, not a missing limit.
- Decision: a 40-line stdlib checker, `scripts/check_timeouts.py` (no YAML dependency, since CI installs only pytest).
- Confidence that nothing fits better: 0.75.

## 9 Nov 2026, story #139 (ADR-011): maker and checker are different sessions
- Need: enforce that the agent session that wrote a PR's commits cannot approve it.
- Run: `scout.py --need "enforce maker checker: the agent session that wrote commits cannot approve the pull request"`:
  no repos found. `gh search repos topic:four-eyes-principle` and `topic:segregation-of-duties`: a PR-workflow demo
  (cakarci/pull-request-workflow) and SAP/IAM audit tools; none knows about agent sessions on one account.
  GitHub's own "require review from someone other than the last pusher" sees accounts only (Tier A, 0.85).
- Decision: a `Built-by:` commit trailer written by `git interpret-trailers` (git's own tool, no new dependency),
  checked by the existing `check_roles.py` and `review_merge.sh`.
- Confidence that nothing fits better: 0.8.

## 9 Nov 2026, story #182 (S2): the spec layer (component doc schema, contracts, doc guards, tokens)
- Need: one doc schema and one cross-platform contract per component, plus a check that fails when a doc
  names a prop the contract lacks or hides an enum's literal values.
- Run: `scout.py --need "component documentation schema and doc guard: fail when a component doc names a prop
  the cross-platform contract lacks or hides literal union values"` and `scout.py --need "design system
  component docs schema for AI agents"`: no repos found. `gh search repos "topic:design-tokens topic:schema"`:
  VoltAgent/awesome-design-md (a list), chakra-ui/panda, system-ui/theme-ui, Manavarya09/design-extract
  (DTCG token extraction); none has a per-component doc schema with a native contract.
- Top READMEs read: `meta/astryx` (MIT, pushed 9 Nov 2026, commit `86a32152f4ed`), its `packages/native`
  README (contracts: core, per-platform, web-only with reason), and design-extract (DTCG tokens, multi-platform emitters).
- Decision: copy Astryx's doc types, contract types and dense guide (ADR-012, rule 38; files and commit in
  `ui/UPSTREAM.md`). Its guards (`docPropReferences`, `docPropLiterals`) read TypeScript sources we do not have,
  so `scripts/check_ui_docs.py` re-applies their two ideas against our JSON contracts (stdlib). Tokens use the
  W3C Design Tokens format (`$value`, `$type`), the one the emitters in S6 already read.
- Confidence that nothing fits better: 0.8.

## 9 Nov 2026, story #183 (S3): run Meta's Astryx CLI for the kit's components
- Need: one lookup CLI agents run before UI work (`component`, `docs`, `--dense`, `--json`, `init` agent block, `doctor`), for web, Android and iOS.
- Run: the plan already names the source, Meta's Astryx (`meta/astryx`, MIT, read in S2). No other tool has a managed agent block
  plus dense docs. Read at tag `v0.7.11`: `packages/cli/README.md` and `authoring/integration/type.ts` (Tier A, the vendor's own code, 0.9).
- Finding: the CLI is built to be extended. An `astryx.integration.*` manifest adds `docs`, `templates`, `agentDocs.append`.
  So we use it, not copy it. Three spikes on the owner's Mac: needs core installed; `component` needs a React source file; reference topics work.
- Decision: pin `@astryxdesign/cli` and `core` `0.7.11` in `ui/tool/`; native parts as generated topics; a fail-closed wrapper.
- Confidence that nothing fits better: 0.85.

## 9 Nov 2026, story #135 (S5): the iOS library (counted SwiftUI list, iOS-only docs, five templates)
- Need: the list of Apple's standard iOS components with their exact SwiftUI types, and screen templates built only from them.
- Run: `scout.py --need "list of standard SwiftUI components mapped to Apple HIG, and SwiftUI screen templates using only
  standard controls"`: no repos found. `gh search repos "topic:swiftui topic:design-system"`: jaywcjlove/awesome-mac and
  dkhamsing/open-source-ios-apps (lists), jordanbaird/Ice and CodeEditApp/CodeEdit (macOS apps), NativeScript (a cross-platform
  runtime); none is a component list or a template set.
- Source used instead: Apple's own SwiftUI and HIG docs (Tier A, the vendor, 0.9), read as the JSON the pages render.
  Rule 38 says to use SwiftUI as Apple ships it, so there is nothing to adopt; the docs only point at Apple's parts.
- Decision: `docs/research/ios-swiftui-components.md` (33 counted), 12 iOS-only docs in `ui/components/`, templates in
  `ui/ios/templates/` from standard controls only. No package added.
- Confidence that nothing fits better: 0.85.
## 9 Nov 2026, story #134 (S4): the Android library (Compose Material 3 docs and screen templates)
- Need: one doc and contract per Material 3 component, and five Compose screen templates built only from M3 parts.
- Run: `scout.py --need "Jetpack Compose Material 3 component catalog with per-component docs and screen templates"`: no repos found.
  `gh search repos "topic:jetpack-compose topic:material3"`: gkd-kit/gkd and JunkFood02/Seal (apps, not libraries),
  android/compose-samples and android/nowinandroid (Google's own samples).
- Top READMEs read: android/compose-samples (Jetnews, Jetchat, Reply: M3 apps, Tier A), android/nowinandroid
  (one app built with Compose, "follows Android design and development best practices", Tier A), gkd-kit/gkd (not a fit).
- Decision: the source is Google's own Material 3, used as shipped (rule 38). Nothing is copied: the docs restate
  Google's pages (`docs/research/android-m3-components.md`), and the templates call M3 composables the way Google's guides show.
- Confidence that nothing fits better: 0.9 (the library is Google's, so there is nothing to find beyond it).

## 9 Nov 2026, story #225: read the kit pin from a kit branch (rule-24 children)
- Need: read a git submodule pin and config files from another branch in a CI adoption check.
- Run: `scout.py --need "read a git submodule pin and config files from another branch in a CI adoption check (git show branch:path)"`:
  no repos found. `gh search repos "topic:git-submodules"`: junhoyeo/vercel-submodules (fetches private submodules at Vercel
  deploy), sgoudham/update-git-submodules (an Action that bumps submodules to the latest tag), roehling/git-archive-all
  (archives a repo with its submodules). READMEs read; none checks a pin on another branch.
- Decision: no tool. Plain git does it: `git fetch origin <b>`, `git rev-parse <b>:knowledge/shipquick_latest`,
  `git show <b>:.pre-commit-config.yaml`; the scan uses the GitHub contents API (`type: submodule`, `sha`). Built from scratch.
- Confidence that nothing fits better: 0.85.
## 9 Nov 2026, story #216: the UI coverage gate (every counted component has a doc, a contract and a topic)
- Need: check that every row of a counted component list has one doc, one contract and one served topic, and that no name we serve shadows a core doc.
- Run: `scout.py --need "check that every component in a counted design-system list has a doc, a contract and a served topic, and no name shadows the upstream library"`: no repos found.
  `scout.py --need "design system component documentation coverage check"`: no repos found.
  `gh search repos "topic:design-system documentation coverage"`: system-design-primer, FreeDomain, the-art-of-command-line,
  VoltAgent/awesome-design-md, Leonxlnx/taste-skill (none check coverage). `gh search repos "storybook coverage"`: small demos.
- Top READMEs read: yannbf/storybook-coverage-recipes (code coverage of rendered stories, not doc coverage),
  tomnar/storybook-coverage (a Chromatic Angular template), VoltAgent/awesome-design-md (a list of DESIGN.md files). Not a fit.
- Decision: build from scratch, about 100 lines of stdlib Python. It reuses `read_doc` from `scripts/check_ui_docs.py`
  and reads the same tables the S4 and S5 tests read. No package added.
- Confidence that nothing fits better: 0.8 (the input is our own two tables, so a general tool would still need this glue).

## 9 Nov 2026, story #228: per-platform usage text in one shared component doc
- Need: one shared component doc with usage text per platform, and a check that a platform topic never names the other platform's API.
- Run: `scout.py --need "keep one shared component doc with per-platform usage text and fail when a platform reference topic names another platform's API (Compose vs SwiftUI)"`: no repos found.
  `scout.py --need "cross-platform design system docs with per-platform usage guidelines android ios"`: no repos found.
  `gh search repos --topic=design-system --topic=compose --topic=swiftui`: none. `--topic=design-system --topic=multiplatform`: one app (mrfatworm/ZZZ-Archive) and one React library; not a fit.
- Read instead: our upstream, meta/astryx `packages/cli/authoring/doctypes/component/type.ts` at the pinned commit (`ui/UPSTREAM.md`).
  Its `UsageDoc` has one text for the whole component and no per-platform field, so there is nothing there to adopt.
- Decision: build from scratch, small. One optional field `platformUsage` in our copy of the doc type, with the same
  fields as upstream's `UsageDoc` (`description`, `bestPractices`, `accessibility`), so it reads like upstream. The leak
  check is about 10 lines of stdlib regex in `scripts/ui_topics.py`. No package added.
- Confidence that nothing fits better: 0.8 (the split is about our own two-platform docs; a general tool would still need this glue).

## 9 Nov 2026, story #231: generate the full UI lists from each library's public API
- Need: parse a Jetpack Compose `api/current.txt` dump and Apple's DocC documentation JSON into lists of public UI components.
- Run: `scout.py --need "parse a Jetpack Compose api current.txt dump and Apple DocC documentation JSON into lists of public UI components"`: no repos found.
  `scout.py --need "parse Apple DocC documentation JSON symbol graph"`: no repos found.
  `gh search repos --topic=docc`: DoccZz/docc2html, tayloraswift/swift-biome, and others not a fit. `gh search repos "docc json"`: thehammer/callimachus-adapter-docs.
  `gh search repos "metalava api current.txt parser"`: none.
- Read: the top 3 READMEs. docc2html turns a DocC archive into HTML (Swift, a whole site). swift-biome is superseded
  by swift-unidoc and compiles symbol graphs into a docs server. callimachus-adapter-docs indexes DocC JSON into its own
  knowledge store. None lists View conformers with iOS availability, and none reads a Compose API dump.
- Borrowed: the callimachus idea of reading `metadata.symbolKind` and the relationship sections of each DocC page
  (we read `conformingTypes` on the `View` page and `metadata.platforms` on each type's page).
- Decision: build from scratch, about 300 lines of stdlib Python (`scripts/ui_api_lists.py`). No package added.
- Confidence that nothing fits better: 0.8 (both inputs are vendor formats with no maintained parser for this job).

## 9 Nov 2026, story #260: make a status check required on child repos and report the ones missing it
- Need: require a GitHub status check on a child repo's default branch and report repos missing it.
- Run: `scout.py --need "require a GitHub status check on a child repo's default branch and report repos missing it"`: no repos found.
  `gh search repos --topic=branch-protection --sort=stars`: conventional-branch/conventional-branch, cloudposse/github-status-updater,
  kunwarVivek/mcp-github-project-manager, warestack/watchflow, benjefferies/branch-protection-bot.
- Read: the top 3 that fit. github-status-updater (Go CLI) sets commit statuses and can turn on required checks with the
  classic protection API; one call we can make with `gh api` ourselves. watchflow is a GitHub App rule engine that posts its
  own check runs; it replaces our gate, it does not require it. branch-protection-bot toggles "include administrators"; not a fit.
- Borrowed: the idea from github-status-updater of one call that turns on the required check. We use a ruleset instead of
  the classic PUT, so existing protection and its other checks stay.
- Decision: about 40 lines added to `scripts/kit_branch.py` (stdlib), reusing its `gh api` protection read. No package added.
- Confidence that nothing fits better: 0.8 (the job is two GitHub API calls; any tool would still need our gate name).

## 9 Nov 2026, story #242: offline vendor backup of npm and Maven dependencies
- Need: keep an offline, checksummed copy of the pinned npm tarballs and Compose Maven artifacts, and prove a restore with no registry.
- Run: `scout.py --need "offline vendor backup of npm and maven dependencies"`: no repos found.
  `gh search repos "offline maven npm mirror vendoring"`: none. `--topic=npm-mirror` and `--topic=offline-mirror`: shrinkpack
  (JamieMason), netdoctor-ir, a few site mirrors.
- Read: shrinkpack stores npm tarballs in the repo and installs offline; it is old (npm 5 era), npm only, no Maven. netdoctor-ir
  switches mirrors; it keeps no copy. The Gradle docs describe a local file Maven repository with `--offline`; no tool needed.
- Borrowed: shrinkpack's idea of keeping the tarballs and checking them against the lockfile integrity. npm's own cache does the
  same today (`npm ci --offline --cache`), so we use that. Maven side: a plain folder in Maven layout.
- Decision: about 300 lines, `scripts/vendor_backup.py` (stdlib) and `scripts/restore_vendor.sh`; npm and Gradle do the installing.
- Confidence that nothing fits better: 0.8.
## 9 Nov 2026, story #217: prove every contract prop compiles against Compose Material 3 and SwiftUI
- Need: generate a compile-only proof that every UI component contract prop exists in Jetpack Compose Material 3 and SwiftUI, checked in CI.
- Run: `scout.py --need "generate a compile-only proof that every UI component contract prop exists in Jetpack Compose Material 3 and SwiftUI, checked in CI"`: no repos found.
  `scout.py --need "compose api compatibility check"`: no repos found.
  `gh search repos "compose material3 api check"`: none. `gh search repos "swiftui api compile test"`: none.
  `gh search repos "topic:binary-compatibility kotlin"`: JetBrains/kotlin and unrelated apps, not a fit.
- Read: no repo fits, so no README fits the job. The tools that do exist (Kotlin's binary-compatibility-validator, metalava)
  check that a library keeps its own API; they do not check that our docs name a real API.
- Borrowed: the compiler itself is the checker. Gradle, the Android Gradle Plugin, Kotlin and Xcode are the vendors' own tools
  (owner yes on #217, 9 Nov 2026), pinned exactly and run on GitHub CI only.
- Decision: build from scratch, about 300 lines of stdlib Python (`scripts/ui_proof.py`) that writes the two proof files.
  No package added to the repo.
- Confidence that nothing fits better: 0.8 (the contracts are our own format; any tool would still need this glue).

## 9 Nov 2026, story #185: lint that refuses hand-drawn UI in a child
- Need: detekt SwiftLint forbid hand-drawn UI.
- Run: `scout.py --need "detekt SwiftLint forbid hand-drawn UI"`: no repos found.
  Read instead: detekt (`ForbiddenImport`), Konsist (`LemonAppDev/konsist`) and SwiftLint (`realm/SwiftLint`, `custom_rules`).
  The owner said yes to all three on #185 ("Haan, teeno", 9 Nov 2026).
- Borrowed: all three are used as they are, pinned exactly (detekt 1.23.8, Konsist 0.17.3, SwiftLint 0.65.1) and run on GitHub CI only.
  No custom detekt rule module. The rules are config and one Kotlin test file.
- Decision: no new tool. We write two configs, one Konsist test, two fixture apps and a drift test (stdlib Python).
- Confidence that nothing fits better: 0.8 (the three tools are the usual choice for Compose and SwiftUI; no repo does both).
## 9 Nov 2026, story #184: one tokens.json to a Compose Theme and SwiftUI Tokens
- Need: turn `design/tokens.json` into a Compose Material 3 `Theme.kt` and a SwiftUI `Tokens.swift`, checked in CI.
- Run: `scout.py --need "design tokens json to Compose Theme and SwiftUI Tokens"`: no repos found.
  `gh search repos "style-dictionary"`: style-dictionary/style-dictionary (about 4.9k stars, pushed 3 Nov 2026).
  `gh search repos "design tokens compose swiftui"`: none.
- Read: Style Dictionary is a Node tool. It needs `npm install` and a custom format per target, written by us: one for
  Compose Material 3 roles and one for SwiftUI. Its stock Android and iOS formats write XML and Objective-C style output,
  not `ColorScheme`, `Typography` or SwiftUI `Color`. Meta's Astryx has a Swift theme emitter
  (`packages/native/scripts/swift-ios-theme.mjs`, 839 lines, v0.7.11). It reads CSS custom properties resolved from
  `defineTheme`, not W3C tokens, so it does not fit. Borrowed ideas only: a generated-file header that names the command,
  the output committed, a test that fails on drift, and a check for reserved words in names. No file was copied.
- Decision: build from scratch, one stdlib Python file (`scripts/emit_tokens.py`), the same shape as `scripts/ui_proof.py`.
  It runs on CI with no install, and the output is the part that needs our own mapping anyway.
- Confidence that nothing fits better: 0.75 (Style Dictionary would save the JSON walk, but not the mapping, and adds Node).
## 9 Nov 2026, story #288: save the public names of each framework package
- Need: save a list of public API names of Android and Apple framework packages to validate names in docs.
- Run: `scout.py --need "save a list of public API names of Android and Apple framework packages to validate names in docs"`: no repos found.
  `gh search repos "android api current.txt"`: none. `gh search repos --topic=docc`: DoccZz/docc2html, tayloraswift/swift-biome,
  JosephDuffy/VaporDocC (and two not a fit).
- Read: the top 3 READMEs. docc2html builds a static site from a DocC archive. swift-biome serves many Swift packages'
  docs (superseded by swift-unidoc). VaporDocC serves a DocC archive from a Vapor app. None saves a name list we can check against.
- Borrowed: nothing new. We reuse our own `scripts/ui_api_lists.py` (its `get`, `sha`, current.txt regexes and the Apple JSON reading).
- Decision: about 90 lines added to `scripts/ui_api_lists.py` and 30 to `scripts/check_ui_coverage.py` (stdlib). No package added.
- Confidence that nothing fits better: 0.8 (the job is our own glue on two vendor formats we already parse).

## 9 Nov 2026, story #285: an own-family rule for iOS docs
- Need: enforce that each API row is documented only in the doc of its own family, mapping SwiftUI modifiers to component docs.
- Run: `scout.py --need "enforce that each API row is documented only in the doc of its own family, mapping SwiftUI modifiers to component docs"`: no repos found.
  `gh search repos "swiftui modifiers list"`: none. `gh search repos "swiftui modifiers" --sort stars`: superwall/iOS-Backports,
  Aeastr/AdaptiveDimensions, ngimelliUW/WiggleAnimationModifier (and two more single-modifier packages).
- Read: the top 3 READMEs. iOS-Backports adds a `.backport` wrapper for new modifiers. AdaptiveDimensions scales sizes with text
  size. WiggleAnimationModifier adds one animation. Each is a modifier to use in an app, not a catalog or a gate.
- Borrowed: nothing. We reuse our own Android rule in `scripts/check_ui_coverage.py` (PR #255) and the generated list.
- Decision: a `Doc family` column from `scripts/ui_api_lists.py` (one map, `IOS_DOC_FAMILY`) and about 20 lines in the gate. No package added.
- Confidence that nothing fits better: 0.85 (the rule is about our own docs and our own list).

## 10 Nov 2026, story #186: the component-request gate
- Need: check that a GitHub issue has an owner-yes comment and an approval label, both by a reviewer account, before a custom component merges.
- Run: `scout.py --need "check a GitHub issue has an approval label and an approval comment by an allowed account before merge"`: one repo, score 0, ignore (a list, no licence, dead 2004 days).
  `gh search repos --topic=approval-gate`: agentveil-sdk, renezander030/agent-approval-gate, herdr-telegram-gate. All are runtime approval for AI agents, not a GitHub issue check.
- Read: the top 3 READMEs. agent-approval-gate is a draft-validate-approve pattern with n8n and email. agentveil-sdk guards agent actions at run time. herdr-telegram-gate sends Telegram approve cards. None reads issue comments and label events.
- Borrowed: nothing; the idea of a recorded approval step is already our rule 38.
- Decision: build from scratch, about 100 lines of stdlib Python (`scripts/check_component_request.py`), calling `gh api` for issue events and comments.
- Confidence that nothing fits better: 0.8.
## 10 Nov 2026, story #91 (epic ShipQuick Desk): localhost dashboard for one repo
- Need: a localhost dashboard for one GitHub repo that shows issues, PRs, decisions waiting for the owner and the roadmap, refreshed on a timer, with no server beyond the stdlib.
- Run: `scout.py --need "localhost dashboard for one GitHub repo: issues, PRs, decisions waiting for the owner, roadmap, refreshed on a timer, no server beyond the stdlib"` found no repos (empty list).
  Then `gh search repos --topic github-dashboard --sort stars -L 10`. Top hits: `javiertuya/dashgit`, `AKharytonchyk/git-pull-request-dashboard`, `imhamiddev/GitHub-monitor`, then unrelated small repos.
- Read (top 3 READMEs, GitHub API, tier A for what the repo says, tier C for its own claims):
  - `javiertuya/dashgit`: browser-only dashboard for many repos and GitLab, hosted on GitHub Pages. Has `dashgit-server-py/server.py`, a stdlib Python server on 127.0.0.1:8080, no Docker, no Node. Tokens kept in browser storage. Multi-repo, so too broad.
  - `AKharytonchyk/git-pull-request-dashboard`: multi-org PR and issue view with a PAT in the browser, GitHub Pages demo. Built for many repos, not one repo's decisions and roadmap. Does not fit.
  - `imhamiddev/GitHub-monitor`: Next.js 15 SaaS with a database and GitHub App auth. Far too heavy for a localhost page. Does not fit.
- Borrowed: the idea of a stdlib Python server bound to 127.0.0.1 (from dashgit `server.py`). Our roadmap engine is reused as is: `roadmap/roadmap.js` and `roadmap/query.graphql`.
- Verdict: nothing fits the need (one repo, decisions waiting, roadmap). Build from scratch, small, on top of the existing roadmap engine.
- Confidence that nothing fits: 0.8. Test: the design doc's Option A and B each get a spike; if a tool turns up that covers one repo's decisions, swap the page only.

## 10 Nov 2026, story #310 (A0): the Done when line and the size warning
- Need: fail a user story issue with no `Done when:` line, and warn on size M, L or XL labels.
- Run: `scout.py --need "fail a GitHub user story issue with no Done when line and warn on size M L XL labels"`: no repos found.
  `gh search repos "github issue template size story checker"`: no fit for a check on an existing issue label set.
- Read: none to read; the search gave no repo that checks story issues.
- Decision: extend `scripts/check_story.py` (the story-shape check of #155). No new tool: the same issue read, the same skip rule for old stories.
- Confidence that nothing fits better: 0.7 (a narrow ShipQuick rule; the search was thin).
- Study of Ponytail and ECC (the epic's source, read in full by the reviewer, 10 Nov 2026): `docs/research/2026-11-10-ponytail-ecc-study.md`.

## 10 Nov 2026, story #327: shortcut ledger for ponytail and shortcut comments
- Need: list every `shortcut:` or `ponytail:` comment in tracked source, tag the ones with no upgrade trigger, log them once to a follow-ups table.
- Run: `scout.py --need "find shortcut or ponytail debt comments in a repo that lack an upgrade trigger, and log them"` returned "no repos found". `gh search repos "todo comment tracker missing trigger lint"` returned no rows. Thin search: no read of READMEs (nothing to read).
- Decision: build from scratch in `scripts/check_shortcuts.py` (stdlib, about 100 lines). Nothing found fits: the ponytail kit's `ponytail-debt` skill is the idea source (study in `docs/research/2026-11-10-ponytail-ecc-study.md`, row A11), not a script to call.
- Confidence that nothing fits better: 0.5 (the search was thin; a broader search could still find a lint for TODO comments).
## 10 Nov 2026, story #325 (A7): workflow security lint
- Need: a stdlib check that fails a GitHub Actions workflow which checks out the PR head under pull_request_target or workflow_run, or runs npm ci or npm install without --ignore-scripts.
- Run: `scout.py --need "lint GitHub Actions workflows for pull_request_target or workflow_run checkouts of untrusted PR head and npm install without ignore-scripts"` found no repos. Then `gh search repos "github actions workflow security linter pull_request_target"` and `topic:github-actions-security`.
- Read the top 3 READMEs that fit the need:
  - `praetorian-inc/trajan` (Apache-2.0, Go, about 200 stars, pushed 2 Nov 2026): a full CI/CD scanner for GitHub, GitLab and Azure. Broad, needs a Go binary or an Action. Does not fit a stdlib check run in CI and in check_local. Idea noted, not copied.
  - `indoor47/gh-workflow-hardener` (MIT, Python, about 13 stars, last push 28 Feb 2026): pin-by-SHA, permissions and script injection scan. Its scope is wider and it is a pip install. Does not check the head-checkout rule or npm install scripts. Idea noted (rule shape: one finding per line with file and line).
  - `eliottreich/taskbounty-check` (about 2 stars, last push 21 Jun 2026): npm package, tied to a hosted review offer. Does not fit.
- Decision: build from scratch, small (about 150 lines, stdlib, no install). Nothing found covers the two exact rules. Confidence that nothing fits: 0.8. Test: fixtures give exit 1, exit 1, exit 0, and the repo's own workflows pass.
## 10 Nov 2026, story #319 (A15): the TDD evidence check
- Need: fail a PR that changes code when its body has no `## Red` section, or names a test file that is not in the PR diff.
- Run: `scout.py --need "fail a pull request whose body has no Red test section, or names a test file that is not in the PR diff (TDD evidence check in CI)"`: no repos found. `gh search repos "pull request body check tdd red test"`: no results. Thin search, said so.
- Read: none; no repo came back to read.
- Decision: build `scripts/check_tdd.py` from scratch (stdlib). It reuses the shape of `scripts/check_story.py` (PR body in, reason out) and the diff rule of the pr-size check. Nothing found fits a `## Red` body rule.
- Confidence that nothing fits: 0.6 (the search was thin; a narrow ShipQuick rule).
---
## 10 Nov 2026, story #313 (A2): hook plugin, rules reach every session and subagent
- Need: a Claude Code plugin whose SessionStart and SubagentStart hooks inject a dense rules file and the mode into every session and subagent.
- Run: `scout.py --need "Claude Code plugin with SessionStart and SubagentStart hooks that inject a dense rules file and a codebase map into every session and subagent"`: no repos found.
  `gh search repos "claude code hooks SessionStart SubagentStart plugin"`: no results.
  `gh search repos "topic:claude-code-plugin hooks"`: DietrichGebert/ponytail (MIT, pushed 29 Oct 2026), thedotmack/claude-mem (memory, not rules), wshobson/agents (plugin packs, no runtime rule injection).
- Read: ponytail `.claude-plugin/plugin.json`, `hooks/claude-codex-hooks.json`, `hooks/ponytail-subagent.js`, `hooks/ponytail-map.js` (study clone, read only).
- Decision: adopt ponytail's hook layout (SessionStart + SubagentStart, `hookSpecificOutput.additionalContext`, one hook per script). Rewrite in stdlib Python, the kit's language, with a rules file generated from CLAUDE.md. Ponytail's map and loop guard are later stories (A9, A12).
## 10 Nov 2026, story #331 (A1a-2): bench cell runner and --rescore
- Need: a headless `claude -p` runner per task and arm, with a timeout tree-kill and an offline rescore.
- Run: `scout.py --need "headless claude -p benchmark runner per task and arm with fake claude test and offline rescore"`: no repos found.
  `gh search repos "claude code benchmark harness headless claude -p arms"`: no results.
- Read: ponytail `benchmarks/agentic/run.py` (`run_cell`, `_kill_group` via process group, stdout to file, `rescore`), study clone, read only.
- Decision: adopt ponytail's cell pattern (stdout to a file, `start_new_session`, group kill on timeout, logs outside the scored folder). Written for the kit's bench with stdlib only; the ponytail fixtures, plugin arms and cache warm-up are not borrowed (ShipQuick has no plugin arms yet).
- Confidence that nothing fits better: 0.7 (the search is thin; ponytail is the only close fit).

---
## 10 Nov 2026, story #312 (A1b): bench report, stats and docs
- Need: a report on bench results: median per task, kit divided by no-kit, geometric mean over tasks, 95% bootstrap interval, as a markdown table.
- Run: `scout.py --need "bootstrap confidence interval geometric mean ratio report for LLM benchmark arms"`: no repos found. The GitHub search was not repeated: the same need ran in #331 with no fit.
- Read: ponytail `benchmarks/agentic/compare.py` and `run.py` (study clone, read only): per-task median, a sign test over pairs, no bootstrap and no geometric mean.
- Decision: write `bench/report.py` (stdlib: `statistics`, `random` with a fixed seed). Borrow the idea of per-task medians; the ratio, geometric mean and bootstrap are not in ponytail.
- Confidence that nothing fits better: 0.7 (thin search; the stats are a few lines of stdlib).
