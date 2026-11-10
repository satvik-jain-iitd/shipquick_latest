# Experiments

Every test of a hypothesis lands here: what we tried, how, the result and the decision. A failed test stays.

| Date | Experiment | Design | Result | Decision |
|---|---|---|---|---|
| 2026-11-10 | Haiku coder on an XS or S story (ShipQuick Desk, epic #91) | The design step and the build step ran as separate Haiku agents under the reviewer session. The reviewer ran every runtime claim itself. | Design step: 118k tokens, 37 tool calls, 4.8 min, 0 defects. Build step: 100,892 tokens, 13 tool calls, 2 min 9 s measured wall time (the agent reported about 25 min), 522 lines, 8 tests red then green, 4 of 4 runtime claims verified by the reviewer, 1 medium and 1 low finding. | Fit for XS and S stories. Time self-reports are not trusted; measured wall time is used. |
| 2026-11-10 | Rules split by path (story #328, spike): UI rules 31 and 38 in a path-scoped file under `.claude/rules/` | Hypothesis: the two UI rules can move to a rule file with `paths:` and nothing is lost. Docs read on 10 Nov 2026 with WebFetch: https://code.claude.com/docs/en/memory (section "Path-specific rules": a path rule loads when Claude uses Read, Write or Edit on a matching file, or a Bash read of one file; a rule without `paths` loads at launch). Design: paired run on the bench (#312, A1b) with the same tasks and arms, rules in CLAUDE.md wording against the path file. Result: pending test. No run yet; no rule moved in #328. | Decision: pending. Move only if the paired run shows no regression. Known gap: a path rule does not load for a subagent edit made only through Bash. |
