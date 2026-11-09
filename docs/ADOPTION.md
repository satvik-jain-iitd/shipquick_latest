# Adoption is never silent

Story #124, raised by GoServe: it carried the ShipQuick submodule for 19 days with zero checks wired, and nobody noticed. Two layers close that gap.

## Layer 1: the child's own CI fails when it is not wired

`scripts/adopt.sh <child-path>` writes `.github/workflows/shipquick-call.yml`, a caller pinned to the exact commit of `knowledge/shipquick_latest` at adoption time:

```yaml
jobs:
  shipquick-checks:
    permissions:
      contents: read
    uses: satvik-jain-iitd/shipquick_latest/.github/workflows/checks.yml@<SHA>
    with:
      shipquick_ref: <SHA>
```

`.github/workflows/checks.yml` (the reusable workflow this calls) runs every PR gate a child needs — team block, `Closes #n`, design-first, UAT on main, release freeze, environments — plus one more job, **adoption**, that runs first and fails loudly when:
- the caller's pin (`shipquick_ref`) does not equal the commit the child's `knowledge/shipquick_latest` submodule is actually at, or
- the child's `.pre-commit-config.yaml` carries no ShipQuick hooks.

Either failure prints the one command to fix it: `bash knowledge/shipquick_latest/scripts/adopt.sh .`.

The same verdict runs locally and before a commit ever reaches GitHub: `bash knowledge/shipquick_latest/scripts/adopt.sh . --check` prints "adopted" or "not adopted: <why>" and exits 1 when not adopted.

## Layer 2: a child with no caller at all

Layer 1 only fires once a child is wired enough to have the caller running. A child that never ran `adopt.sh`, or deleted the caller, has no CI of its own to fail. `docs/children.md` is the registry (one `owner/repo` per line, optionally followed by `private`); `scripts/adoption_scan.py`, run daily by `.github/workflows/adoption-scan.yml`, reads it and opens one `feedback` issue **in this repo** for any child whose default branch has no `shipquick-call.yml`, or pins a ShipQuick commit more than 14 days old. It reuses an existing open issue (comments instead of opening a second one) for the same child.

