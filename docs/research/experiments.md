# Experiments

Every test of a hypothesis lands here: what we tried, how, the result and the decision. A failed test stays.

| Date | Experiment | Design | Result | Decision |
|---|---|---|---|---|
| 2026-11-10 | Haiku coder on an XS or S story (ShipQuick Desk, epic #91) | The design step and the build step ran as separate Haiku agents under the reviewer session. The reviewer ran every runtime claim itself. | Design step: 118k tokens, 37 tool calls, 4.8 min, 0 defects. Build step: 100,892 tokens, 13 tool calls, 2 min 9 s measured wall time (the agent reported about 25 min), 522 lines, 8 tests red then green, 4 of 4 runtime claims verified by the reviewer, 1 medium and 1 low finding. | Fit for XS and S stories. Time self-reports are not trusted; measured wall time is used. |
