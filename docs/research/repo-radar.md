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
