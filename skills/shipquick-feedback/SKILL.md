---
name: shipquick-feedback
description: Send one line of feedback about a ShipQuick gap, found while working in any project that carries ShipQuick as the knowledge/shipquick_latest submodule, into ShipQuick's own feedback inbox as a full nine-section story. Use when the owner says "send this to ShipQuick", "ShipQuick feedback", "tell ShipQuick about this", or when a session hits a ShipQuick rule, check or script that is missing, wrong, or carries project facts that do not belong in the generic kit.
---

# ShipQuick feedback

ShipQuick is the shared process every project inherits. A gap found while working in a child project (job-search, GoServe, LinkRight, any project with the `knowledge/shipquick_latest` submodule) never becomes a full PR against ShipQuick from inside that project — the child session does not know ShipQuick's own rules (branches, TDD, team blocks). It becomes one `feedback` issue instead, told as the whole story, so the ShipQuick sessions can build a generic fix.

## When to run this

- The owner says "send this to ShipQuick" (or similar words) about something just discussed.
- You (the session) hit a ShipQuick rule, check, or script that is missing, wrong, too strict, or carries one project's own facts into the generic kit.

## Steps

1. Copy `knowledge/shipquick_latest/docs/templates/feedback.md` to a scratch file.
2. Fill every section from this session's own context — do not leave any blank:
   - **Situation, Expected vs seen, Steps to reproduce, Impact**: what actually happened here, in this project, right now.
   - **Root cause**: a real five-whys chain, at least three "Why" lines, ending at the real cause, not the symptom.
   - **Why ShipQuick did not catch it**: name the missing or wrong rule, check or script.
   - **How big teams avoid it**: find one real source (a book, a vendor doc, a well-known practice) with its tier (A, B, C, K, P) and a confidence from 0 to 1. Never invent a source.
   - **Generic fix for ShipQuick**: the change written for any project — no project facts (no this project's own numbers, names, or setup). State "Applies when" and "Does not apply to".
   - **Stop the repeat**: the test or CI check that would catch it next time, and the workaround this project uses today.
   - Leave the header out — `feedback.sh` fills it.
3. **Show the filled file to the owner before sending it.** He reads it in chat; fix anything he flags.
4. Run, from the project's own repo root:
   ```
   knowledge/shipquick_latest/scripts/feedback.sh --title "<one line>" --body-file <the scratch file>
   ```
5. Report the result in one line: the issue number it opened, or the issue number it commented on (a similar one was already open), or — if there was no `gh` login for the build account — tell the owner to paste the printed text himself.

Never skip step 3. Never invent the "how big teams avoid it" source. Never write project facts into the "generic fix" section.
