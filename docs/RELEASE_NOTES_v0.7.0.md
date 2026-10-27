# ShipQuick v0.7.0 (27 Oct 2026)

A minor release, so it ships as `v0.7.0` (`pm/agile/RELEASE_GUIDE.md`).

## New
- **Roles in the source.** The coder opens every pull request, dev to main too. The reviewer never opens one. In Auto mode the reviewer merges dev to main with `scripts/review_merge.sh` and the owner is not asked. In Manual and Semi the owner still merges main. The dev to main title starts with `release:`, so the gate does not ask for `Closes #n`.
- **A project-facts template.** `docs/CLAUDE.project.template.md` holds stack, folders, decisions and one pointer line.
- **adopt.sh writes the pointer.** The line `Protocol: follow <path>/CLAUDE.md` goes into the child's `CLAUDE.md`. Your own lines stay.

## Changed
- `CLAUDE.md` is the protocol only. Rules 6, 9 and 10 were project facts and are removed. Numbers stay fixed.

## For child projects
1. Move the submodule to `v0.7.0`.
2. Run `bash knowledge/shipquick_latest/scripts/adopt.sh .` to get the pointer line.
3. If your `CLAUDE.md` copies protocol rules, delete those copies. Keep only your project facts. If you relied on old rules 6, 9 or 10 from ShipQuick, copy those facts into your own `CLAUDE.md` first.
4. The mode is yours to set; this release does not change it.
