# Live roadmap (requirement, v1.0.0)

Every project has one live roadmap page from its first epic. The owner opens it at any time, on any device,
and sees where the project stands. Nobody edits it by hand.

## What the page shows (top to bottom, one vertical scroll)
1. **Vision**: one line, the end goal, in words a stranger understands.
2. **Delivered**: closed epics and stories, newest first, folded shut by default.
3. **Now**: stories with an open PR or the `doing` state.
4. **Next**: open stories in priority order.
5. **Board**: four columns, To do, Doing, Review, Done, one card per story.

## Where the words come from
- Each story's roadmap text is the first sentence under `## Business` in the issue (or a `**Business line:**` line).
- Plain words: tech terms are swapped for plain ones (CI = "the checks", PR = "change", migration = "database change").
  The Board keeps the story's own words.
- An epic is an issue labelled `epic`; a story is its sub-issue (`story` or `user-story`).

## How it runs (runtime rule: free, GitHub only, nothing on the Mac, no n8n)
Owner decision, 26 Oct 2026: a kit user may have no n8n and no server, so the roadmap runs on GitHub Actions alone (story #49).
- One reusable workflow, `.github/workflows/roadmap.yml` (`on: workflow_call`). A project calls it from a short file of its own.
  It asks GitHub for the project's issues and open pull requests, writes `ROADMAP.md` and keeps it on a branch called `roadmap`,
  so the history of `dev` stays clean. It makes no commit when the page did not change (the page has no clock inside).
- The token is the built-in `GITHUB_TOKEN`, so a project reads only itself. The calling job grants `contents: write`
  (to write the `roadmap` branch), `issues: read`, `pull-requests: read`, `checks: read` and `statuses: read` (the check state sets Doing or Review).
  No secret, no personal token.
- Settings live in the project: `roadmap.json` with `title` and `vision` (the vision is one line, in words a stranger understands).
  ShipQuick holds no project names. A missing title or vision stops the run with a clear message.
- Code: `roadmap/roadmap.js` writes the Markdown page, `roadmap/query.graphql` is the GitHub question, `roadmap/render.js` has the shared
  rules (plain words, columns, epics) and an HTML page for GitHub Pages. Tests: `node --test roadmap/*.test.js` and `tests/test_roadmap_workflow.py`.
- The page lists the titles of the repo's issues. In a private repo GitHub's own login guards the `roadmap` branch.
- Issues must close when their change is merged (`Closes #n` in the change, or `scripts/close_linked_issues.py` after a merge into dev). The page asks
  GitHub for open pull requests only, so a story whose change is merged but whose issue is still open goes back to To do.
- Limit: one GitHub page, the newest 100 issues. The page says so when a project passes it.
- Limit: a pull request from a fork has a read-only token, so its run cannot write the branch. It stays red on the fork only.

### A child project joins in three steps
1. Add `roadmap.json` (title, vision) to the root of the project.
2. Copy `.github/workflows/roadmap-call.yml` from ShipQuick. Change `uses:` to
   `satvik-jain-iitd/shipquick_latest/.github/workflows/roadmap.yml@<SHA>` and `shipquick_ref` to the same SHA. Keep the `permissions:` block of the job.
3. Merge it into the default branch (scheduled and issue runs only start from the default branch). Open `ROADMAP.md` on the `roadmap` branch,
   and put that link in the README.

### Triggers
Issues (opened, edited, closed, reopened, labeled), a finished CI run (it runs on every pull request push, so Doing and Review stay current), a daily
timer, and a manual run. There is no pull request trigger: on a pull request the job would run that change's own unreviewed script with write rights.
Every trigger starts from the default branch, so the script that runs is reviewed code. A change shows on the page about a minute after the event.

## Done when
A new issue shows on the page within 5 minutes, and the link opens on the owner's phone.
