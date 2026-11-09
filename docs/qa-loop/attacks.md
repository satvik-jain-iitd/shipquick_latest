# Attack catalog (generic, shared by every project)

Each attack has an id. Record the id in `runs.jsonl`; the scorecard computes the yield. Add new ones at the end.

| Id | Attack | How |
|---|---|---|
| NET-OFF | Offline at the tap | Airplane mode, then tap the main action |
| NET-SLOW | Slow network | Throttle to slow 3G; watch spinners and double sends |
| NET-DROP | Network drops mid-flow | Go offline after step 2, back online at step 3 |
| TAP-DOUBLE | Double tap | Tap the main action twice fast |
| TAP-BACK | Back at every step | Browser back and Android system back at each step |
| VIEW-SMALL | Small phone | 375 x 667 |
| VIEW-BIG-TEXT | Largest text size | System text size max |
| VIEW-DARK | Dark or night theme | Switch theme mid-flow |
| BRW-WEBKIT | iPhone Safari engine | Run in WebKit, not only Chromium |
| ENV-PARITY | Dev vs prod | Same screen on both links; differences must be on purpose |
| ENV-STALE | Old installed app | Install, deploy a new build, reopen: does the new build load? |
| ORDER-SKIP | Deep link mid-flow | Open a later step's link with no earlier step done |
| ORDER-REPEAT | Redo a finished step | Go back and do a done step again |
| DEV-TWO | Second device | Same account on two phones at once |
| TIME-AWAY | A week away | Expired session, old cache, changed menu |
| COLD-ALERT | Opened from an alert | Tap a push alert with the app closed |
| INPUT-ODD | Odd input | Paste, emoji, very long text, leading spaces, autofill |
| PERM-DENY | Permission denied | Deny location, alerts, camera; then allow later |
| KILL-MID | App killed mid-flow | Swipe the app away during a save or payment |
| CLOCK | Clock and time zone | Change phone time; open near midnight |
| NET-OFF-COLD | Offline cold open | Visit once online, then open with no internet; screen and images must match online | 
