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
CI compiles them (story #217, job `ui-android-compile`, only when `ui/**` changes). The build files here pin
Gradle 8.14.3, AGP 8.13.2, Kotlin 2.2.21 and Compose BOM 2025.10.00 (material3 1.4.0). It compiles `templates/`
and `proof/ApiProof.kt`, which `scripts/ui_proof.py` writes from the contracts: it calls every component with every
prop its contract names. CI compiles only; it runs nothing. Nothing is built on the owner's Mac.
Using this folder as a Gradle build with `includeBuild("knowledge/shipquick_latest/ui/android")` is story S9.

## What is checked now

`tests/test_android_templates.py` scans every `ui/android/templates/*.kt`.
- Imports come from an allow-list: `androidx.compose.material3`, `foundation`, `runtime` and `ui`,
  Google's icon set `androidx.compose.material.icons`, and the Kotlin stdlib. Anything else fails, Material 2 too.
- Banned patterns fail: `Canvas(`, `drawBehind`, `drawWithContent`, `Color(`, `.background(Color.`,
  `GenericShape`, `RoundedCornerShape(`, and a custom `Shape` class.
- `clickable`, `selectable`, `toggleable` and `verticalScroll` stay allowed. Google's own patterns use them.
- A call to an experimental M3 part (like `TopAppBar`) needs `@OptIn(ExperimentalMaterial3Api::class)`.
- The step flow: the filled button comes last, and the screen uses `imePadding()`.
Lint takes over this job in a child (story #185): `lint/detekt.yml` (local, warnings), `lint/detekt-ci.yml` (CI, errors)
and `lint/UiRulesKonsistTest.kt`. `tests/test_ui_lint.py` keeps them in step with the bans above. See `docs/ADOPTION.md`.
Lint takes over this job in story S7.

## The theme (story #184)

`theme/Theme.kt` is written by `python3 scripts/emit_tokens.py` from `design/tokens.json`. Do not edit it.
It holds `ShipQuickTheme` (Material 3 colours light and dark, type and shapes), and the constants `ShipQuickSpacing`,
`ShipQuickMotion`, `ShipQuickHaptics` and `ShipQuickTouchTarget`. Brand colours reach an app only through this theme.
CI compiles it with the templates.
