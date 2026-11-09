# Design process

Rules for every screen, frame and design canvas in a ShipQuick project. They are generic: no project names, no tokens, no story numbers. Each rule says the date it was learned, so a later change can be dated too. Read this page before any design work; read `design-system.md` and `design-tokens.md` for the look itself.

## 1. Direction before screens (29 Oct 2026)

Never jump to making screens before the direction is final.
- First show two or three frames, or one or two variations of the one thing in question.
- Get the owner's feedback in words: what he likes, what he does not.
- Only then go to the full design, and even then two or three screens at a time, feedback, then the next.
- Brainstorm the direction in words first when the owner asks for it. Nothing is built before he picks.
- Motion follows the same rule: frames and a note, never a finished animatic.

## 2. Design first, approval, then code (28 Oct 2026; rewritten 30 Oct 2026, story #121)

- At Definition of Ready, every story answers: does this touch the frontend — UI, layout, design or copy? Yes or no, on the issue.
- A "yes" starts with a sample screen on the design canvas, from the latest approved board, shown to the owner. Code does not start until he approves it and the board moves to "Design final not live". The code builds that exact screen; copy goes from the frame into the code word for word — the frame is the contract, the code does not improve the words on its own.
- This applies to every story type: feature, bug fix, chore. Code is never ahead of design.
- After the code ships to production, the board moves to "Production" (rule 3).
- A PR that touches the project's own frontend paths (`scripts/check_frontend_design.sh`, globs configured per project) must name the approved board and its approval date in its body (`Design board: <name>` and `Approved: <date>`), or the check fails — in CI and in `scripts/check_local.sh`. A PR that says "no screen change" while still touching those paths also fails. A `dev -> main` promotion or a `main -> dev` back-merge (base or head is `main`) is never a frontend story and is always skipped.
- Nothing on the canvas is deleted. An old version moves to the mistakes section (rule 4).

## 3. The canvas by stage (29 Oct 2026)

One canvas per project. Each stage is a section on its own background board.

