# Design System Usage Guide

What to use directly, what to reference only, what to skip.

## Use Directly

These files are Apache 2.0 docs. Read, adapt, ship.

| File | Use |
|---|---|
| `material-design-3/web/` | Web setup guides (intro, quick-start, theming) |
| `material-design-3/mdc-web/` | Web integration guides (frameworks, theming) |
| `material-design-3/android/` | Android setup guides (getting-started, theming) |
| `material-design-3/ios-README.md` | iOS setup overview |
| `material-design-3/flutter-README.md` | Flutter setup overview |
| `material-design-3/catalog-README.md` | Component catalog tour |
| `material-design-3/REPOSITORIES.md` | Links to all 10 repos |
| `../../docs/design-tokens.md` | Token values, replace placeholders |
| `../../docs/design-system.md` | Master design reference |

## Reference Only

Study the idea, write your own code. Never bulk-copy.

| Source | Study |
|---|---|
| Local `material-design-system/material-web/src/` | Web component source |
| Local `material-design-system/material-components-android/lib/` | Android component source |
| Local `material-design-system/material-components-ios/` | iOS component source |
| Local `material-design-system/material-components-flutter/` | Flutter widget source |
| Component API docs (`components/` folders) | Per-component props and slots |

Reference lives outside this repo in a local folder. It is not committed here.

## Skip

Do not use, do not copy.

| Item | Why |
|---|---|
| `.git/` folders | Version history, not needed |
| `CHANGELOG.md` files | Historical, not needed |
| Test and mock files | Testing code, not needed |
| CI and infra configs | Upstream ops, not portable |
| Brand assets and logos | Copyright risk |

## Rule

Patterns are knowledge. Code is property. Take the first, write the second yourself.
