# Component library: library first

CLAUDE.md rule 38. Decision: `docs/decisions/ADR-012.md`.
This works for any ShipQuick child and any stack. GoServe is only the worked example.

## Why

GoServe built every component by hand. No library was picked. So the UI was slow, and no two screens matched.
A library already has the parts. They are tested. They are accessible. Agents can look them up.
So we use the library, and we build only what it truly lacks.

## The library for each platform

| Platform | Library | How it is used |
|---|---|---|
| Android | Jetpack Compose Material 3 (Google) | Directly. Our brand through `MaterialTheme`. |
| iOS | SwiftUI (Apple) | Directly. Our brand through `Tokens.swift`. |
| Web | `@astryxdesign/core` (Meta) | Used directly, exact version pinned. Theme through `defineTheme`. CI runs `astryx doctor --built` as a failing check. |

Both apps share one tokens file, `design/tokens.json`. It holds the feel: colour, type, spacing, shape, motion, haptics and touch-target size.
So the apps feel the same, even when they look a little different.

Compose Multiplatform is not used. It draws Android parts on iOS. See ADR-012.

## The rule

1. A screen is built only from library components. It starts from a template. Layout containers are allowed.
2. No hand-drawn UI in app code. That means Canvas, a custom Shape or ButtonStyle, drawBehind,
   controls built from raw gestures, and M2 or View widgets. On native (Android or iOS), a third-party UI kit is banned too.
   The web is different: its library is Astryx.
   Lint does this from story S7. Until S9 (#187) wires it into children, the reviewer checks by hand.
3. If nothing fits, the coder files a `component-request` and stops. No stand-in is built while waiting.
4. The reviewer checks if existing components can do the job. If they can, the reviewer rejects the request and says how.
5. If they cannot, the reviewer asks the owner in one line: the screen, what is missing, why, and a picture.
6. When the owner says yes, a reviewer account posts an issue comment `Owner yes: <date> "<his words>"` and adds the label `component-approved`.
7. The coder builds it in the kit's library folder (`ui/android/` or `ui/ios/`). It comes with a doc, a contract, a preview, a snapshot, a registry row
   and a board on the canvas. Its twin on the other platform is requested at the same time.

An approved component joins the library and is never built twice.

## The request flow

```
coder  -> files a component-request (docs/templates/component-request.md), stops that part
reviewer -> can a library part do it?
            yes -> rejects, names the part and how
            no  -> asks the owner in one line
owner  -> yes (or no)
reviewer -> posts the issue comment "Owner yes:" and adds the label component-approved
coder  -> builds it in the kit's library folder (`ui/android/` or `ui/ios/`), with its twin requested on the other platform
child  -> bumps the library pin, then the screen uses it
```

The coder writes the issue body, so an `Owner yes:` line in the body never counts.
Only an issue comment by a reviewer account counts, plus the `component-approved` label added by a reviewer account.
No approved comment and label, no build. Story S8 (#186) reads exactly that, and fails a custom component without it.

## What "never hand-write" means

These four points are the rule. The tools that enforce them come in stories S3 to S8.
Until S9 (#187) wires the lint into children, the reviewer checks by hand.

1. **A screen starts as a copied template.** Once S3 lands, run `ui template <name> <path>`. The agent replaces only the content.
2. **A component is used as the library ships it.** No wrapper that rewrites it. From S7, lint refuses hand-drawn UI in app code.
3. **An approved custom component starts as a copy too.** `ui swizzle <BaseComponent>` (from S3) copies the nearest library part's
   real source into the kit's library folder, licence header included. Then only the approved change is made.
4. **Nothing ShipQuick writes replaces a library part.** ShipQuick adds only what no library has:
   the tokens bridge, the request flow, the gates and the canvas board.

## Where things live

| Place | What it holds |
|---|---|
| ShipQuick kit (submodule in every child) | The platform-neutral layer: doc schema, contracts, `design/tokens.json`, the copied Astryx CLI (`ui/cli/`), the agent block, the request flow, the checks |
| `ui/android/` in the kit (Gradle, `includeBuild`) | Generated `Theme.kt`; a `<Name>.doc.mjs` per M3 component we use (the component stays Google's); approved custom components, each swizzled from M3 source; screen templates; generated contracts; a catalog app; snapshots |
| `ui/ios/` in the kit (SPM, `.package(path:)`) | An SPM package `ShipQuickUI`: SwiftUI components, generated contracts, docs, templates, previews, snapshots |
| A web child | `@astryxdesign/core`, exact pin, its own `astryx init` agent block; CI runs `astryx doctor --built` as a failing check |

The kit is public, so both libraries are too. They hold no brand and no client data. A child needs no new submodule: it already carries the kit, and `adopt.sh --platforms` (story S9) writes the build snippet. Why one repo: ADR-012, "Where it lives".
A child's brand lives in the child, as tokens.

## The MIT copy policy

We copy Meta Astryx's agent architecture as code (MIT). We never rewrite it.

- Every copied file keeps `Copyright (c) Meta Platforms, Inc. and affiliates.` and the MIT notice.
- The upstream commit is written down next to the copy, in `ui/UPSTREAM.md`. That file also says how to pull upstream changes.
- A component swizzled from Compose M3 keeps its Apache 2.0 header the same way.
- We never use the name "Astryx" for our product.

## Worked example: GoServe

- GoServe's PWA stays as it is. It is moving to native, so it is not switched to Astryx.
- When the native work starts, its Android screens use M3 parts through `ui/android/`, and its iOS screens use SwiftUI parts through `ui/ios/`.
- Say a booking screen needs a time-slot grid. The coder first tries `FilterChip` in a `FlowRow`.
  If that cannot show a full slot, the coder files a component-request and stops. The reviewer asks the owner.
  After his yes, the grid is swizzled from the nearest M3 part. Its iOS twin is requested the same day.
- Rollout is story S13: warn-only for one sprint, then blocking.
