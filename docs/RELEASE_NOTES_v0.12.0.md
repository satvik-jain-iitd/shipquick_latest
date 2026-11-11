# ShipQuick v0.12.0 (11 Nov 2026)

D7 ships as a minor release (`pm/agile/RELEASE_GUIDE.md`). The kit gets an iOS library, a live roadmap page and two new checks for children.

## New

- **Story and design checks for children.** `checks.yml` has a `story` job (#175) and a `design-tokens` job (#133), both in the gate. `adopt.sh` writes the `issues: read` grant and the `edited` pull_request type into the caller (#92).
- **The iOS library (rule 38).** Swift structs generated from the contracts, with a drift check (#222, #215); a SwiftLint runner and a fixture app (#218, #221); snapshot tests (#219) and an accessibility audit per template (#220). The six catch-all modifier docs are split into 18 control and task docs (#296).
- **The live roadmap page (#81 to #84).** Timeline, You are here, dependency map, an HTML page and Cloudflare Pages inputs.
- **The ui MCP server and `llms.txt` (#190).** An agent reads the component library through `scripts/ui_mcp.py`, with ten evaluation questions in `ui/mcp/evals.xml`.
- **Kit checks and tools.** `check_timeouts.py` fails a workflow file with zero jobs (#174); vibe tests with ten screen prompts per platform (#189); a design system board from the registry (#188).

## What breaks for children on the bump

- **The `story` job needs `issues: read` from the caller.** A caller without it makes GitHub refuse the whole ShipQuick checks run at startup (`The nested job 'story' is requesting 'issues: read', but is only allowed 'issues: none'`) and no gate check appears. Run `bash knowledge/shipquick_latest/scripts/adopt.sh .` after the bump. A user story without `Who does it:` (and, from 10 Nov 2026, `Done when:`) also turns the gate red.
- **The caller needs the `edited` pull_request type** to re-run the body-reading checks after a body edit. `adopt.sh` writes it; a hand-written caller keeps working but does not re-run on an edit.
- **The new `design-tokens` job** fails a PR that adds a colour or font literal on a web style line. Move the value into a token file, or list the file in `scripts/design_token_files.txt`.
- **`timeout-minutes` on every child job.** The `adoption` job fails a child workflow job without it. `python3 knowledge/shipquick_latest/scripts/check_timeouts.py .github/workflows` lists them; `timeout-minutes: 10` is the usual value.
- **`ui/llms.txt` must be regenerated.** A doc or registry change in `ui/` that does not regenerate `ui/llms.txt` fails its drift check.

## Not yet

- The live bench run (#312) and the vibe baseline (#189): both need a subscription run and the owner's yes.
- `adopt.sh` still overwrites a child's customised `.claude/commands/mode.md` (feedback #359).

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.12.0`. Run `scripts/adopt.sh <path>`. See `docs/ADOPTION.md`.
