# shipquick_latest — design/ Notes

> Folder-specific notes only. Root `CLAUDE.md` standing rules still apply here.

- **`material-design-3/` is a curated file-copy of generic design docs.** It is not a git submodule. Do not run `git submodule update` here.
- **Read before deciding** — `material-design-3/` holds platform guides (web, Android, iOS, Flutter) and the repo index in `REPOSITORIES.md`. Check the relevant guide before choosing components.
- **Vendored, not submoduled** — upstream changes are pulled by re-copying, never at runtime. See `UPDATE_PROCESS.md`.
- **Sanitized** — brand-specific references removed. Design tokens use `<PLACEHOLDER>` values in `docs/design-tokens.md`.
- **New design notes** that are not yet formal ADRs go directly in this folder, outside the `material-design-3/` tree.
- **Usage rules** — see `USAGE_GUIDE.md` for what to use directly vs reference only.
