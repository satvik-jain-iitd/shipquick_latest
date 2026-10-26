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
  the list of projects, Kill switch, and a GET webhook that serves a page) and SUB `SQ Roadmap 11 Build Page` (GitHub
  GraphQL, render, save to the Data Table `roadmap_pages`). Source and tests: `roadmap/` in this repo.
  The renderer is `roadmap/render.js` (port of GoServe `scripts/roadmap.py`); `roadmap/build.js` writes the two workflow
  files into `roadmap/workflows/`. Never edit a node in the n8n editor: change the source, run the tests, build, deploy.
- One link per project: `https://n8n.linkright.in/webhook/roadmap?s=<slug>&k=<key>`. One fixed path, not `/roadmap/<slug>`:
  n8n puts an id into the URL of a webhook with a path parameter, and that id changes on a re-import.
  The key is a secret in `~/Desktop/Secrets/shipquick-roadmap.env`. The repo holds only its SHA-256 (`roadmap/projects.json`),
  so no key sits in a workflow file. A wrong or missing key returns 404. To rotate a key: make a new one, put its hash in
  `projects.json`, build, deploy, send the new link.
- The link works like a password. The key also shows in browser history and in proxy logs, so share it only with people you trust, and rotate it if it leaks.
  The MAIN keeps no successful run (`saveDataSuccessExecution: none`), so the key and the page do not stay in the n8n history either. Failed runs are still saved.
- The Kill switch stops the builds only. The link keeps answering with the last saved page, because serving only reads.
- The page lists the titles of the repo's issues. A private repo's titles are on the page, so the key is the only lock:
  share the link only with people who may read those titles.
- The GitHub token is read-only (issues, pull requests, metadata). It lives only as the n8n credential
  `SQ Roadmap GitHub read-only` (HTTP header auth: `Authorization: Bearer <token>`).
- Issues must close when their change is merged (`Closes #n` in the change, or `scripts/close_linked_issues.py` after a merge into dev). The page asks GitHub for open pull requests only, so a story whose change is merged but whose issue is still open goes back to To do.
- A child project joins by adding one row to `roadmap/projects.json` (slug, title, repo, vision line, key hash), building,
  deploying, and putting the link in its README. The token must be able to read that repo.
- Limit: one GitHub page, the newest 100 issues. The page says so when a project passes it (`render.js`, `MAX_NODES`).

### Registry (n8n rulebook A1.3)
| Workflow | Kind | Job | Called by | Id |
|---|---|---|---|---|
| SQ Roadmap 01 | MAIN | timer, serve a page, Config, Kill switch | timer and GET link | set after deploy (`roadmap/ids.json`) |
| SQ Roadmap 11 Build Page | SUB | read GitHub, render, save | SQ Roadmap 01 | set after deploy (`roadmap/ids.json`) |

### Deploy (needs the owner's yes: activation, new folder, token)
1. Create the n8n folder `Roadmaps`, the Data Table `roadmap_pages` (columns `slug`, `html`, `updated_at`, all text) and the credential.
2. Put the ids in `roadmap/ids.json`, run `node roadmap/build.js` (it refuses while an id still starts with `TBD`; `--draft` is only for the committed draft files), create SUB then MAIN with the API (SUB first, rulebook 95.16). The MAIN calls the SUB once per project (`mode: each`): a failing project stops the later ones and the Error Alert fires.
3. Dry run (Config `dry_run` is true): read the execution node by node. Then set `dry_run` false, run once, open the link.
4. Activate the MAIN. Look at both canvases in the editor (fit view).

## Done when
A new issue shows on the page within 15 minutes, and the link opens on the owner's phone.
