# Usage Guide

What to use directly, what to reference only, what to skip.

## Use Directly

These files are generic. Copy, adapt, ship.

| File | Use |
|---|---|
| `docs/Database/` | Database ADR patterns |
| `docs/Event-Brokers-and-Messaging/` | Event streaming patterns |
| `docs/API-Integration-Platforms/` | API gateway and contract patterns |
| `docs/Big-Data-&-Analytics/` | Analytics patterns |
| `docs/Application-Observability-&-Auditability/` | Monitoring patterns |
| `docs/AI~ML/` | AI and ML patterns |
| `docs/BuildBuy-Overview/` | Build vs buy templates |
| `docs/Front-End-and-Mobile-Communications/` | Design system patterns |
| `ARCHITECTURE_PATTERNS.md` | Pattern summaries |
| `../../docs/design-tokens.md` | Token values, replace placeholders |

## Reference Only

Study the idea, write your own code. Never copy.

| Source | Study |
|---|---|
| Reference portal `src/app/` | Page and layout structure |
| Reference portal `src/app/api/` | Thin API route shape |
| Reference portal `src/components/` | Shared component splits |
| Reference portal `src/hooks/` | Custom hook splits |
| Reference portal `src/utils/` | Utility splits |
| Reference portal `src/context/` | Provider splits |

Reference lives outside this repo in a temp folder. It is not committed here.

## Skip

Do not use, do not copy.

| Item | Why |
|---|---|
| Brand icon packages | Licensed, brand-specific |
| Internal SSO and certs | Security, not portable |
| Deploy pipelines and helm charts | Infra-specific |
| Static brand assets | Copyright risk |
| Archive indexes and CSVs | Internal data |

## Rule

Patterns are knowledge. Code is property. Take the first, write the second yourself.
