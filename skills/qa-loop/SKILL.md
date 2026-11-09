---
name: qa-loop
description: Self-improving QA loop for any app (web, Android, iOS, CLI) that has approved designs. Three tracks in one loop - sanity (the design and the real app match screen by screen), QA (every control and every happy, sad, edge and error case, automated first, the owner by hand only for what fails or needs a real device; bugs become design or code stories), and a design audit (a world-class designer's critique, written to one HTML report as the roadmap, never as stories). Uses Google's Elephant-Goldfish model - the elephant holds the whole journey, fresh goldfish subagents see one screen cold. Repeats until a run finds zero bugs and learns from every miss. Use when the owner says "qa loop", "screen audit", "design audit", "audit the next screen", "test the app end to end", "regression run", "find bugs", "freeze test", or sends a screenshot of a bug.
---

# QA loop (pointer)

This skill is a pointer. The loop itself lives in the ShipQuick kit, so every project gets the same version.
This folder is a link into the kit (`scripts/install_skill.sh` makes it), so the kit is two folders up.

Read these, in this order, before any step:
1. `docs/QA_LOOP.md` in the kit: the whole loop, sections 1 to 15.
2. The project's own QA home `README.md` (default `docs/qa/`): links, roles, labels, the product promise.
3. The references in the kit's `docs/qa-loop/`: `attacks.md`, `design-lenses.md`, `egm.md`, `templates.md`,
   and the two goldfish briefs `goldfish_cold_user.md` and `goldfish_design_critic.md`.

Tools are in the kit's `scripts/qa/` (scorecard, flow map, audit report, board render, control list, layout gate).
In a child project the kit is `knowledge/shipquick_latest/`, so the paths start there.

Rules that do not bend: never say "works" without a test on the same link and device the owner uses; never
more subagents at once than the project's cap; no personal data in issues, screenshots or reports; a change to
the loop is a ShipQuick feedback issue, never a silent edit here.
