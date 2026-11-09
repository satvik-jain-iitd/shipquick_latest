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
- Compiling and snapshots: a macOS CI job runs when `ui/ios/**` changes. It comes in a later story.
  Today a text scan checks the templates (`tests/test_ios_templates.py`).
