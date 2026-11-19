# ShipQuick v0.14.0 (13 Nov 2026)

A minor release (`pm/agile/RELEASE_GUIDE.md`). It adds one flag to `adopt.sh` and makes `adopt.sh --check` stricter for a project that keeps the kit on its own branch (rule 24). It comes from feedback #478: in such a project every commit on a code branch stopped with "No .pre-commit-config.yaml file was found".

## What a child gains

- **`adopt.sh --gate-files`.** On a code branch it copies the gate files from the kit branch and stages them: the hook config, the submodule pin and its `.gitmodules` entry, the two callers, `roadmap.json`, `.shipquick/features.json` and `.shipquick/roles.yml`. The one list is `scripts/gate_files.txt`. No document is written. After the commit the git hooks run on that branch (ADR-017).
- **A stricter `adopt.sh --check`.** On a code branch it fails for each gate file that is missing, differs from the kit branch, or is only on the code branch, and prints the fix. It reads the hook config and the switches from the branch you are on, never from the kit branch. A bump branch cut from the kit branch is read like the kit branch.
- **A clear line when the kit folder is empty.** The hook config starts with a `shipquick-kit` hook. In a fresh clone or a new worktree a commit stops with one line that says `git submodule update --init`. `adopt.sh` adds the hook to a config written by an older kit.
- **The no-config guard.** In a Claude Code session with the kit plugin, a command that sets `PRE_COMMIT_ALLOW_NO_CONFIG`, or a `pre-commit` call with `--allow-missing-config`, is refused like `--no-verify`. Both skip every hook.
- **For the kit's own CI:** a PR that only edits `ci.yml` no longer runs the phone jobs, and a new run of a PR cancels the old one.

## What breaks for children on the bump

- A project with no `kit_branch` in its caller: nothing. Run `adopt.sh .` once; it adds the `shipquick-kit` hook to your hook config. `adopt.sh --check` says "not adopted" until that hook is there.
- A project with a `kit_branch`: `adopt.sh --check` on a code branch now says "not adopted" until that branch carries the gate files. CI in the child does not change with this release.

## What a kit-branch child does after the bump

1. Bump on a branch cut from the kit branch, as before: `adopt.sh . --ref v0.14.0`, then `adopt.sh . --check`. Merge it into the kit branch.
2. On each code branch: `git fetch origin <kit branch>`, then `bash knowledge/shipquick_latest/scripts/adopt.sh . --gate-files` (add `--kit-branch <kit branch>` when the branch has no caller yet), then `git submodule update --init`, then commit and open a PR.
3. Run `adopt.sh . --check` on that branch and paste the output in the PR.
4. Never get past a hook that cannot start with `PRE_COMMIT_ALLOW_NO_CONFIG` or `--allow-missing-config`. Stop and tell the reviewer.

## Not yet

- CI's `adoption` job does not compare a code branch's gate files with the kit branch. Only `adopt.sh --check` on the Mac does.
- In a clone that fetched only one branch, `--check` can read a code branch as kit-branch work. Fetch all branches first.
- `--check` compares the submodule pin, not the commit the kit folder is really checked out at.
- A PR that edits the steps of a `ui-*` job in the kit's `ci.yml` needs one manual full run (`docs/PR_RULES.md` section 14).

All four are rows in `docs/follow-ups.md`.

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.14.0`. Run `scripts/adopt.sh <path>` and then `scripts/adopt.sh <path> --check`, and paste the output in the bump PR. A kit-branch child then follows the four steps above. See `docs/ADOPTION.md`.
