# Plan: one component library per platform, built the Astryx way, and no custom component without the owner's yes

## Context
- GoServe's UI was slow to build. Every component was custom, because no UI library was picked.
- GoServe is a PWA today. It will become a native Android app and a native iOS app soon.
- The owner wants both apps to **feel** the same. The look may differ a little.
- The coder must use library components as they are: the library's own code, not a rewrite.
- A custom component is built only after the owner says yes. The ask goes coder -> reviewer (qa) -> owner -> yes.
- An approved custom component joins the library. It is never built twice.
- ~~There are two new repos (Android, iOS).~~ Changed (owner, 9 Nov 2026, "haan theek hai"): the Android and iOS libraries live inside the kit, as `ui/android/` and `ui/ios/`. The kit is already a submodule in every child, so no new submodule is needed.
- Owner (9 Nov 2026): study Meta's Astryx. Use its components wherever possible. Wherever not, **copy its whole architecture**, the way it makes agents use a design system correctly.
- All of this is generic for any ShipQuick child. GoServe is only the first user.

## Decisions so far (owner, 9 Nov 2026)
- **Native, with a shared feel.**
  - Android uses Jetpack Compose Material 3 (Google, stable 1.4.0).
  - iOS uses Apple's own SwiftUI components.
  - Both share one tokens file: colour, type, spacing, shape, motion, haptics and touch-target size.
- **Where it lives (changed 9 Nov 2026):** inside the kit, `ui/android/` (Gradle, `includeBuild`) and `ui/ios/` (SPM, `.package(path:)`). One repo, as Astryx does it. A contract change and both platforms land in one PR. The empty repos `shipquick-ui-android` and `shipquick-ui-ios` are not used; archiving them is the owner's call.
- **Protected PRs:** each one gets my review, then a fresh second-reviewer agent, then the owner's one-line yes, and then I merge it. This goes into the process (S0).

