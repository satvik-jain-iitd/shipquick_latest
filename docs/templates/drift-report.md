# Drift report: Production board vs live app

Run this when a Production board and the live app disagree. It only lists what disagrees and why — it
never edits a board. A human decision (a code story back to the board, or a new design story through
approval) is what changes anything, never this report (`docs/DESIGN_PROCESS.md` rule 10, story #125).

One row per mismatch:

| Board | App screen | Causing PR | Approved board named? | Verdict |
|---|---|---|---|---|
| `<board file>` | `<the live screen it should match>` | `#<PR that changed the app screen>` | yes / no | app drift / board drift |

- **Approved board named?** did that PR's body carry `Design board: <name>` and `Approved: <date>`
  (rule 2)? "yes" only if it named *this* board.
- **Verdict**: "no" above always means **app drift** — the board stands; the fix is a code story back
  to the board, or a new design story through approval, never a silent board rewrite. "yes" means the
  change was approved first, so it is safe to rewrite the board from the app (**board drift**, i.e. the
  board is the one now behind).

## Worked example

| Board | App screen | Causing PR | Approved board named? | Verdict |
|---|---|---|---|---|
| `LIVE · Checkout.dc.html` | /checkout | #142 | no | app drift — board stands; open a code story to match `Checkout.dc.html`, or a design story for the new layout |
| `LIVE · Cart.dc.html` | /cart | #138 | yes (`Cart.dc.html`, approved 2026-10-20) | board drift — `scripts/canvas_stage.py` may now rewrite `Cart.dc.html` from the app, citing `{"pr": "#138", "approved": "2026-10-20"}` |
