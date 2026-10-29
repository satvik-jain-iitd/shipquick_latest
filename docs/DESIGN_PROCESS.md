# Design process

Rules for every screen, frame and design canvas in a ShipQuick project. They are generic: no project names, no tokens, no story numbers. Each rule says the date it was learned, so a later change can be dated too. Read this page before any design work; read `design-system.md` and `design-tokens.md` for the look itself.

## 1. Direction before screens (29 Oct 2026)

Never jump to making screens before the direction is final.
- First show two or three frames, or one or two variations of the one thing in question.
- Get the owner's feedback in words: what he likes, what he does not.
- Only then go to the full design, and even then two or three screens at a time, feedback, then the next.
- Brainstorm the direction in words first when the owner asks for it. Nothing is built before he picks.
- Motion follows the same rule: frames and a note, never a finished animatic.

## 2. The canvas is the contract (28 Oct 2026)

- Every UI change lands on the design canvas in the same story as the code, as a board with a note. A story with a screen change and no board is not done.
- Copy goes from the frame into the code word for word. The frame is the contract; the code does not improve the words on its own.
- Nothing on the canvas is deleted. An old version moves to the mistakes section (rule 4).

## 3. The canvas by stage (29 Oct 2026)

One canvas per project, five sections top to bottom, each on its own background board:
1. Production: the screen as it is live today, the latest version only.
2. Design final, not live: the owner said yes; not coded yet, or coded behind a flag the live build does not carry.
3. In discussion: no decision yet, or on hold.
4. Rejected: tried and not taken, or replaced by a later pick.
5. Mistakes, fixed: the old screen as it was when it was wrong, with a note naming the fix and the corrected board in section 1.

How it is kept:
- The layout comes from a manifest (`design/canvas-stages.json`: sections, rows, the boards in each row, the purpose of each section) through `scripts/canvas_stage.py`. A board moves by editing the manifest and running the tool, never by dragging.
- A background is an artboard, listed first in the canvas order, sized around everything inside it. A drawn note never sits under a screen, so a note is never a frame.
- Nothing ever sits outside its background board: no text, icon, image, note or screen. The tool refuses a layout where a box is outside its board or two boxes overlap.
- Inside Production the rows follow the user's journey left to right, then the other roles (staff, admin).
- Every board's name starts with its state: LIVE, ON STAGING, DESIGN, IN TALK, REJECTED, OLD, UNSORTED.
- A "start here" note above section 1 says how to read the canvas. Section titles say the purpose; each section note says what it holds and when a board moves.
- A board the manifest forgets lands in an Unsorted row, so nothing is lost and the gap shows.
- Chat never cites a canvas version number; the link always opens the latest.

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

## 10. Feedback becomes a rule the same day (29 Oct 2026)

- Every generic design feedback from the owner (anything that would apply to another project) is written into this page the same day, with its date, by the session that received it, and into that session's own instruction file. Project-specific feedback goes to the project's docs. Nothing stays only in chat.

## 9. The owner's words land on the canvas and on the story (29 Oct 2026)

- A comment the owner leaves on a board is answered on that board (what changed, where) and recorded on the story issue the same day.
- A decision that changes scope (a new flow, money, a setting) goes on the story before the build, in his words.