## FINAL VERDICT: what we take from A, B and C (owner, 9 Nov 2026: take a thing fully, customise lightly, never hand-write)
| From | Taken | Fully? | Light customisation only |
|---|---|---|---|
| **A1. Google Jetpack Compose Material 3** (Android) | Every component, used **directly** in app code (`Button`, `TextField`, `NavigationBar`…). No ShipQuick wrappers that rewrite them. Plus Google's own M3 catalog and samples as the copy-from source. | Yes | Our brand through `MaterialTheme` (colour, type, shape), generated from `tokens.json` |
| **A2. Apple SwiftUI** (iOS) | Every standard control, used directly. Apple's sample code as the copy-from source. | Yes | Our brand through tokens (`Tokens.swift`), never a restyled copy |
| **B. Compose Multiplatform** | **Nothing.** Dropped. | — | — |
| **C1. Astryx components** (web) | `@astryxdesign/core` components and its 58 page templates, used directly in React web children | Yes | A theme (Astryx's own `defineTheme`) from our tokens; exact version pinned |
| **C2. Astryx agent architecture** (all three platforms) | Its doc schema (`*.doc.mjs`, same fields), its CLI (`component`, `docs`, `template`, `build`, `search`, `doctor`, `swizzle`, `--dense`, `--json`), its managed AGENTS.md/CLAUDE.md block with SELF-CHECK, doc guards, two-tier lint, vibe tests. **We copy the code itself (MIT), not a rewrite.** | Yes | Point the CLI at our Android and iOS doc folders. Rewrite the agent-block rules with Compose and SwiftUI words. Make `doctor` fail instead of warn. |

What "never hand-write" means, enforced:
1. **A screen starts as a copied template**, through `ui template <name> <path>`. The agent replaces only the content.
2. **A component is used as the library ships it.** Lint refuses hand-drawn UI in app code.
3. **An approved custom component starts as a copy too.** `ui swizzle <BaseComponent>` (Astryx's command) copies the nearest library component's real source into the kit's library folder (`ui/android/` or `ui/ios/`), licence header included. Compose M3 is Apache 2.0, so its source can be copied. Then only the approved change is made.
4. **Nothing ShipQuick writes replaces a library part.** ShipQuick only adds what none of them have: the tokens bridge, the request flow, the gates, the canvas board.

## All options, side by side (research 9 Nov 2026; Tier A = the vendor's own repo or docs)
| | (a) Compose M3 + SwiftUI + shared tokens | (b) Compose Multiplatform | (c) Meta Astryx |
|---|---|---|---|
| What it is | Google's Android library, Apple's iOS components | JetBrains: the same Material code on both | Meta's **React web** design system (MIT, beta 0.7.11) |
| Native Android | Yes, full | Yes, full | **Nothing** |
| Native iOS | Yes, Apple native | Material drawn on iOS; looks like Android, 9 MB+ bigger | **Canary only**, 6 SwiftUI parts, "not for production" |
| Web | No | No | **Yes**: 150+ components, 58 page templates |
| Agent support | We build it | We build it | **Best seen**: lookup CLI, a doc file per component, managed AGENTS.md block, MCP, llms.txt |
| Blocks custom UI | detekt, Konsist, SwiftLint | detekt | Its lint is private; `doctor --built` only warns |
- Astryx is truly Meta's (0.95). Its agent support is the best of the three, but only on the web (0.85).
- **Verdict:** (a) for native. Astryx's code is used directly only on the web. Its architecture is copied for all three platforms.

## The Astryx architecture we copy (source: the meta/astryx repo, read 9 Nov 2026)
MIT licence: every copied file keeps `Copyright (c) Meta Platforms, Inc. and affiliates.` and the MIT notice. We never use the name "Astryx" for our product.
1. **A doc file per component is the single source.** Astryx: `Button.doc.mjs`, typed by `doctypes/component/type.ts`. Fields: name, group, keywords, usage (what it is for), bestPractices (do and don't), accessibility (the WCAG criterion and its number), anatomy, props (types with literal values), examples, theming, related. A dense twin is written for agents, under the rule "same facts, fewer tokens".
   - Ours: the same `<Name>.doc.mjs` format and the same type file, copied. Only one field is added: `platforms: {android, ios, web}`.
2. **Contracts: one component, many platforms.** Astryx `packages/native`: the core props are portable; each platform adds its own; each web-only prop must give a reason; `sameMeaning` maps events ("onClick = a press, as in Compose"). Contract code is generated: a Kotlin data class and a Swift struct. A drift test fails when the code and the contract differ.
   - This is how we keep Android and iOS level.
3. **A lookup CLI that agents run before they write UI.** Astryx: `component --list`, `component <Name> --dense`, `docs`, `template`, `build "<idea>"` (names the template to start from), `search`, `doctor`, and `--json` on every command.
   - Ours: **Astryx's own CLI code** (`packages/cli`, MIT), vendored into the kit as `ui/cli/` and run with Node. It gets a thin config that points it at our doc folders. No Python rewrite.
4. **A managed agent block.** `init` writes one block between markers into AGENTS.md and the project's CLAUDE.md. `upgrade` refreshes it. Rules, adapted to our platforms:
   - "start every screen from a template, never from scratch";
   - "run `ui show <Name>` before you use a component";
   - "no raw `Box`/`Canvas`/`Color(0x…)` (Android), no raw `Shape`/`Color(red:)`/`.padding(13)` (iOS)";
   - a **SELF-CHECK** pass: re-read the file and swap any raw element for the component or token. Meta measured that this pass cuts raw CSS about 4 times (their number, 0.6).
5. **Screen templates.** These are full screen source per platform: sign-in, list, detail, settings, a step flow (rule 12), an empty state and an error. The agent starts from a template and replaces only the content.
6. **Doc guards in CI.** A doc that names a prop the code lacks fails. A prop type without its literal values fails. A component with no doc, no preview or no snapshot fails. (Astryx: `docPropReferences`, `docPropLiterals`.)
7. **Lint in two tiers.** Warnings locally, errors in CI (Astryx `ASTRYX_STRICT_LINT`). Unlike Astryx, our consumer purity check **fails** the build instead of warning.
8. **Vibe tests.** Fixed prompts are run through a coding agent. We count how many screens use only library components. That is our eval for the docs and the agent block (rule 10).
9. **MCP and llms.txt.** Later (S12). The CLI comes first.
- **Skipped:** Astryx's knowledge-record governance, arms B to E of its native experiment, release machinery, translations, integrations, and committing generated code by hand.

## Where things live
- **ShipQuick kit** (already a submodule in every child) holds the platform-neutral layer: the doc schema, the contracts, `design/tokens.json` with the feel, the vendored Astryx CLI (`ui/cli/`), the agent block, the request flow and the checks. The Android and iOS libraries sit beside it, in `ui/android/` and `ui/ios/` (changed 9 Nov 2026), so no other repo is needed.
- **`ui/android/` in the kit** (was the shipquick-ui-android repo):
  - the generated `Theme.kt`;
  - a `<Name>.doc.mjs` for each M3 component we use, so agents look it up (the component itself is Google's, never wrapped);
  - approved custom components only, each swizzled from M3 source;
  - screen templates built from M3 components;
  - generated contract classes, a catalog app and Roborazzi snapshots.
- **`ui/ios/` in the kit** (was the shipquick-ui-ios repo): an SPM package `ShipQuickUI`, with SwiftUI components, generated contract structs, docs, templates, Prefire and swift-snapshot-testing. Copy Astryx's Swift theme emitter and its Button (with its 44 pt tap area), keeping the MIT headers.
- **Web children (owner, 9 Nov 2026):** use `@astryxdesign/core` directly, with a pinned exact version and its own `astryx init` agent block. CI runs `astryx doctor --built` as a failing check. This closes the library pick in story #133. GoServe's PWA is not switched, because it is moving to native. A new story, **S5w**, wires this into `adopt.sh --platforms web`. Beta risk: the pin, plus a monthly check of the release notes.

## The rule (new CLAUDE.md rule 38, "Library first")
1. A screen is built only from library components and starts from a template. Layout containers are allowed.
2. Hand-drawn UI in app code is refused by lint: Canvas, a custom Shape or ButtonStyle, drawBehind, raw gesture-built controls, M2 or View widgets, third-party kits.
3. If nothing fits, the coder files a `component-request` and stops. No stand-in is built while waiting.
4. The reviewer checks whether existing components can do the job. If they can, the reviewer rejects the request and says how.
5. If they cannot, the reviewer asks the owner in one line: the screen, what is missing, why, and a picture.
6. Owner yes: the reviewer records `Owner yes: <date> "<his words>"` and the label `component-approved`.
7. The coder builds it in the kit's library folder (`ui/android/` or `ui/ios/`), with a doc, a contract, a preview, a snapshot, a registry row and a board on the canvas. Its twin on the other platform is requested at the same time.

## Stories (shipquick-dev builds; shipquick-qa reviews and merges; auto mode)
Every story runs radar first, writes the failing test first, ships one PR, and carries a milestone and an assignee. All of them sit under epic #130. Stories #133, #134 and #135 are widened, not duplicated.
- **S0. Protected-PR process.** `docs/MODES.md` and `review_merge.sh`: a protected PR merges only with a second-review line and an `Owner yes:` line in the PR. ADR in the same PR.
- **S1. ADR-012 and rule 38.** Library first, native plus shared feel, the Astryx pattern, the MIT copy policy. Plus `docs/COMPONENT_LIBRARY.md` and `docs/templates/component-request.md`. The owner merges it, since it is a rule file.
- **S2. The spec layer in the kit.** `ui/schema/component.schema.json` (copied from Astryx's doctypes and adapted), the dense-writing guide, the contract format, the doc-guard tests, and `design/tokens.json` with the feel added.
- **S3. Vendor Astryx's CLI** into `ui/cli/` (MIT headers kept, the upstream commit recorded). Point it at our doc folders. Keep its `init`/`upgrade` agent block, `swizzle`, and a `doctor` that fails. A `ui/UPSTREAM.md` says how to pull upstream changes.
  - **Changed (9 Nov 2026, story #183, three spikes):** the CLI is used as shipped from npm, pinned in `ui/tool/`, not copied (3314 files). Native parts are reference topics. See ADR-012, "What the CLI serves".
- **S4. The Android library (`ui/android/` in the kit).** Skeleton, theme, docs for the first ten M3 components we use (button, text field, list item, top app bar, navigation bar, bottom sheet, dialog, chip, card, snackbar), generated contracts with a drift test, five templates, a catalog app, Roborazzi.
- **S5. The iOS library (`ui/ios/` in the kit).** The same set and templates on SwiftUI, with Prefire and snapshots on a macOS runner.
- **S6. Token emitters.** One `tokens.json` produces Compose `Theme.kt` and Swift `Tokens.swift`, checked by a golden-file test.
- **CI (9 Nov 2026):** the Android and iOS jobs run only when `ui/android/**` or `ui/ios/**` change (path filters), each with a timeout. The macOS runner is free because the kit is public.
- **S7. Enforcement in children.** detekt `ForbiddenImport` plus a Konsist template; SwiftLint `custom_rules`. Two tiers. Fixture apps with a good screen and a bad screen.
- **S8. The request gate.** `scripts/check_component_request.py` in the kit's CI for `ui/android/` and `ui/ios/` and in `review_merge.sh`, plus a parity report.
- **S9. `adopt.sh --platforms android,ios[,web]`.** It adds no new submodule: it writes the `includeBuild` (from `knowledge/shipquick_latest/ui/android`) and SPM `.package(path: "knowledge/shipquick_latest/ui/ios")` snippet, the lint configs and the protected paths, then runs `ui init` (web children run `astryx init` as well).
- **S10. A "Design system" board on the canvas**, generated from both registries, next to Design learnings.
- **S11. Vibe tests.** Ten fixed screen prompts per platform. The score is the share of screens with no raw UI. Results go in `docs/research/experiments.md`.
- **S12 (later).** An MCP server (`search`, `get`) over the registries, and llms.txt.
- **S13 (later, rule 25 gate).** GoServe rollout when its native conversion starts: warn-only for one sprint, then blocking.

Order: S0 and S1 -> S2 -> S3 -> S4 with S5 in parallel lanes -> S6 -> S7 -> S8 -> S9 -> S10 -> S11.

## Verification
- **Fixtures:** the bad Android or iOS screen fails lint with the rule named; the good one passes.
- **Doc guards:** a doc naming a missing prop fails; a component with no doc, preview or snapshot fails.
- **Drift:** editing a contract without regenerating fails in both platform repos.
- **CLI:** `ui component Button --dense` prints the dense doc; `--json` has the `{apiVersion, type, data}` shape; `init` twice leaves exactly one block; `doctor` fails on a raw screen.
- **Request gate:** a custom row with no approved issue fails; with the label and an `Owner yes:` line, it passes.
- **adopt.sh:** on a scratch child, `--platforms android,ios` adds both pins, and `--check` prints OK.
- **Vibe test:** the baseline score is recorded before the agent block exists, then after. The block must raise it.
- **End to end:** request, owner yes, component in the library, pin bump in the child, screen uses it.

## First actions after approval
1. shipquick-dev logs the idea (rule 12, `idea.py`), adds today's direction to `docs/discussions/2026-11-09.md`, and opens S0 to S13 under epic #130.
2. shipquick-qa only delegates, reviews and merges. Protected PRs follow S0.
