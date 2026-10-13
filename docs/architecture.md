# shipquick_latest: Architecture Guidelines

## Material Design 3 Integration

This repository is built to work with **Google's Material Design 3 (M3)** open-source design system.

### Design Tokens (Replace `<PLACEHOLDERS>` with Your Brand)

| Token | Material 3 Default | Your Value |
|---|---|---|
| `<PRIMARY_COLOR>` | `#3B82F6` (Blue-500) | Your primary brand color |
| `<PRIMARY_DARK>` | `#2563EB` (Blue-600) | Your primary dark variant |
| `<TEXT_COLOR>` | `#1F2937` (Gray-800) | Primary text color |
| `<BG_COLOR>` | `#FFFFFF` (White) | Main background |
| `<BG_ALT>` | `#F3F4F6` (Gray-100) | Alternative background |
| `<SUCCESS_COLOR>` | `#10B981` (Green-500) | Success states |
| `<ERROR_COLOR>` | `#EF4444` (Red-500) | Error states |

### Typography
- **Font Family**: `Roboto` (or `<PRIMARY_FONT>`)
- **Font Size Base**: `16px`
- **Font Size Large**: `24px`
- **Font Weight Normal**: `400`
- **Font Weight Bold**: `700`

### Spacing System
- **Spacing Unit**: `4px` (or `<SPACING_UNIT>`)
- **Spacing 1**: `4px` (0.25x)
- **Spacing 2**: `8px` (0.5x)
- **Spacing 3**: `16px` (1x)
- **Spacing 4**: `24px` (1.5x)

### Shape (Corner Radius)
- **Radius Small**: `4px` (buttons, inputs)
- **Radius Medium**: `8px` (cards, containers)
- **Radius Large**: `12px` (modals, complex components)

### Shadow System
- **Shadow Small**: `0 1px 2px rgba(0,0,0,0.05)`
- **Shadow Medium**: `0 2px 4px rgba(0,0,0,0.1)`
- **Shadow Large**: `0 4px 8px rgba(0,0,0,0.12)`

### Icon System
- **Icon Library**: Material Symbols (outline SVG, no color fill)
- **Icon Size**: Inherit from parent container
- **Icon Color**: `currentColor` (inherits text color)
- **Accessibility**: Include `aria-label` for screen readers

### Breakpoints (Responsive)
- **XSmall**: `<640px` (phones)
- **Small**: `≥640px` (small devices)
- **Medium**: `≥768px` (tablets)
- **Large**: `≥1024px` (laptops)
- **XLarge**: `≥1280px` (desktops)
- **2XLarge**: `≥1536px` (large desktops)

## Architecture Overview

### Module Structure
```
shipquick_latest/
├── models/              # AI models (gitignored, shipped in zip)
├── scripts/             # One script per OS (macos/, windows/)
├── docs/                # All documentation
├── .github/             # CI and GitHub config
├── backend/             # Backend architecture and patterns
│   └── architecture-portal/  # Vendored portal (Material 3 tokens)
└── frontend/            # Front-End (Material 3)
    └── UI components (React/TypeScript)
```

### Key Architecture Principles

| Principle | Description | Your Implementation |
|---|---|---|
| **Modular design** | Components can work independently | Start with 2-3 modules for MVP |
| **Offline-first** | No network calls at runtime | Models in zip |
| **Material 3** | Use Material Design 3 system | Replace `<PLACEHOLDERS>` with your brand |
| **Apple-silicon native** | arm64 only, no Rosetta | Python ≥ 3.12 < 3.14 |
| **One process** | Single thread + audio callback | Like a single-process audio callback app |
| **Resilient design** | Graceful failure, not crashing | Basic error handling |

### Material 3 Design Token Zones

| Zone | Purpose | Your Value |
|---|---|---|
| **Color** | Brand identity and status | `<PRIMARY_COLOR>`, `<ERROR_COLOR>` etc. |
| **Typo** | Text hierarchy and readability | `<PRIMARY_FONT>`, `<TEXT_COLOR>` |
| **Space** | Layout and breathing room | `<SPACING_UNIT>` |
| **Shape** | Visual softness and consistency | `<SHAPE_SMALL>`, `<SHAPE_MEDIUM>`, `<SHAPE_LARGE>` |
| **Elevation** | Depth and hierarchy | Shadow definitions |
| **Icon** | Visual navigation and recognition | Material Symbols |

### PWA → Mobile Workflow (Recommended)

**Phase 1: Progressive Web App (start here)**
- Build web application first using Material 3 components
- Use responsive design that works in browser
- Test on desktop and mobile browser
- Key files: `index.html`, `styles.css`, `app.js`
- Save to `docs/demos/D0.md` when working

**Phase 2: Mobile Application (later)**
- Take PWA idea, build with Flutter or React Native
- Share code between web and mobile
- Key: Most logic stays the same, just UI changes
- Save mobile demos separately

**Why this order?**
- PWA is faster to build (one codebase)
- You get mobile browser testing for free
- Then mobile app is just "make it native"
- Matches your: "pahle PWA, phir mobile" requirement

### Getting Started (Non-technical)

1. **Clone shipquick_latest**: `git clone <url> <your-project-name>`
2. **Customize identity**:
   - Open `CLAUDE.md`, replace project name
   - Open `docs/design-tokens.md`, set `<PRIMARY_COLOR>`, `<PRIMARY_FONT>`, `<SPACING_UNIT>`
   - Review `docs/architecture.md` and adjust modules for your needs
