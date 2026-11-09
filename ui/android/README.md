# ui/android/: the Android library

This folder is the kit's Android library (rule 38, ADR-012 "Where it lives").
The library is Google's own Jetpack Compose Material 3. We use it as Google ships it.
We never wrap it or redraw it.

## What is here

- `templates/`: five screen templates in Kotlin. Each one uses only Material 3 parts and `MaterialTheme`.
  - `SignInTemplate.kt`: email, password, and one sign-in button.
  - `ListTemplate.kt`: a top bar, rows in a `LazyColumn`, one add button, and an empty state.
  - `DetailTemplate.kt`: one item, with the main action in a bottom bar.
  - `SettingsTemplate.kt`: a switch row, a one-of-many choice, and sign out behind a confirm dialog.
  - `StepFlowTemplate.kt`: steps like onboarding. It follows `docs/DESIGN_PROCESS.md` section 12.

The docs for each part live in `ui/components/<Name>/`. Look one up with
`bash scripts/ui.sh docs android-<name> --dense` (for example `android-textfield`).
The full list of 30 parts, counted from Google's page, is `docs/research/android-m3-components.md`.

## How a child app uses a template

1. Copy the template file into your app's own screen folder.
2. Change the package name, the function name and the words.
3. Keep the parts. Do not swap a Material 3 part for a hand-drawn one.
   If no part fits, file a `component-request` and stop (rule 38).
4. Colours and type come from `MaterialTheme`. Your theme fills it from `design/tokens.json`.

The templates name the spacing tokens in a comment (16dp is `spacing.md`, 24dp is `spacing.lg`).
They are not compiled yet. A Gradle build comes with stories S6 and S7, when the owner installs the tools.
Using this folder as a Gradle build with `includeBuild("knowledge/shipquick_latest/ui/android")` is story S9.

## What is checked now

`tests/test_android_templates.py` scans the templates. It fails on `Canvas(`, `drawBehind`, `Color(0x`,
a custom `Shape` class, or a Material 2 import (`androidx.compose.material.`; the icon set is allowed).
It also checks the step flow: the filled button comes last, and the screen uses `imePadding()`.
Lint takes over this job in story S7.
