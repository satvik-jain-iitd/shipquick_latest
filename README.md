# shipquick_latest - Material Design 3 Architecture & Process Template

A retained and generalized repository from a design system postmortem, 
ready for use as a Material Design 3 template for any future project.

## Repository Purpose
This repository contains the complete architecture and front-end design system 
sanitized to remove brand-specific dependencies and generalized for use in any project.

## Key Features
- ✅ **Material Design 3 Integration** - Ready to use M3 design tokens and components
- ✅ **Process Template** - CLAUDE.md standing rules, TDD, process trace
- ✅ **Architecture Documentation** - ADRs, component patterns, design guidelines
- ✅ **Front-End System** - React/TypeScript components with design tokens
- ✅ **Generalized** - All brand-specific content removed, replaced with placeholders

## Repository Structure

```
shipquick_latest/
├── CLAUDE.md                                    # 10 standing rules
├── README.md                                    # This file
├── docs/
│   ├── process-trace.md                         # Process trace template
│   ├── PLAN.md                                  # Part D: Process
│   ├── architecture.md                          # Architecture guidelines
│   ├── design-tokens.md                         # Material 3 design tokens
│   ├── test-cases.md                            # Gherkin test conventions
│   ├── ideas.md                                 # Ideas log template
│   └── decisions/
│       └── ADR-template.md                      # ADR template
├── .github/
│   └── workflows/
│       └── ci.yml                               # CI configuration
├── architecture/                                # Architecture (Material 3)
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── architecture-portal/                     # Vendored Material Portal
│   │   ├── docs/                                # ADRs by domain
│   │   ├── src/                                 # React/TS components
│   │   ├── package.json                         # @material/web dependency
│   │   └── __mocks__/                           # Material Symbols icons
│   └── general-index.md                 # Generalized index
└── frontend/                                    # Front-End (Material 3)
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── skills-lock.json                         # Material 3 restrictions
    └── resy_web_onboarding_journey.md           # (generalized onboarding)
```

## Material Design 3 Integration

This repository is designed to work with **Google's Material Design 3 (M3)** open-source design system.

### Design Tokens
- Primary color: `<PRIMARY_COLOR>` (replace with your brand color)
- Font: `Roboto` or `<PRIMARY_FONT>` 
- Spacing: `<SPACING_UNIT>` (4px or 8px increments)
- Colors: `<TEXT_COLOR>`, `<BG_COLOR>`, `<SUCCESS_COLOR>`, `<ERROR_COLOR>`

### Components
- Use `@material/web` npm package for web components
- `<md-button>`, `<md-text-field>`, `<md-checkbox>`, etc.
- Material Symbols for icons (SVG outline, no color fill)

### Quick Start
```bash
npm install @material/web
# Or use CDN:
<link rel="stylesheet" href="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css">
<script src="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js"></script>
```

## Architecture Overview

### Architecture Portal (Vendored)
Contains ADRs (Architecture Decision Records) by domain:
- AI/ML, Database, Event Brokers, API Integration, Big Data, Observability
- Build vs Buy Assessment, Front-End and Mobile Communications
- Design Language System Prescriptive ADR

### Component Library
React/TypeScript components organized by domain:
- Admin panel components (AdminCards, AdminHeader, AdminLayout, AdminSidebar)
- Page components (database, events, api-integration, build-buy)
- Core page layout

## Front-End & Back-End Integration

### Integration Pattern: Feature-Based

```
┌─────────────────────────────────────────────────────────────┐
│                    Feature Modules                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Front-end │  │   API Layer │  │   Back-end Service │ │
│  │   (React)   │  │   (REST/GraphQL)│ │   (Node/Python) │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│           │                    │                    │
│           ▼                    ▼                    ▼
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │   UI Components     │  │   API Calls       │  │   Business Logic   │ │
│  │   (React Components)│  │   (fetch/axios)   │  │   (Service Layer) │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Front-end → Back-end**: HTTP requests (GET/POST/PUT/DELETE)
   - Using `fetch` or `axios` with proper error handling
   - API endpoints defined in `api/` folder
   - Response parsed and state updated

2. **Back-end → Front-end**: JSON responses
   - Consistent schema defined in `api-contracts/`
   - Error responses with proper status codes
   - WebSocket for real-time updates (optional)

3. **State Management**
   - Local state: React `useState`/`useReducer`
   - Global state: Context API or Redux (optional)
   - Persistence: LocalStorage or IndexedDB

### API Contract Example

```typescript
// api/types.ts
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

export interface ErrorResponse {
  message: string;
  code: string;
  details?: string[];
}

// api/example.ts
export const getUser = async (id: string): Promise<User> => {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
};
```

### Component-API Integration Example

```typescript
// components/UserProfile.tsx
import { useEffect, useState } from 'react';
import { getUser } from '../api';

interface UserProfileProps {
  userId: string;
}