3. **First session**:
   - Read `docs/process-trace.md` (first action of every session)
   - Create `docs/discussions/2026-10-11.md` (today's date)
   - Log first idea to `docs/ideas.md` and `~/Desktop/SecondBrain/tools/idea.py`
4. **Start building (PWA first)**:
   - Build web application in `web/` folder
   - Follow the Gherkin tests in `docs/tests/test-cases.md`
   - Demo increment: D0 (foundations), D1, D2, ...
   - Later: Take PWA idea to mobile (Flutter/React Native)
   - Update `architecture.md` to add mobile module

## What Stays vs Changes

| Stays Exactly Same (for every project) | Changes Per Project |
|---|---|
| CLAUDE.md 10 standing rules | Project name (`<PROJECT_NAME>`) |
| Process trace format | Primary color and font |
| Branching strategy (`main → dev → feat/`) | Architecture modules |
| TDD: failing test first | Design tokens values |
| Demo increments (D0, D1, D2, ...) | PWA → mobile workflow timing |
| Idea logging and discussion tracking | Scale (MVP vs full production) |
| Apple-silicon native only rule | |
| Models in zip, never download at run time | |

## Material Design 3 Replacement Summary

| Legacy DLS Element | Material 3 Replacement | Action |
|---|---|---|
| `@enterprise/dls-icons` | Material Symbols (SVG outline) | **REPLACE** |
| `text-primary` class | `md-primary` or `<PRIMARY_COLOR>` | **REPLACE** |
| `text-on-surface` class | `md-on-surface` or `<TEXT_COLOR>` | **REPLACE** |
| `Benton Sans` font | `Roboto` or `<PRIMARY_FONT>` | **REPLACE** |
| 8px spacing | 4px base (8px grid) | **REPLACE** |
| DLS component mocks | Material component mocks | **REPLACE** |
| Legacy design tokens | Material 3 design tokens | **REPLACE** |

## Quick Reference: Material Design 3 Color Palette

| Color | Legacy Value | Material 3 Value | Your Value |
|---|---|---|---|
| Primary | `<PRIMARY_COLOR>` | `#3B82F6` (Blue-500) | `#XXXXXX` |
| Primary Dark | `#00509E` | `#2563EB` (Blue-600) | `#XXXXXX` |
| Text | `#1374D4` | `#1F2937` (Gray-800) | `#XXXXXX` |
| Background | `#FFFFFF` | `#FFFFFF` (White) | `#XXXXXX` |
| Success | `#34A853` | `#10B981` (Green-500) | `#XXXXXX` |
| Error | `#EA4335` | `#EF4444` (Red-500) | `#XXXXXX` |

---

## Material Symbols Icons (Outline, No Color)

| Icon Name | SVG Outline Code |
|---|---|
| `home` | `<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8l-7-5-7 5v8z"/></svg>` |
| `search` | `<svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 1 0-.7.7l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.99S7.01 6 9.99 6s2.98 2.01 2.98 4.99-1.34 2.98-2.98 2.98z"/></svg>` |
| `user` | `<svg viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>` |
| `logout` | `<svg viewBox="0 0 24 24"><path d="M13 5h-2v8h2zM17 5h-2v8h2zM21 5h-2v8h2zM3 5h-2v8h2z"/></svg>` |
| `settings` | `<svg viewBox="0 0 24 24"><path d="M19.14 12.94c.04-.3.06-.61.06-.94s-.02-.64-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.42-.48-.42h-3.84c-.24 0-.44.18-.48.42l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.2-.08.47.12.61l2.03 1.58c-.04.3-.06.61-.06.94s.02.64.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.04.24.24.42.48.42h3.84c.24 0 .44-.18.48-.42l.36-2.54c.59-.24 1.13-.57 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.2.08-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>` |

## CI Configuration

The `.github/workflows/ci.yml` runs pytest on every push to `dev` and pull request to `dev`. It uses Python 3.12 and uploads test results as artifacts.

## Design Token Replacement Guide

When customizing for your project:

1. **Open `docs/design-tokens.md`**
2. **Replace all `<PLACEHOLDER>` values** with your project-specific assets
3. **Keep the 8px spacing increment system** for consistency
4. **Choose 1 primary font** and stick with it throughout
5. **Use the color tokens** for consistent branding
6. **Update `docs/design-tokens.md`** when making design decisions (link to ADRs)
7. **Reference tokens** in your CSS/design system using the token names

Example CSS usage:
```css
/* Using design tokens in your CSS */
.button-primary {
  background-color: var(--<PRIMARY_COLOR>);
  color: var(--<TEXT_COLOR>);
  padding: var(--<SPACING_2>);
  font-family: var(--<PRIMARY_FONT>);
  font-size: var(--<FONT_SIZE_BASE>);
}

.heading-primary {
  color: var(--<PRIMARY_COLOR>);
  font-size: var(--<FONT_SIZE_HEADING>);
  margin-bottom: var(--<SPACING_3>);
}
```

---

**Replace all `<PLACEHOLDER>` values** with your project-specific assets before starting development.

| Inspired by: Material Design 3 design tokens (open source, Apache-2.0 license).