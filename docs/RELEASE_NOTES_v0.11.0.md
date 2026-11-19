# ShipQuick v0.11.0 (10 Nov 2026)

A minor release, so it ships as `v0.11.0` (`pm/agile/RELEASE_GUIDE.md`).
The kit now measures itself, and its rules reach every session and subagent through a plugin.

## New

- **Rules at runtime.** A hook plugin (`plugin/`) injects the mode and ten load-bearing rules at session
  start and at subagent start, adds a codebase map, warns about edits to protected paths in auto mode,
  warns about new scratch markdown files, blocks `git --no-verify` and `core.hooksPath`, and guards
  against loops and runaway cost (#313, #314, #315, #320, #321, #322).
- **New CI checks.** The rule-copy canary (#316), the TDD evidence check (#319), the workflow security
  lint (#325) and the shortcut ledger, warn only (#327). The same checks run in `scripts/check_local.sh`.
- **Bench.** A selftest harness, ten logic tasks, a cell runner and a report with a fixed-seed
  confidence interval (#311, #331, #312). The live paid run was cancelled by the owner.
- **Review shape.** A finding has a fixed shape, and an approval needs a `Verdict` and a `Not checked` line (#317, #318).
- **Story size.** A user story needs a `Done when:` line, and an L or XL size warns (#310).
- **Component library gate (S8, S9).** A custom component needs a `component-request` with the owner's
  recorded yes (#186); `adopt.sh --platforms android,ios[,web]` (#187).
- **ShipQuick Desk.** A localhost server and page (#307), with a spend column (#323).
- **Release gate.** `scripts/release.sh vX.Y.Z` tags only when the notes, the gate and the tag agree (#324).
- **Adopt `--check` reads the Ponytail plugin switch** (#326).

## What breaks for children on the bump

The workflow children call (`checks.yml`) gained two jobs, and `adopt.sh` changed.

1. **A new required job, `rule-copies`, is in the gate (#316).** A child's `CLAUDE.md` must carry the kit rule
   block between `<!-- shipquick-rules:start -->` and `<!-- shipquick-rules:end -->`, unchanged.
   Fix: run `bash knowledge/shipquick_latest/scripts/adopt.sh .`. It writes or refreshes the block and keeps the rest of the file.
   Broken markers stop `adopt.sh` and leave the file alone; repair them by hand, then run it again.
2. **A new job, `component-registry`, is in the gate (#186).** It reads `ui/registry.json`. A child with no registry passes.
   A child with custom components needs the owner's recorded yes on each request issue.
3. **`adopt.sh --check` now also reads the Ponytail switch (#326).** Locally it fails when the plugin is not enabled in the
   Claude settings; it prints the two install lines. In CI it only warns.

## Not yet

- A live bench run (#312, cancelled by the owner as a paid run).
- Generated files such as `.d.ts` and `.min.js` are not skipped by the codebase map.
- The iOS own-family rule (#285), the compile proof against real Compose and SwiftUI (#217), and a design system board (#188) and vibe tests (#189).

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.11.0`. Run `scripts/adopt.sh <path>`. See `docs/ADOPTION.md`.
