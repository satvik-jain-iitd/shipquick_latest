# ShipQuick v0.10.0 (9 Nov 2026)

A minor release, so it ships as `v0.10.0` (`pm/agile/RELEASE_GUIDE.md`).
Every public entry of Compose Material 3 and SwiftUI now has a doc that agents can look up.

## New

- **Nothing missing.** The lists come from each library's own public API: M3 1.4.0 has 319 entries
  and SwiftUI has 848. Every entry is covered by a structured field of one doc.
  Deprecated and not-on-iOS entries say "Do not use: X. Use Y."
- **The gate is strict.** `check_ui_coverage.py --strict-api` runs in CI. A new API entry with no doc fails.
- **Each entry has one owner.** On Android, a component is covered only by a doc of its own family,
  and each slot names only entries of its own kind.
- **Framework topics.** Widgets, notifications, pull to refresh, Swift Charts, web views and the
  other system surfaces each have one doc, served as `<platform>-<topic>`.
- **Children are enforced, not only told.** `adopt.sh` prints the ruleset that makes
  `shipquick-checks / gate` a required check, pinned to the GitHub Actions app.
  `adopt.sh --check` fails when the gate is not required. The daily scan names every child it skipped.

## What breaks for children on the bump

Each item has its one-line fix.

1. **`--strict-api` fails a child that adds or edits UI docs with an uncovered API row** (#231).
   Fix: cover the row in a structured field (`platforms`, `variants`, `supporting` or `family`) of one doc.
2. **On Android, a component row is covered only by a doc of its own family** (#231).
   Fix: give the component its own doc, or move it to its family's doc.
3. **`adopt.sh --check` fails when the gate is not a required check from the GitHub Actions app** (#260).
   Fix: run the ruleset command that `adopt.sh` prints (it carries `integration_id` 15368).
4. **A private child on GitHub Free cannot enforce rulesets** (#260). The gate then only reports.
   Fix: a paid plan, or make the repo public.
5. **New protected paths:** `scripts/ui_api_lists.py` and `scripts/kit_branch.py`.
   Fix: a PR that touches them needs the second review and the owner's yes.

## Not yet

- The iOS own-family rule (#285).
- Framework-doc names checked against a package list (#288).
- The compile proof against real Compose and SwiftUI (#217).
- The offline vendor backup (#242).
- Library first S6 to S11: tokens (#184), lint in children (#185), the component-request gate (#186),
  `adopt.sh --platforms` (#187), a design system board (#188), and vibe tests (#189).

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.10.0`. Run `scripts/adopt.sh <path>`. Run the printed ruleset command. See `docs/ADOPTION.md`.
