# Design System

Complete Material Design 3 integration guide.

## What We Follow

Google Material Design 3 (M3). Open source, Apache 2.0. One system for web, Android, iOS, and Flutter.

## Where Things Live

| Need | File |
|---|---|
| Token values (colors, fonts, spacing) | `docs/design-tokens.md` |
| Platform setup guides | `design/material-design-3/` |
| Repo index (all 10 repos) | `design/material-design-3/REPOSITORIES.md` |
| Usage rules | `design/USAGE_GUIDE.md` |
| Update steps | `design/UPDATE_PROCESS.md` |
| Pattern summaries | `backend/architecture-portal/ARCHITECTURE_PATTERNS.md` |

## Platforms

| Platform | Guide | Status |
|---|---|---|
| Web | `design/material-design-3/web/` | Ready now |
| Android | `design/material-design-3/android/` | Design ready, code next |
| iOS | `design/material-design-3/ios-README.md` | Design ready, code next |
| Flutter | `design/material-design-3/flutter-README.md` | Design ready, code next |

## Design Tokens

Same tokens work everywhere. Replace placeholders in `docs/design-tokens.md` with your brand.

| Token | Purpose |
|---|---|
| `<PRIMARY_COLOR>` | Main brand color |
| `<PRIMARY_FONT>` | Interface font |
| `<SPACING_UNIT>` | Base spacing (4px or 8px) |
| `<TEXT_COLOR>`, `<BG_COLOR>` | Text and background |

## Options We Considered

| Option | Verdict |
|---|---|
| Material Design 3 | Chosen. Open, cross-platform, ready components. |
| Older Material versions | Superseded by M3. |
| Platform-only systems | Single platform each. Rejected for multi-platform goal. |
| Custom system from scratch | More work, less consistency. Rejected. |

## Rule

Read `design/USAGE_GUIDE.md` before using anything. Patterns are knowledge, code is property.

Before any screen, frame or canvas work, read `docs/DESIGN_PROCESS.md` (the rules, dated).
