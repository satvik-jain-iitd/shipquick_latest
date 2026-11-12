# ShipQuick v0.13.3 (12 Nov 2026)

A patch release (`pm/agile/RELEASE_GUIDE.md`). It fixes three small gaps the first bumps showed. No breaking change, and no project is forced to bump: take it at your next bump.

## What a child gains

- **The pre-push hook knows the kit branch.** A project that follows rule 24 cuts its bump branch from its kit branch. With `BASE` not set, the hook now reads `kit_branch` from the caller and compares the push with that branch when the push is nearer to it than to `dev`, so a bump pushes without a hand-set `BASE` and without `SKIP`. A set `BASE` always wins. A caller whose `kit_branch` cannot be read fails the run, and a push cut from `dev` is compared with `dev` as before.
- **`adopt.sh` keeps a `mode.md` you changed on purpose.** `.claude/commands/mode.md` is written when it is missing or still equal to a kit copy, old or new. A file you changed is kept and the run says `kept      .claude/commands/mode.md (yours; differs from the kit copy)`, the way `roadmap.json` is kept. `adopt.sh --check` says nothing new about it.
- **The markdown check ignores ignored files.** `check_md_blocks.py` reads the files git knows (tracked, or new and not ignored), so a gitignored file with a broken code block no longer fails the local hook while CI passes. A new file that is not yet added is still checked.

## What breaks for children on the bump

Nothing. A project with no `kit_branch` keeps its base as before. A project whose own `mode.md` differs from the kit copy now keeps it instead of losing it.

## Not yet

- A caller with `kit_branch: main` would make the local `tdd` check read a push as a promotion (`docs/follow-ups.md`). Local hook only.

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.13.3` at your next bump. Run `scripts/adopt.sh <path>` and then `scripts/adopt.sh <path> --check`, and paste the output in the bump PR. See `docs/ADOPTION.md`.
