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

## How it runs (runtime rule: free, n8n first, nothing on the Mac)
- One n8n workflow pair on Oracle builds every project's page: MAIN `SQ Roadmap 01` (every 15 minutes, Config with
  the list of repos, Kill switch, and a GET webhook that serves a page) and SUB `SQ Roadmap 11 Build Page` (GitHub
  GraphQL, render, save). Source and tests: `roadmap/` in this repo.
- One link per project: `https://n8n.linkright.in/webhook/roadmap/<slug>?k=<key>`. The key is a secret in the Config;
  a wrong key returns 404. The GitHub token is read-only (issues, pull requests, metadata).
- A child project joins by adding one Config row (slug, repo, vision line, key) and putting the link in its README.

## Done when
A new issue shows on the page within 15 minutes, and the link opens on the owner's phone.