**Private children.** The workflow's own `github.token` can only ever read this repo, never someone else's private one. A line in `docs/children.md` marked `private` is read instead with the `SHIPQUICK_CHILD_TOKEN` secret — a fine-grained GitHub PAT, scoped to that repo only, with `Contents: read` and `Metadata: read` and nothing else. Set it once: `gh secret set SHIPQUICK_CHILD_TOKEN -R satvik-jain-iitd/shipquick_latest` (same build account, pasting the fine-grained PAT). With no secret set, or when the token gets a 404 or 403, a private child files nothing — that answer would otherwise look exactly like "not adopted," and a false feedback issue is worse than a skip. But a skip is never silent (story #260): the run ends with `summary: <n> skipped` and one line per child, `skipped <repo>: private, no token (...)` or `skipped <repo>: private, cannot read it with SHIPQUICK_CHILD_TOKEN (404 or 403)`.

## Rule-24 children (story #225)

Some children keep `main` small. Only the code that runs goes there (rule 24). The submodule and the rule files live on another branch, for example `dev` or `documents`. We call it the kit branch.

Such a child puts only one file on `main`: `.github/workflows/shipquick-call.yml`. That file names the kit branch:

```yaml
    with:
      shipquick_ref: <SHA>
      kit_branch: dev
```

Write it with `bash knowledge/shipquick_latest/scripts/adopt.sh . --kit-branch dev`. Run it on the kit branch. Then copy only the caller file to `main`.

**The kit branch must be protected.** Its roles file says who may code and who may review. A direct push could add a name to it. So protect the kit branch on GitHub, and require pull request reviews there. `adopt.sh --check` and the daily scan both read `branches/<kit branch>/protection`. They fail when the branch has no protection, or when it does not require pull request reviews. For a private child, the `SHIPQUICK_CHILD_TOKEN` also needs `Administration: read` to see the protection.

`kit_branch` must be a plain branch name. A trailing `# comment` is fine. A `${{ ... }}` expression is refused. One script reads it for everyone: `scripts/kit_branch.py`.

If you run `adopt.sh` again without `--kit-branch`, it keeps the kit branch your caller already names.

What changes when `kit_branch` is set:
- The adoption job reads the submodule pin and `.pre-commit-config.yaml` from the kit branch.
- The roles job reads `.shipquick/roles.yml` from the kit branch. So does `scripts/review_merge.sh` in auto mode.
- A job that runs on the kit branch itself still reads its own commit. So a PR that moves the pin is checked against its own change.
- The rule-37 check still runs. The pin must be merged into ShipQuick `dev` or `main`, or be a tag.
- `adopt.sh . --check` prints one line for the caller's branch and one for the kit branch.
- The daily scan also checks the kit branch: the submodule there must match the caller's pin, and the hooks must be there.

What stays the same:
- With no `kit_branch`, everything works as before.
- A release freeze still lives on `main` (`.shipquick/freeze`). `freeze.sh` writes it there.

## The gate must be a required check (story #260)

A caller that runs is not enough. If `shipquick-checks / gate` is not a required check, a red gate does not stop a merge. So the child's default branch must require it.

`adopt.sh` prints the one command that does this. It never runs it. A repo admin runs it once:

```bash
echo '<ruleset JSON>' | gh api -X POST repos/<owner>/<repo>/rulesets --input -
```

The command makes a ruleset named `shipquick gate` on `~DEFAULT_BRANCH`. We use a ruleset, not `PUT .../branches/<b>/protection/required_status_checks`, for two reasons:
- It works when branch protection already exists, and when it does not. The PUT gives 404 on a branch with no protection.
- It adds the gate next to the checks the child already requires. The PUT replaces that whole list.

A second run of the command gets an error that the name is taken. That is safe: the first ruleset stays.

The ruleset pins the gate to the GitHub Actions app (`integration_id: 15368`). Without that pin, anyone who may post a commit status could post one named `shipquick-checks / gate` and pass it.

`adopt.sh . --check` reads both places: `branches/<default>/protection` and `rules/branches/<default>`. The gate counts only with its exact name and the Actions app (`checks[].app_id` in branch protection, `integration_id` in a ruleset). When the gate is in neither, it prints `not adopted: gate not required on <branch>: ...` with the command, and exits 1. When the rules read gets a 403 or 404, it prints `cannot read rules (403/404) ...` and exits 1 too. Reading branch protection needs `Administration: read`. Without it, only rulesets are seen. That is one more reason to use the ruleset.

A private repo on GitHub Free cannot enforce rulesets or branch protection. Such a child needs a paid plan, or it stays "gate not required".

## Checklist for each child

Do these in order, in the child repo. One step at a time.
1. Bump the submodule to the release tag: `git -C knowledge/shipquick_latest fetch --tags && git -C knowledge/shipquick_latest checkout <release tag>`, then `git add knowledge/shipquick_latest`.
2. Run `bash knowledge/shipquick_latest/scripts/adopt.sh . --ref <release tag>`. A rule-24 child adds `--kit-branch <branch>` and runs it on that branch.
3. Commit and push the files through a PR. A rule-24 child also copies `shipquick-call.yml` to `main` in a PR.
4. Run the command `adopt.sh` printed, to make `shipquick-checks / gate` a required check.
5. If the caller names a kit branch, protect that branch and require pull request reviews there.
6. A private child: add a fine-grained token that can read it to ShipQuick's `SHIPQUICK_CHILD_TOKEN`, or the daily scan names it as skipped.
7. Wait for one PR whose `shipquick-checks / gate` is green. Then run `adopt.sh . --check`. It must print `adopted`.

## Adding a child

Add its `owner/repo` to `docs/children.md` once (a one-line PR to ShipQuick, or let the owner do it). Add `private` only when `gh repo view` says it is private. Write one `# <name>: <what GitHub shows>. Next: <step>` note above its line. Then follow the checklist above.

## The offline vendor backup

A child never fetches the vendor backup. It is a private repo, read only by the kit's own CI with a token. It fetches the ShipQuick submodule commit and nothing else. ShipQuick keeps
a copy of its pinned npm and Compose packages in another repo, `satvik-jain-iitd/shipquick-vendor-backup`, in case a source
goes closed. A clone or a submodule update never fetches it, so nobody downloads its 286 MB.
Read `docs/VENDOR_BACKUP.md`.
