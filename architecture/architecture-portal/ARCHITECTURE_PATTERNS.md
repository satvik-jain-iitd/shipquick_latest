# Architecture Patterns Reference

How the reference portal was built. Patterns only, no copied code.

## What the Reference Was

A Next.js 16 + React 18 portal app. One codebase serving docs and dashboards.

| Layer | Pattern |
|---|---|
| Pages | File-based routing, one folder per domain |
| Data | Markdown/MDX files read at build time |
| API | Thin Next.js route handlers (auth, search, proxy) |
| UI | Shared layout, per-domain page components |
| State | React context for theme, query lib for server data |

## Backend Patterns by Domain

### Database
- See `docs/Database/`. Pattern: one ADR per decision, schema changes reviewed.

### Event Brokers and Messaging
- See `docs/Event-Brokers-and-Messaging/`. Pattern: async first, schema registry, dead-letter queues.

### API Integration
- See `docs/API-Integration-Platforms/`. Pattern: gateway in front, versioned contracts, sandbox for partners.

### Big Data and Analytics
- See `docs/Big-Data-&-Analytics/`. Pattern: batch and stream kept separate, one catalog.

### Observability and Auditability
- See `docs/Application-Observability-&-Auditability/`. Pattern: trace every request, log structured events.

### AI and ML
- See `docs/AI~ML/`. Pattern: models versioned like code, evals before deploy.

### Build vs Buy
- See `docs/BuildBuy-Overview/`. Pattern: score build, buy, reuse on cost, control, speed. Template in folder.

### Front-End and Mobile
- See `docs/Front-End-and-Mobile-Communications/`. Pattern: one design system, Material Design 3 tokens shared across web and mobile.

## Frontend Patterns

- Presentational vs container components.
- Parent passes data via props, child emits events.
- Global state only for theme and auth.
- Design tokens, never hardcoded colors.

## What to Build From This

1. Pick one domain per story.
2. Read its ADR first.
3. Write failing test, then least code.
4. Record decision in `docs/decisions/ADR-NNN.md`.
