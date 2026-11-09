# ShipQuick v0.10.0 (9 Nov 2026)

A minor release, so it ships as `v0.10.0` (`pm/agile/RELEASE_GUIDE.md`).
Every public entry of Compose Material 3 and SwiftUI now has a doc that agents can look up.

## New

- **Nothing missing.** The lists come from each library's own public API: M3 1.4.0 has 319 entries
  and SwiftUI has 848. Every entry is covered by a structured field of one doc.
  Deprecated and not-on-iOS entries say "Do not use: X. Use Y."
- **Framework topics.** Widgets, notifications, pull to refresh, Swift Charts, web views and the
  other system surfaces each have one doc, served as `<platform>-<topic>`.
- **The kit guards its own docs.** In the kit's own CI (not in `checks.yml`), `check_ui_coverage.py --strict-api`
  fails on any API entry with no doc, and on Android a component counts only in a doc of its own family.
  `scripts/ui_api_lists.py` is now a protected path; this applies to kit PRs only.
- **Children are enforced, not only told.** `adopt.sh` prints the ruleset that makes
  `shipquick-checks / gate` a required check, pinned to the GitHub Actions app.
  `adopt.sh --check` fails when the gate is not required. The daily scan names every child it skipped.

## What breaks for children on the bump

The workflow children call (`checks.yml`) did not change since v0.9.0. Only the local tool changed.

1. **`bash knowledge/shipquick_latest/scripts/adopt.sh . --check` now fails when the gate is not a required check**
   from the GitHub Actions app, on the default branch (#260). It also needs a GitHub `origin` to pass.
   Fix: run the ruleset command that `adopt.sh .` prints (it carries `integration_id` 15368).
   A private repo on GitHub Free cannot enforce rulesets, so there the gate only reports until the plan changes.

## Not yet

- The iOS own-family rule (#285).
- Framework-doc names checked against a package list (#288).
- The compile proof against real Compose and SwiftUI (#217).
- The offline vendor backup (#242).
- Library first S6 to S11: tokens (#184), lint in children (#185), the component-request gate (#186),
  `adopt.sh --platforms` (#187), a design system board (#188), and vibe tests (#189).

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.10.0`. Run `scripts/adopt.sh <path>`. Run the printed ruleset command. See `docs/ADOPTION.md`.
