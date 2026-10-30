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
