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
