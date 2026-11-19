# ShipQuick Desk: design, two options

Epic #91. Owner put it first on 10 Nov 2026. This doc is the design only. No build starts until the owner picks A or B.

## Goal

One page on the owner's own Mac. He opens it and sees one project's ShipQuick:
- which features are on,
- what is waiting for him,
- what the agents decided for him,
- the roadmap.

It runs on localhost. It does not run on the phone.

## What the Desk shows

Each part has one source. No part needs a new service.

1. **Waiting for you.** Open pull requests and the owner's next call.
   Source: `gh api graphql` with `roadmap/query.graphql` (open PRs, their check state, their draft flag). Plus `.shipquick/roles.yml` (who the owner is).
2. **What the agents decided for him.** Rows where the owner was not asked.
   Source: `docs/process-trace.md` (the column "owner contact asked / volunteered / reviewed"). This file is in the repo, so no network is needed.
3. **Features on.** Which switches are on for this project.
   Source today: `.shipquick/mode`, `.shipquick/freeze` and the `Dev link:` and `Production link:` lines in the project `CLAUDE.md`. There is no single feature list yet. Epic #86 (features as plugins) would give one. See open question 1.
4. **Roadmap.** Now, Next and the board.
   Source: `roadmap/query.graphql` for the GitHub data, then `roadmap/render.js` `build()` for the same columns the public page uses. The Desk reuses this code. It does not copy it.

Every number on the page has a time stamp of when it was read.

## Option A: a file the timer writes, and a static page

**How it runs.** Two small parts.
- A timer (launchd, every 5 minutes) runs `scripts/desk_pull.py`. That script runs `gh`, runs the roadmap engine, reads the `docs/` files and writes `desk/desk.json` next to the page.
- `desk/index.html` reads `desk.json` every 60 seconds and redraws.
- A plain `python3 -m http.server 8765 --bind 127.0.0.1` serves the folder.

**How data comes in.** Only the timer touches `gh`. The page only reads one JSON file.

**No token on disk.** `gh` keeps its login in the macOS keychain. The script never reads the token. `desk.json` holds no token and no account secret.

**When gh is logged out.** The timer fails. The script keeps the last good `desk.json`, adds `"error": "gh is logged out: run gh auth login"` and a new `"as_of"` time. The page shows a stale banner with that text. Nothing is lost.

**Size (estimate).** Page about 150 lines. `desk_pull.py` about 120 lines. Plus one launchd plist of about 20 lines.

**Reuse of roadmap.js.** The script calls `node roadmap/roadmap.js` for the Markdown page and `roadmap/render.js` `build()` for the columns. No new roadmap code.

## Option B: one stdlib server that asks gh on request

**How it runs.** One process: `python3 scripts/desk_server.py`. It binds to `127.0.0.1` only. It serves:
- `GET /` the page,
- `GET /api/state.json` the state.

When the state is asked for, the server runs `gh`, the roadmap engine and the `docs/` reads. It keeps the answer for 60 seconds. The page asks for `/api/state.json` every 60 seconds, so the data refreshes on a timer. Gh runs at most once a minute.

**How data comes in.** On request, through `gh` in a child process with a 20 second timeout.

**No token on disk.** Same as A. The server holds no token. It never writes the answer to disk.

**When gh is logged out.** The route returns the last good answer with `"stale": true` and `"error"`. If there is no good answer yet, it returns HTTP 503 with the same error text. The page shows the error card.

**Safety.** The server checks the `Host` header is `127.0.0.1:<port>` or `localhost:<port>`. This blocks a web page from reading the Desk through a DNS trick.

**Size (estimate).** Server about 140 lines. Page about 150 lines, the same page as A. No launchd plist needed.

**Reuse of roadmap.js.** Same as A. The same functions run in the request.

## Side by side

| | Option A: timer writes a file | Option B: server asks on request |
|---|---|---|
| Processes running | Two: the timer and `http.server` | One: `desk_server.py` |
| When gh runs | Every 5 minutes, even when the page is closed | Only when the page is open, at most once a minute |
| Data age on open | Up to 5 minutes old | Up to 60 seconds old |
| Token on disk | No | No |
| Logged out | Last good file, banner shows the error | Last good answer, error card |
| Attack surface | A static folder | A small API, Host check needed |
| Lines (estimate) | About 290 plus a plist | About 290 |
| Reuses roadmap.js | Yes | Yes |
| Phone | No | No |
| Fits "no server beyond the stdlib" | Yes, `http.server` is stdlib | Yes |

## Recommendation

**Option B.** One process, fresh data when the owner opens the page, and no timer to forget. The page is the same file in both options, so switching later costs little.

Why not A: the timer keeps calling GitHub while nobody looks, and a launchd job is one more thing that can silently stop.

## Risks

- **GitHub rate limit.** The roadmap query reads 100 issues and 100 PRs. The 60 second cache keeps it far below the limit. The page says when it hit the limit.
- **The Mac must be on.** Both options need the Mac awake and a terminal or launchd job running. Stated on the page.
- **Stale data is shown as stale.** A page that looks fresh but is not is the worst result. Both options show the `as_of` time on every card.
- **Feature list is a guess.** Until epic #86 exists, "features on" reads a few switch files. The page labels it "switches read from files", not "all features".
- **Host check missed.** If the Host check is left out, option B can be read by any local web page. The check is required, and a test must send a bad Host and get 403.

## Open questions for the owner

1. "Features on": is it fine to show the switch files for now (mode, freeze, dev link), until epic #86 gives one feature list?
2. Should the Desk show one project only (this repo), or every child in `docs/children.md`?
3. Is localhost enough, or do you want it on the phone later? The phone needs a host and login, which is a different and bigger build.

## Frames

- `docs/plans/desk-frame-a.html`: Option A, a 390 px phone board.
- `docs/plans/desk-frame-b.html`: Option B, the same board with the live status.

Each frame names its design rule in the first line of its board.
