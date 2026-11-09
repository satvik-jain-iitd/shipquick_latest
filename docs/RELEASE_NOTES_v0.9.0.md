# ShipQuick v0.9.0 (9 Nov 2026)

A minor release, so it ships as `v0.9.0` (`pm/agile/RELEASE_GUIDE.md`).
Children can now pin a tag that holds today's gates (rule 37 needs a merged or tagged pin).

## New

- **Library first (rule 38).** Screens use library parts only. Android uses Compose Material 3.
  iOS uses SwiftUI. The web uses `@astryxdesign/core`. A custom part needs the owner's yes.
- **One lookup for agents.** `scripts/ui.sh docs android-button --dense` answers from our own docs.
  It fails closed, even where the upstream CLI only warns.
- **The Android and iOS libraries live in the kit.** Docs and contracts sit in `ui/components/`.
  The topics agents read sit in `ui/integration/docs/`. `ui/android/` and `ui/ios/` hold five templates each.
- **Coverage you can count.** The lists come from each library's own public API: M3 1.4.0 and
  Apple's SwiftUI data. Nothing is left out. Deprecated and not-on-iOS entries say "Do not use: X. Use Y."
  The coverage gate lists every gap. Family PRs close the gaps next.
- **No cross-platform leaks.** An iOS topic that names a Compose API fails, and so does the reverse.
- **Rule-24 children.** A child that keeps its kit files off `main` sets `kit_branch`.
  That branch must be protected, or adoption fails.
- **Protected PRs need two yeses.** A second review, and an owner yes line in the approval.

## What breaks for children on the bump

Each item has its one-line fix.

1. **The adoption job fails any workflow job with no `timeout-minutes`** (`check_timeouts.py` in checks.yml, #154).
   Fix: add `timeout-minutes: <n>` to every job in `.github/workflows/`.
2. **A child with `docs/screens.txt` needs a `Render:` line** in a frontend approval (#153, #146).
   Fix: the reviewer writes `Render: <board> -- matches` after putting the render beside the board.
3. **A protected-path PR has a new merge route** (#180). Before, auto mode refused every protected PR outright.
   Now `review_merge.sh` merges one when the approval carries `Second review: ...` and `Owner yes: <date> "<words>"`.
   New protected paths: `CLAUDE.md`, `docs/screens.txt` and `scripts/kit_branch.py`. A `.shipquick/*` PR stays owner-only.
   Fix: add both lines to the approval, or let the owner merge.
4. **A private child's scan token needs `Administration: read`** to see branch protection (#225).
   Fix: give `SHIPQUICK_CHILD_TOKEN` that permission.
5. **A child that sets `kit_branch` needs that branch protected** (#225).
   Fix: run `scripts/adopt.sh . --kit-branch <b>` and protect `<b>` with required PR reviews.
6. **Maker and checker sessions are opt-in** (#139). Nothing breaks if `roles.yml` has no session lists.
   Fix, to turn it on: add `coder_sessions:` and `reviewer_sessions:` to `.shipquick/roles.yml`.
7. **A screen named in `docs/screens.txt` must be checked by a workflow** (`check_screens_wired.py` in the adoption job, #146).
   Fix: add a workflow step that runs `screens.sh --check`.

## Not yet

- The API gaps: the family PRs under #231 are open now. `--strict-api` turns on with the last one.
- The compile proof against real Compose and SwiftUI (#217).
- Tokens to `Theme.kt` and `Tokens.swift` (#184).

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.9.0`. Run `scripts/adopt.sh <path>`. Push. See `docs/ADOPTION.md`.