Stages are columns, read left to right (9 Nov 2026, story #165). The owner reads a process left to right, like a kanban board. So the columns follow the order a design moves, and end on what the team learned:
1. In discussion: no decision yet, or on hold. Prefix IN TALK.
2. Approved, not built: the owner said yes; no code yet. Prefix DESIGN.
3. On dev: coded and on the dev link, or behind a flag the live build does not carry. Prefix ON DEV (or ON STAGING).
4. Production: the screen as it is live today, the latest version only. Prefix LIVE.
5. Mistakes, fixed: the old screen as it was when it was wrong, with a note naming the fix and the corrected board in Production. Prefix OLD.
6. Rejected: tried and not taken, or replaced by a later pick. It sits near the end because it is the feedback loop. Prefix REJECTED.
7. Design learnings: one board the tool makes for you (see below). Prefix LEARNINGS.

Set `"layout": "columns"` in the manifest. Each section is one column; its rows stack top to bottom inside it. A column that grows past 8000 px splits into tiles downward, as before. Every run places every column again, so a growing column never meets the next one. Without the key, sections stack top to bottom (the old layout), so an old canvas does not move until you choose.

The Design learnings board (9 Nov 2026, story #165). The owner is learning design; the reviewer is the expert. The board keeps what he likes and dislikes, and teaches him back.
- It lives in the section with `"id": "learnings"`. In column layout that section is required; the tool stops without it.
- Its rows are in that section's `"learnings"` list: `{"date": "2026-11-09", "kind": "owner", "text": "...", "link": "..."}`. `link` is optional.
- `kind` is one of three columns: `owner` (the owner's own taste, credited to him), `craft` (a craft rule the reviewer taught), `testing` (what testing taught both). Any other kind stops the run.
- The tool draws one board, `design-learnings.dc.html`, three columns, newest on top. Never edit the board by hand; edit the list.
- After every owner design decision, the reviewer adds one row the same day.
- An `owner` row is his call. A generic rule never overwrites it. When they disagree, both rows stay, and the note says which one stands for this project.
- Each new frame says in one line which rule it shows and why, so the owner learns while he picks.

How it is kept:
- The layout comes from a manifest (`design/canvas-stages.json`: sections, rows, the boards in each row, the purpose of each section) through `scripts/canvas_stage.py`. A board moves by editing the manifest and running the tool, never by dragging.
- The manifest, in short. Colours and the font are the project's own, copied from its tokens; the tool holds none. Keys the tool does not know (`canvas`, `arranged`, a project's own record) are left alone and ignored.
  ```json
  {
    "canvas": "https://claude.ai/artifact/<id>",
    "tints": {"sage": "#rrggbb", "teal": "#rrggbb", "yellow": "#rrggbb", "red": "#rrggbb", "gray": "#rrggbb"},
    "ink": "#rrggbb", "paper": "#ffffff", "font": "'Project Sans', system-ui, sans-serif",
    "start_here": "How to read this canvas: ...", "start_tint": "sage",
    "remove_notes": ["an-old-title-note"],
    "layout": "columns",
    "sections": [
      {"id": "talk", "title": "1 · In discussion", "purpose": "Waiting on a pick.", "prefix": "IN TALK", "tint": "yellow",
       "rows": [{"id": "1a", "title": "1a · Sign-in options", "boards": ["SignIn-A.dc.html", "SignIn-B.dc.html"], "notes": []}]},
      {"id": "production", "title": "4 · Production", "purpose": "What is live today.", "prefix": "LIVE", "tint": "sage",
       "rows": [{"id": "4a", "title": "4a · First open", "boards": [{"board": "Welcome.dc.html", "pr": "#12", "approved": "2026-10-20"}], "notes": ["first-open"]}]},
      {"id": "learnings", "title": "7 · Design learnings", "purpose": "What we learned, newest on top.", "prefix": "LEARNINGS", "tint": "gray",
       "rows": [], "learnings": [{"date": "2026-11-09", "kind": "owner", "text": "Main button at the bottom, same place every step."}]}
    ]
  }
  ```
  `boards` are the canvas file names; `notes` are the ids of story stickies that sit at the end of that row; a row's `prefix` overrides the section's. `remove_notes` is the only way the tool removes a note of yours (its own notes carry the `cs-` prefix).
- A background is an artboard, listed first in the canvas order, sized around everything inside it. A drawn note never sits under a screen, so a note is never a frame.
- Nothing ever sits outside its background board: no text, icon, image, note or screen. The tool refuses a layout where a box is outside its board or two boxes overlap.
- Inside Production the rows follow the user's journey left to right, then the other roles (staff, admin).
- Every board's name starts with its state: LIVE, ON STAGING, ON DEV, DESIGN, IN TALK, REJECTED, OLD, LEARNINGS, UNSORTED.
- A "start here" note above the first section says how to read the canvas. In column layout it says: one stage per column, read left to right, end on the learnings. Section titles say the purpose; each section note says what it holds and when a board moves.
- A board the manifest forgets lands in an Unsorted row, so nothing is lost and the gap shows.
- Chat never cites a canvas version number; the link always opens the latest.
- Publish from the canvas, never from memory (9 Nov 2026, story #163). A tall section splits into a new tile file on its own. A typed list misses it, and its boards float with no background.
  1. Read the live canvas first. Run the tool with `--apply`.
  2. Publish exactly what `canvas_stage.py --canvas <folder> --publish-list` prints: `project/canvas.json`, every bg tile, every board.
  3. List the artifact's files. Save the listing to a file, one path per line.
  4. Run `canvas_stage.py --canvas <folder> --verify <listing>`. It fails and names each file that canvas.json needs and the artifact lacks. Publish those, then run it again until it passes.

## 4. Which bucket (29 Oct 2026)

- Production holds the latest version of what is live. A corrected screen that is live goes here, never in the mistakes section.
- The mistakes section holds the old wrong version, with the fix named in the note.
- A fix made on the base board itself leaves no old board; that is fine, say so in the note.
- A feature coded behind a flag the live build does not carry is "on staging", not live.
- A redesign that replaced a live screen is not a mistake; the note says "redesign" and names the decision.

## 5. Base boards (29 Oct 2026)

- A new frame starts from the latest approved board, never from an older copy.
- When an options board exists (A, B, C), the chosen option is the base; the note on the canvas says which won and when.
- Two "approved" boards for the same thing is a bug: the note must say which one stands.

## 6. Contrast and colour (24 to 29 Oct 2026)

- Every colour comes from the project's tokens, never a literal in a screen.
- Text keeps 4.5:1 against its surface in every theme (3:1 at 24 px and up). Check both themes before a screen is called done.
- A state shown by colour always carries a word; colour alone is never the message.
- One pop colour per system. The error token is for failures only, so a warning (no connection, a hold) never looks like a failed order.
- A big board or band behind screens keeps enough contrast that each screen's edge is clear.
- Before any text is placed anywhere (a screen, a board, a note), look at what sits behind it: light behind means dark text, dark behind means light text. Never let an editor pick the colour of a title for you; paint the title on the board, in a colour you chose against that board's fill, and measure it (the canvas tool does, and stops under 4.5:1).

## 7. Layout (24 to 29 Oct 2026)

- Spacing in 8 pt steps, a 20 px screen gutter, 44 px tap targets, a type scale kept to.
- One screen is one board, at the device size (phone 390 by 844).
- On the canvas: 80 px between boards in a row, 120 px between rows at least, a title at least 223 px above its row.
- Nothing overlaps text, an icon, a panel or an image, on a screen or on the canvas. Text painted on a background board (a band, a row title) is a box like any other; a continued board (the second tile of a tall section) carries no band, so a row title never meets one. The tool checks it.

## 8. Who owns the canvas (29 Oct 2026)

- One owner per project: the reviewer session. It reads the live canvas before every change and publishes with the tool.
- The coder reads the canvas and never edits it. A code change that needs a board change asks the reviewer in a teammate block.

## 9. The owner's words land on the canvas and on the story (29 Oct 2026)

- A comment the owner leaves on a board is answered on that board (what changed, where) and recorded on the story issue the same day.
- A decision that changes scope (a new flow, money, a setting) goes on the story before the build, in his words.

## 10. Provenance, not recency, decides Production drift (30 Oct 2026, story #125)

When a Production board and the live app disagree, the question is never "which one is newer" — it is
"which one was approved". Recency decided once, on a GoServe audit: 62 of 66 boards were read as
"stale" and rewritten from unapproved code, overwriting design nobody had signed off.

- If no approved board covers an app change, **the app is the drift and the board stands.** The fix is
  a code story back to the board, or a new design story through approval (rule 2) — never a silent
  rewrite of the board from whatever the app happens to do.
- A Production board is rewritten from the app **only** when the PR that changed the app named that
  approved board (`Design board: <name>` and `Approved: <date>`, rule 2 / story #121).
- The manifest enforces this: a `boards` entry in the Production section (`"id": "production"`) must be
  `{"board": "<name>", "pr": "<the PR that changed it>", "approved": "<its approval date>"}`, not a
  plain filename. `scripts/canvas_stage.py` refuses to lay out — and writes nothing — when a Production
  board entry has no `pr` or no `approved`, when `pr` is not `"#<n>"`, a PR URL, or `"baseline"`, or when
  `pr` is `"baseline"` but the manifest's `"provenance_since"` is unset or this board's `approved` date
  falls after it — a one-time migration date, not a free pass to fake provenance for anything newer.
- A drift audit (any number of boards, any time) never edits a board itself. It lists each mismatch —
  board, app screen, the PR that caused it, whether that PR named an approved board, and the verdict
  (app drift or board drift) — using `docs/templates/drift-report.md`. Only a human decision (a code
  story, or a new approved design story) changes anything from there.

## 11. Feedback becomes a rule the same day (29 Oct 2026)

- Every generic design feedback from the owner (anything that would apply to another project) is written into this page the same day, with its date, by the session that received it, and into that session's own instruction file. Project-specific feedback goes to the project's docs. Nothing stays only in chat.

## 12. Step-by-step flows: the main action is last, in the same place on every step (9 Nov 2026, story #164)

A flow of two or more steps (onboarding, sign-up, checkout steps) is read as one thing, not as separate screens. A person taps "next, next, next" with one thumb. The main action must never move.
The rule is the same on web, Android and iOS. Each platform's own words are in brackets.

1. The main action is one full-width button, anchored to the bottom of the content area. It sits above the safe area (iOS home indicator, Android gesture bar, a web page's bottom edge). The last element ends 24 px above that edge plus the safe area.
2. With two actions, the main one (filled) is LAST, at the very bottom. The other one (outline or text) sits above it. So the main button is in the same place on every step, whether a step has one button or two.
3. The hero visual of a step (an icon, an image, an illustration) is centred on one line shared by every step of the flow. Measure the centre on the visual's own shape (its circle), not its box, since boxes carry uneven padding.
4. On a step with typing, the button rides on top of the keyboard (iOS keyboard layout guide, Android `imePadding`, the web `visualViewport` or `interactive-widget=resizes-content`). It never hides under the keyboard and never jumps to the top.
5. The steps fill the space. A big empty area under a button that sits high is a bug, not air.

Exceptions:
- A danger or cancel pair (delete, sign out) keeps its own pattern: the danger action is never the easy default.
- A long list or a form that scrolls keeps a sticky bottom bar with the same button; the rule still holds.
- One dialog alone, or a wide desktop layout, is not a step flow.

How it is checked: the reviewer looks at the steps side by side, not one screen at a time. Measure the main button's top edge and the hero's centre on every step. They match within 2 px, or the flow goes back.
Why: the bottom of a phone is where the thumb rests (Steven Hoober, 2013, observed one-thumb use). Apple and Google's own guides put main actions within easy reach.

## 13. A default screen is not a design (9 Nov 2026, story #148)

On a screen with one job (sign-in, an empty state, a permission ask, a confirmation, an error with one way out), the words are most of what the person sees. So the words are the design.
1. Options put to the owner differ in their words, not only in layout. Each option board says in one line the sentence that makes it different.
2. A board whose text could be pasted into any other product unchanged is not an option. It is the default, and the default is not a design.
3. A rejected option is annotated the same day: on the canvas, beside the board, in the owner's own words, with the one rule it leaves behind. The same reason goes on the story issue, so the coder reads it without opening the canvas. Add the rule to the Design learnings board too (rule 3).

The manifest carries it, and `scripts/canvas_stage.py` stops the run without it:
- A row with `"options": true` lists each board as `{"board": "<name>", "copy": "<the sentence that makes it different>"}`. A board with no `copy`, or two boards with the same `copy`, stops the run.
- A row whose prefix is `REJECTED` lists each board as `{"board": "<name>", "reason": "<the owner's own words>"}`. A rejected board with no `reason` stops the run.

Applies to: any options board shown to the owner for a pick, and any screen with one main action and little else.
Does not apply to: dense screens where the real question is layout; motion frames; a board that only restates an approved screen; a screen with no text.
