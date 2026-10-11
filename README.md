# shipquick_latest

A ready-to-use starter kit for building websites and web applications using Google's Material Design 3 (M3) system.

## What is this?

**shipquick_latest** is a pre-built foundation that gives you everything you need to start a web project immediately. Think of it like a "starter kit" or "toolbox" for building websites.

Inside, you get:
- A organized folder structure
- Design tools (colors, fonts, spacing)
- Ready-made user interface components
- Guidelines for how to build your project

## Who is this for?

This is for anyone who wants to build a website or web application quickly and consistently. Whether you are:
- A designer wanting to use a professional design system
- A developer wanting to start fast without building everything from scratch
- A team wanting to follow consistent patterns

## What problem does it solve?

Building a website from scratch takes a lot of time. You have to:
- Decide on colors and fonts
- Create a folder structure
- Build basic components (buttons, forms, etc.)
- Set up design rules

**shipquick_latest** already has all of this set up. You just need to customize it with your own brand colors and fonts.

## What's inside?

Here is the folder structure explained simply:

```
shipquick_latest/
├── README.md          ← This file (tells you what everything is)
├── CLAUDE.md          ← Rules to follow when working on the project
├── docs/              ← All documentation (guides, plans, decisions)
│   ├── architecture.md← How the system is organized
│   ├── design-tokens.md ← Colors, fonts, spacing values (replace with your own)
│   ├── PLAN.md        ← The step-by-step plan for building your project
│   ├── process-trace.md ← What has been done so far (updated each session)
│   └── test-cases.md  ← How to test your project
├── .github/           ← Automatic testing setup
│   └── workflows/     │   └── ci.yml   ← Runs tests automatically
├── architecture/      ← System design and portal components
│   └── architecture-portal/ ← Pre-built interface components
│       ├── docs/      ← Design records
│       ├── src/       ← React code components
│       ├── package.json ← Tool dependencies (Material Design 3)
│       └── __mocks__/ ← Test icons
├── frontend/          ← Front-end setup and patterns
│   ├── AGENTS.md      ← Rules for AI assistants
│   ├── CLAUDE.md      ← Session rules
│   ├── skills-lock.json ← Material Design 3 restrictions
│   └── resy_web_onboarding_journey.md ← Onboarding flow guide
```

## Design Tokens (Colors and Fonts)

The system uses **Design Tokens** - these are named values for colors, fonts, and spacing that you can use throughout your project.

### Current Tokens (Replace with your own):

| Token | What it is | Your brand value |
|---|---|---|
| `<PRIMARY_COLOR>` | Your main brand color | `#YourColorHere` |
| `<PRIMARY_DARK>` | Darker version of main color | `#YourDarkColorHere` |
| `<TEXT_COLOR>` | Main text color | `#YourTextColorHere` |
| `<BG_COLOR>` | Page background color | `#YourBackgroundColorHere` |
| `<PRIMARY_FONT>` | Font family for text | `YourFontName` |
| `<SPACING_UNIT>` | Base spacing size | `4` or `8` |

**To change these**: Open `docs/design-tokens.md` and replace the `<PLACEHOLDER>` values with your brand's colors and fonts.

## Material Design 3

This project uses **Material Design 3** - a design system created by Google. It provides:
- Professional, modern-looking components
- Consistent design patterns that work on all devices
- Pre-built buttons, forms, dialogs, and more

### Key Material Design 3 Components

You can use these ready-made components in your project:

| Component | What it does | How to use |
|---|---|---|
| `MDCButton` | A styled button | `<MDCButton>Click me</MDCButton>` |
| `MDCTextField` | A form input field | `<MDCTextField>` |
| `MDCCheckbox` | A check box option | `<MDCCheckbox>` |
| `MDCRadio` | Option buttons (select one) | `<MDCRadio>` |
| `MDCSelect` | A dropdown menu | `<MDCSelect>` |
| `MDCDialog` | A pop-up window/modal | `<MDCDialog>` |
| `MDCTopAppBar` | A header/app bar | `<MDCTopAppBar>` |
| `MDCFab` | A floating action button (like a plus sign) | `<MDCFab>` |
| `MDCSnackbar` | A brief message at the bottom | `<MDCSnackbar>` |

**To use these**: You need to install the Material Design package. See the Quick Start section below.

## Quick Start

### 1. Get the project

```bash
# Clone this repository to your computer
git clone <url> <your-project-name>

# Go into the project folder
cd <your-project-name>
```

### 2. Install the design tools

```bash
# Install Material Design components
npm install @material/web
```

### 3. Start building

You can now start using the components and design tokens. Here's a simple example:

```html
<!-- A primary button using your brand color -->
<button style="
  --md-primary: #YourPrimaryColor;
  --md-on-primary: #YourTextOnPrimaryColor;
">
  Click Me
</button>
```

## How to Customize for Your Brand

### Step 1: Set Your Brand Colors and Fonts

1. Open `docs/design-tokens.md`
2. Replace `<PRIMARY_COLOR>` with your main brand color (like `#0066CC`)
3. Replace `<PRIMARY_FONT>` with your font name (like `Arial` or `Roboto`)
4. Replace `<SPACING_UNIT>` with your spacing size (usually `4` or `8`)

### Step 2: Update the Color Palette

The system comes with default Material Design 3 colors. You can change these to match your brand by editing the values in `docs/design-tokens.md`.

### Step 3: Follow the Guidelines

- **Use design tokens** instead of hardcoded colors (e.g., use `var(----md-primary)` instead of `#0066CC`)
- **Use Material Components** for buttons, forms, and other UI elements
- **Follow the folder structure** - keep new files in the appropriate folders
- **Read `docs/process-trace.md`** first in every working session
- **Follow CLAUDE.md** standing rules

## Folder Structure Guide

Here's how to know where to put things:

| Folder | What goes here? | Example |
|---|---|---|
| `docs/` | Documentation, guides, plans | `architecture.md`, `design-tokens.md` |
| `architecture/` | System design and portal components | Admin panels, system architecture |
| `frontend/` | Front-end setup and patterns | React components, onboarding flows |
| `.github/` | Automatic testing and CI | Test configurations |
| `architecture/architecture-portal/src/` | Reusable code components | Buttons, forms, layouts |

## What Will You Build?

With **shipquick_latest**, you can build:
- A personal website or portfolio
- A business landing page
- An internal tool or dashboard
- A customer-facing web application
- Any website that needs a professional, consistent design

## Need Help?

- Read `docs/process-trace.md` first (this is the most important rule)
- Check `CLAUDE.md` for session rules
- Look at `docs/architecture.md` for system guidelines
- Replace design tokens in `docs/design-tokens.md` with your brand values
- Use the Material Design components listed above

## Permanent Location

This repository is stored at:
```
/Users/yourname/Documents/shipquick_latest/
```

It will remain in your Documents folder and can be cloned to start new projects.

---

## Philosophy

**shipquick_latest** is based on the belief that "All software is just Human logic written in Machine language." It provides the human logic (design systems, patterns, structure) so you can focus on writing what makes your project unique.

The name "shipquick" represents the goal: to help you ship (complete and deliver) your project quickly with a solid foundation already in place.