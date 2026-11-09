# Templates

## Screen file: `<qa_home>/screens/NN-<board>.md`
```
# Screen NN: <board name> (<what it is>)
Board: <canvas board name, exact>. App link: <dev link>. Prod link: <prod link or "not on prod">.
## A. Design review (board)        -> D<NN>.<n>: gap, before, after, reason, source, tier. Or "No design gaps".
## B. Controls                     -> control | must happen | on failure
## C. Cases                        -> TC <NN>.<n> | case | steps | expected | check (auto/probe/owner) | result
## D. Owner comments               -> date | comment | decision
```

## runs.jsonl (one line per case result)
{"run": 1, "date": "2026-11-09", "params": 1, "scope": "screen|full", "env": "dev|prod",
 "device": "chromium-390|webkit-iphone13|owner-iphone", "screen": "O0g-B", "case": "TC 1.8",
 "attack": "NET-OFF|basic", "by": "auto|probe|owner", "new_case": true, "result": "pass|fail|blocked|pending",
 "bug": 42, "escape": false}
`escape` is true when the owner found the bug outside the written cases.

## design-audit.jsonl (one line per finding)
{"run": 1, "date": "2026-11-09", "screen": "O0g-B", "image": "boards/O0g-B.png", "source": "board|app",
 "pass": "goldfish|elephant|lens", "kind": "good|issue", "lens": "C2", "severity": "Blocker|Major|Nit",
 "box": [x, y, w, h], "see": "...", "why": "...", "ref": "source and tier", "fix": "...",
 "impact": "high|medium|low", "effort": "S|M|L", "bucket": "now|next|later", "status": "new|still open|resolved"}
`box` is in the pixels of `image`.

## Bug story (GitHub issue)
Title: `<screen>: <what is wrong, in user words>`
Labels: story, qa, bug, plus design-canvas when the board changes. Sub-issue of its epic.
```
**Case:** TC <id>. **Found by:** auto / probe / owner. **Attack:** <id>. **Severity:** <level>.
**Side:** design / app / both.
**Before:** <image of the wrong screen>
**After (expected):** <board image, or the new board after the design fix>
**Why:** <one or two lines, with the rule or source>
**Steps to see it:** 1. ... 2. ... 3. ...
**Done when:** the automated test `TC <id> ... (#<issue>)` passes on dev.
```

## Severity
critical: blocks a core flow, loses data or money. high: a feature is broken, no way around.
medium: works with a visible problem, a way around exists. low: cosmetic.
