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

## 9 Nov 2026, story #139 (ADR-011): maker and checker are different sessions
- Need: enforce that the agent session that wrote a PR's commits cannot approve it.
- Run: `scout.py --need "enforce maker checker: the agent session that wrote commits cannot approve the pull request"`:
  no repos found. `gh search repos topic:four-eyes-principle` and `topic:segregation-of-duties`: a PR-workflow demo
  (cakarci/pull-request-workflow) and SAP/IAM audit tools; none knows about agent sessions on one account.
  GitHub's own "require review from someone other than the last pusher" sees accounts only (Tier A, 0.85).
- Decision: a `Built-by:` commit trailer written by `git interpret-trailers` (git's own tool, no new dependency),
  checked by the existing `check_roles.py` and `review_merge.sh`.
- Confidence that nothing fits better: 0.8.
