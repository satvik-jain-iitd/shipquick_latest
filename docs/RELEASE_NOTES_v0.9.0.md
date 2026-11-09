# ShipQuick v0.9.0 (9 Nov 2026)

A minor release, so it ships as `v0.9.0` (`pm/agile/RELEASE_GUIDE.md`).
Children can now pin a tag that holds today's gates (rule 37 needs a merged or tagged pin).

## New

- **Library first (rule 38).** Screens use library parts only. Android uses Compose Material 3.
  iOS uses SwiftUI. The web uses `@astryxdesign/core`. A custom part needs the owner's yes.
- **One lookup for agents.** `scripts/ui.sh docs android-button --dense` answers from our own docs.
  It fails closed, even where the upstream CLI only warns.
- **The Android and iOS libraries live in the kit.** `ui/android/` and `ui/ios/` hold docs,
  contracts and five templates each.
- **Coverage you can count.** The lists come from each library's own public API: M3 1.4.0 and
  Apple's SwiftUI data. Nothing is left out. Deprecated and not-on-iOS entries say "Do not use: X. Use Y."
  The coverage gate lists every gap. Family PRs close the gaps next.
- **No cross-platform leaks.** An iOS topic that names a Compose API fails, and so does the reverse.
- **Rule-24 children.** A child that keeps its kit files off `main` sets `kit_branch`.
  That branch must be protected, or adoption fails.
- **Protected PRs need two yeses.** A second review, and an owner yes line in the approval.

## Not yet

- The API gaps: the family PRs under #231 are open now. `--strict-api` turns on with the last one.
- The compile proof against real Compose and SwiftUI (#217).
- Tokens to `Theme.kt` and `Tokens.swift` (#184).

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.9.0`. Run `scripts/adopt.sh <path>`. Push. See `docs/ADOPTION.md`.
