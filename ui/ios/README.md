# ui/ios: the iOS library (ShipQuickUI)

This folder is a Swift package, `ShipQuickUI`. It holds screen templates.
Every template uses only Apple's own SwiftUI controls. Rule 38 says why.
It has no dependencies.

## The templates

| File | Screen | Built from |
|---|---|---|
| `templates/SignInTemplate.swift` | Sign in | `Form`, `TextField`, `SecureField`, `Button` |
| `templates/ListTemplate.swift` | A list that opens a detail | `List`, `NavigationLink`, `Label`, `searchable`, `ContentUnavailableView` |
| `templates/DetailTemplate.swift` | One item | `Form`, `LabeledContent`, `ShareLink`, `confirmationDialog` |
| `templates/SettingsTemplate.swift` | Settings | `Form`, `Toggle`, `Picker`, `NavigationLink`, `alert` |
| `templates/StepFlowTemplate.swift` | A step flow | `ProgressView`, `Image`, `TextField`, `Button` |

The step flow follows `docs/DESIGN_PROCESS.md` rule 12.
The filled main button is last, at the bottom, in the same place on every step.
The bordered button sits above it.
The bar is a bottom safe-area inset, so it rides above the keyboard.

## How a child uses them

1. Look the part up first: `bash knowledge/shipquick_latest/scripts/ui.sh docs ios-<name> --dense`.
   The list of Apple's parts is in `docs/research/ios-swiftui-components.md`.
2. Copy the nearest template into the app. Change only the content: words, data, actions.
3. Never add a custom `Shape`, `Color(red:)`, a number in `.padding(...)`, a `Canvas`, or a `UIView` subclass.
   If no SwiftUI part fits, file a `component-request` and stop (rule 38).

Adding the package to a child's Xcode project is story S9.
It will add `.package(path: "knowledge/shipquick_latest/ui/ios")`.

## What is not here yet

- Tokens: `Tokens.swift` comes from `design/tokens.json` in story S6. Until then the templates use the system
  spacing (`.padding()` with no number) and system colours.
- Snapshots: a later story (#219). A text scan also checks the templates (`tests/test_ios_templates.py`).

## What CI compiles (story #217)

Job `ui-ios-compile` runs `xcodebuild` for generic iOS on Xcode 16.4 when `ui/**` changes.
It compiles `templates/` and `proof/ApiProof.swift`. `scripts/ui_proof.py` writes the proof from the contracts:
it calls every component with every prop its contract names. CI compiles only; it runs nothing.
- `Package.swift` lists iOS only. So `swift build` on a Mac builds for macOS and fails on iOS-only calls.
  CI must build with `xcodebuild -scheme ShipQuickUI -destination 'generic/platform=iOS'`.

## What the scan refuses

A custom `Shape` or `ButtonStyle`, `Path`, a raw colour (`Color(red:`, `Color(hue:`, `Color(white:`), `Canvas`,
a UIKit view (`UIView` subclass, `UIViewRepresentable`), any import but SwiftUI and Foundation, and a number
written in `.padding`, `.frame`, `.cornerRadius`, `.offset`, `.system(size:` or `spacing:`.
A token reference passes, like `.padding(.top, Tokens.space2)`.

In a child, `lint/swiftlint.yml` does this job (story #185): every rule is a warning locally, and CI runs `swiftlint lint --strict`.
`tests/test_ui_lint.py` keeps it in step with this list. See `docs/ADOPTION.md`.
`bash ui/tool/ios_lint.sh` (story #218) runs both tiers on the Swift files changed against `origin/dev`: `CI=1` is strict, else it warns; the committed baseline `lint/swiftlint-baseline.json` (protected) filters old findings, and `.swiftformat` runs in lint mode.
## The tokens (story #184)

`Sources/ShipQuickUI/Tokens.swift` is written by `python3 scripts/emit_tokens.py` from `design/tokens.json`. Do not edit it.
It holds `ShipQuickTokens`: `Colors` (light and dark), `Fonts`, `Spacing`, `Radius`, `Motion`, `Haptics` and `touchTarget`.
The feel tokens match Android's. CI compiles it with the templates.

## The contract structs (story #222)

`Sources/ShipQuickUI/Contracts/<Name>.swift` is written by `python3 scripts/emit_contracts.py`, one file per
`ui/components/<Name>/<Name>.contract.json`. Do not edit them. Each holds `<Name>Props`: the contract's core props and
its `platforms.ios` props as typed fields, one nested enum per enum prop. Content slots are listed in a comment, not
stored (SwiftUI takes content as a view builder). Android props stay out; the Kotlin twin is its own story.
`python3 scripts/emit_contracts.py --check` fails when a struct is missing, stale or has no contract left; it runs in
`scripts/check_local.sh` (`ui-contracts`) and in CI. CI compiles the folder with the templates, so a type name that is
not real Swift fails the build.
