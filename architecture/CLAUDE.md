# shipquick_latest — architecture/ Notes

> Folder-specific notes only. Root `CLAUDE.md` standing rules still apply here.

- **`architecture-portal/` is a curated file-copy of generic architecture patterns.** It is not a git submodule. Do not run `git submodule update` here.
- **Read before deciding** — `architecture-portal/docs/` holds prescriptive ADRs by domain (AI/ML, Database, Event Brokers, API Integration, Big Data, Observability, Build/Buy, Front-End and Mobile). Check the relevant ADR before choosing a pattern.
- **Sanitized** — all brand-specific references removed. Design tokens use `<PLACEHOLDER>` values. Replace them with your brand in `docs/design-tokens.md`.
- **New architecture notes** that are not yet formal ADRs go directly in this folder, outside the `architecture-portal/` tree.
- **Usage rules** — see `architecture-portal/USAGE_GUIDE.md` for what to use directly vs reference only.