export function UserProfile({ userId }: UserProfileProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUser(userId)
      .then(data => {
        setUser(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load user:', err);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <span>Loading...</span>;
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">{user?.name}</h1>
      <p>{user?.email}</p>
    </div>
  );
}
```

## Component Integration Patterns

### 1. Presentational vs Container Components

```typescript
// Presentational Component - Only UI, no logic
function Button({ children, onClick, className }) {
  return <button className={className} onClick={onClick}>{children}</button>;
}

// Container Component - Logic + UI
function UseSaveButton({ onSave }) {
  const [saving, setSaving] = useState(false);
  
  const handleSave = async () => {
    setSaving(true);
    await onSave();
    setSaving(false);
  };
  
  return (
    <Button onClick={handleSave} disabled={saving}>
      {saving ? 'Saving...' : 'Save'}
    </Button>
  );
};
```

### 2. Component Communication (Parent-Child)

```typescript
// Parent passes data via props
<ChildValue value={parentValue} onChange={parentHandler} />

// Child emits events
<ChildComponent 
  value={parentValue} 
  onValueChange={parentHandler} 
/>
```

### 3. Global State Integration

```typescript
// Using React Context
const ThemeContext = createContext<ThemeType>('light');

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<ThemeType>('light');
  
  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
}

// Usage anywhere in component tree
const theme = useContext(ThemeContext);
```

## Process Integration

### CLAUDE.md Standing Rules (Apply to All Projects)

1. Read `docs/process-trace.md` first in every session
2. Append session steps before "done"
3. Log owner messages that change direction
4. Log every idea with `~/Desktop/SecondBrain/tools/idea.py`
5. Work from GitHub issues, branch `feat/<issue>-<slug>` from `dev`
6. TDD: failing test first, named after Gherkin scenario
7. Definition of Ready before story starts
8. ADR-NNN.md for architecture/scope changes
9. Apple-silicon native only, Python ≥ 3.12 < 3.14
10. Models in `models/`, never download at run time

### Process Trace Workflow

```
Step 1: Read docs/process-trace.md (FIRST ACTION)
Step 2: Work on story/feature
Step 3: Append session step to process-trace.md (LAST ACTION BEFORE DONE)
Step 4: Create GitHub issue from idea
Step 5: Branch: git checkout -b feat/<issue>-<slug> dev
Step 6: Write failing test first
Step 7: Implement minimal code
Step 8: PR dev → main (owner merges)
Step 9: Write docs/demos/D<n>.md
Step 10: Repeat
```

### Definition of Ready (DoR)

- [ ] Story is GitHub issue linked to epic
- [ ] Gherkin scenarios copied in
- [ ] Every scenario testable
- [ ] Persona and FR named in issue
- [ ] Dependencies listed and available
- [ ] Ponytail check written
- [ ] Owner has seen the issue

### Definition of Done (DoD)

- [ ] Tests written first and green
- [ ] Scenarios mapped to tests or matrix row
- [ ] Docs updated in same PR
- [ ] Ponytail review: nothing speculative added
- [ ] Issue closed by PR
- [ ] Journal entry written

## Material Design 3 Component Reference

### Core Components

| Component | Import | Usage |
|---|---|---|
| `MDCButton` | `import {MDCButton} from '@material/button'` | `<MDCButton>Click me</MDCButton>` |
| `MDCTextField` | `import {MDCTextField} from '@material/textfield'` | Form inputs |
| `MDCCheckbox` | `import {MDCCheckbox} from '@material/checkbox'` | Boolean options |
| `MDCRadio` | `import {MDCRadio} from '@material/radio'` | Option groups |
| `MDCSelect` | `import {MDCSelect} from '@material/select'` | Dropdowns |
| `MDCDialog` | `import {MDCDialog} from '@material/dialog'` | Modals/overlays |
| `MDCTopAppBar` | `import {MDCTopAppBar} from '@material/top-app-bar'` | App headers |
| `MDCList` | `import {MDCList} from '@material/list'` | Navigation lists |
| `MDCFab` | `import {MDCFloatingActionButton} from '@material/fab'` | CTA buttons |
| `MDCSnackbar` | `import {MDCSnackbar} from '@material/snackbar'` | Feedback messages |

### Design Token Usage

```css
/* Using CSS custom properties from Material 3 */
:root {
  --md-primary: #your-primary-color;
  --md-on-primary: #your-text-on-primary;
  --md-surface: #your-background;
  --md-on-surface: #your-text;
  --md-surface-variant: #your-alt-background;
  --md-icon: #your-icon-color;
  --md-divider: #your-divider-color;
}

/* Or using JSMDC styles */
import {styles as mdStyles} from '@material/web/typography/md-typescale-styles.js';
document.adoptedStyleSheets.push(mdStyles.styleSheet);
```

## Repository Maintenance

### Regular Updates
- Check for `@material/web` package updates
- Review ADRs when architecture changes
- Update design tokens when rebranding
- Run CI checks on every push

### Backup & Permanent Storage
- Repository located at: `/Users/satvikjain/Documents/AI_Assistant/shipquick_latest/`
- All 10 Material Components repositories in `/Users/satvikjain/Documents/AI_Assistant/material-design-system/`
- Regular git commits with descriptive messages
- Tag releases at each increment (D0, D1, D2, ...)

### Sanitization Checklist (Run Periodically)
- [ ] No `@americanexpress` references remain
- [ ] No `dls-icons` references remain
- [ ] No `Benton Sans` font references
- [ ] No hardcoded brand color values
- [ ] All tokens use `<PLACEHOLDER>` format
- [ ] All icons use Material Symbols SVG
- [ ] All folder names lowercase, no special chars
- [ ] `package.json` uses `@material/web`

## Permanent Storage Location

`/Users/satvikjain/Documents/AI_Assistant/shipquick_latest/`

This repository is designed to be:
- **Permanent** - Will remain in your Documents folder
- **General** - Works for any project type
- **Integrated** - Front-end, back-end, and process all included
- **Maintained** - Regular updates possible via git

---

**Start new projects by cloning:**
```bash
git clone <url> <your-project-name>
cd <your-project-name>
# Replace <PLACEHOLDERS> in docs/design-tokens.md with your brand values
# Follow CLAUDE.md standing rules
# Begin with D0 foundations
```