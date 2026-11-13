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

## The story job (story #175)

`checks.yml` runs `scripts/check_story.py` on every user story the PR body links (`Closes #n`): the story must say `Who does it:` and, from 10 Nov 2026, `Done when:`. The job reads the child's own issues, so it needs `issues: read`. A called workflow gets only what the caller grants, never more, and the caller `adopt.sh` writes grants it. With a caller written by hand without it, GitHub refuses the whole ShipQuick checks run at startup with `The nested job 'story' is requesting 'issues: read', but is only allowed 'issues: none'`, and no gate check appears (no job of `checks.yml` runs at all). `adopt.sh . --check` names it as `not adopted: shipquick-call.yml grants no issues: read`; a caller that grants `issues: write` passes too.

## Rule-24 children (story #225)

Some children keep `main` small. Only the code that runs goes there (rule 24). The submodule and the rule files live on another branch, for example `dev` or `documents`. We call it the kit branch.

Such a child puts the caller, `.github/workflows/shipquick-call.yml`, and the other gate files on `main` (see "Gate files on every code branch" below). The documents stay on the kit branch. The caller names the kit branch:

```yaml
    with:
      shipquick_ref: <SHA>
      kit_branch: dev
```

Write it with `bash knowledge/shipquick_latest/scripts/adopt.sh . --kit-branch dev`. Run it on the kit branch. Then, on each code branch, run `adopt.sh . --kit-branch dev --gate-files` and commit what it staged.

**The kit branch must be protected.** Its roles file says who may code and who may review. A direct push could add a name to it. So protect the kit branch on GitHub, and require pull request reviews there. `adopt.sh --check` and the daily scan both read `branches/<kit branch>/protection`. They fail when the branch has no protection, or when it does not require pull request reviews. For a private child, the `SHIPQUICK_CHILD_TOKEN` also needs `Administration: read` to see the protection.

`kit_branch` must be a plain branch name. A trailing `# comment` is fine. A `${{ ... }}` expression is refused. One script reads it for everyone: `scripts/kit_branch.py`.

If you run `adopt.sh` again without `--kit-branch`, it keeps the kit branch your caller already names.

## Gate files on every code branch (story #479, ADR-017)

The git hooks run on the branch you have checked out. They read their files from that branch. So a code branch that has no hook config stops every commit with "No .pre-commit-config.yaml file was found". Never get past that with `PRE_COMMIT_ALLOW_NO_CONFIG` or `--allow-missing-config`: both skip every hook. Stop and tell the reviewer.

The fix is a layout. A short list of gate files lives on every code branch, equal to the copy on the kit branch. We call it group A. The one list is `scripts/gate_files.txt`. `adopt.sh --gate-files` and `adopt.sh --check` both read it.

| Gate file | Who reads it, and which copy |
|---|---|
| `.pre-commit-config.yaml` | The git hooks: this branch. CI's `adoption` job: the kit branch. |
| `.gitmodules` and `knowledge/shipquick_latest` (the pin) | The git hooks run the kit's scripts from this folder: this branch. CI's `adoption` job reads the pin on the kit branch. |
| `.github/workflows/shipquick-call.yml` | GitHub runs it from the PR's branch. `check_local.sh` reads `kit_branch` from this branch. |
| `.github/workflows/roadmap-call.yml` and `roadmap.json` | The roadmap workflow runs from the default branch and reads `roadmap.json` from that checkout. |
| `.shipquick/features.json` | The hooks: this branch. A missing file means every default, so a switch that is off on the kit branch would be on here. CI reads the base branch. |
| `.shipquick/roles.yml` | The hook's `ui-registry` check: this branch. CI's `roles` job and `review_merge.sh`: the kit branch. |

Not gate files, they stay on the kit branch: `CLAUDE.md`, `.gitattributes`, `.claude/commands/mode.md`, `docs/`, `scripts/screens.sh`. The hook's `rule-copies` check reads only the kit's own `CLAUDE.md`, so it passes on a branch that has none. CI reads the child's `CLAUDE.md` from the kit branch.

How to put them on a code branch:

```bash
git fetch origin <kit branch>
bash knowledge/shipquick_latest/scripts/adopt.sh . --gate-files   # add --kit-branch <kit branch> when this branch has no caller yet
git submodule update --init
git commit -m "chore: the ShipQuick gate files on this branch"
```

It copies each gate file from the kit branch and stages it. It writes no document. A file the kit branch does not have is skipped. It prints `copied`, `replaced` or `unchanged` for each one. A path whose copy on disk is not the committed one (an edit, a new file, a gitignored file) and that the copy would overwrite stops the run, names the path, and writes nothing. In `.gitmodules` only the `knowledge/shipquick_latest` entry is written, whole, so a code branch keeps its own submodules.

The kit branch is read from `origin/<kit branch>`. A local branch is used only when origin's is not fetched, because a local one can be old. The output says which one was read.

`adopt.sh . --check` on a code branch fails for each gate file that is missing (`gate file <path> is not on <branch>`) or that differs from the kit branch (`gate file <path> on <branch> differs from kit branch <kit>`). A pin that differs prints both pins. The fix is the same for both: run `--gate-files` again. A gate file that is on the code branch and not on the kit branch fails too (`is on <branch> but not on kit branch <kit>`): remove it, or add it on the kit branch first. `--check` compares the file on disk, because that is what the hooks read; for the submodule pin it compares the index. In `.gitmodules` it compares only the `knowledge/shipquick_latest` entry. It reads the hook config and the switches from the branch you are on, never from another branch.

**How a bump reaches the code branches.** (1) Cut the bump branch from the kit branch and run `adopt.sh . --ref <tag>` there. `--check` reads such a branch at HEAD, like the kit branch, and does not compare it with the kit branch. A branch counts as kit-branch work only when the kit branch tip is one of its ancestors and none of its own commits is on another remote branch (every `origin` branch but the kit branch and its own). Any other branch is a code branch and is compared. So fetch all branches before you run `--check`. (2) Merge the bump PR into the kit branch. (3) On each code branch: `git fetch origin <kit branch>`, `adopt.sh . --gate-files`, `git submodule update --init`, commit, open a PR. Until step 3 is done `--check` on that code branch says which gate files differ.

A missing or empty `scripts/gate_files.txt` stops `--check` and `--gate-files` with exit 2 and names the file. `--check` and `--gate-files` together is a usage error.

A kit folder that is not checked out (a fresh clone, a new git worktree) stops the commit with one ShipQuick line that says `git submodule update --init`. The first hook, `shipquick-kit`, does that. `adopt.sh` adds it to a config written by an older kit, and `--check` fails until it is there.

## The milestone (story #357)

The `environments` job needs a filled `Dev link:` and `Production link:` in the project's `CLAUDE.md` once the project is past D0. It reads the project's milestone from the caller: `milestone: D2` under `shipquick_ref:` in `shipquick-call.yml`.
A caller with no `milestone:` line means unknown, so the gate keeps today's behaviour (D1: both links needed). `D0` is the only way to opt out: a project that has deployed nothing yet writes `adopt.sh . --milestone D0`.
`--milestone` takes D0 to D6; anything else is refused before a file is written. A run without the flag keeps the caller's own line, and refuses a `milestone:` line that is not exactly `milestone: D<n>` instead of dropping it.

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

## Rule copies in a child (story #316)

The kit's rules (CLAUDE.md, rule 0 to the last rule) are copied into each child's CLAUDE.md. The copy must match the kit byte for byte, once line endings and outer blank lines are ignored. A check (`scripts/check_rule_copies.py --child project/CLAUDE.md`, job `rule-copies` in `checks.yml`) fails the PR when it does not.

The child marks the copy with two lines, one above and one below the rules, each on its own line and each exactly once:

```text
<!-- shipquick-rules:start -->
0. **Mode** (owner, 26 Oct 2026). ...
...the kit rules, unchanged, from rule 0 to the end of the kit CLAUDE.md...
<!-- shipquick-rules:end -->
```

`scripts/adopt.sh` writes this block for you and rewrites it on every run, so a pin bump refreshes the copy. Run `adopt.sh` again after you bump the ShipQuick pin. What sits outside the two lines is yours and is never touched. If the lines are broken (one missing, or in the wrong order), `adopt.sh` stops before it writes anything and says so.

Where the copy lives: the check reads `CLAUDE.md` from the branch the PR touches. A rule-24 child keeps its rules on its kit branch, not on `main`, so for a PR into another branch the `rule-copies` job reads `CLAUDE.md` from the caller's `kit_branch`, the same way the `roles` job reads `roles.yml`.

The check also confirms that 11 load-bearing phrases are in the kit. They are listed at the top of `scripts/check_rule_copies.py`. Rule 33 is restated in the `shipquick-feedback` skill, so its phrase must be in both `CLAUDE.md` and `skills/shipquick-feedback/SKILL.md`.

A child without the two marker lines fails the `rule-copies` job. To fix it, run `bash knowledge/shipquick_latest/scripts/adopt.sh .` and push again.

## UI lint in a child (story #185)

A child refuses hand-drawn UI with lint. The kit ships the configs. Wiring them in is story #187, not this one.
- **Android:** copy `ui/android/lint/detekt.yml`, `detekt-ci.yml` and `UiRulesKonsistTest.kt`. detekt 1.23.8 and Konsist 0.17.3.
- **iOS:** copy `ui/ios/lint/swiftlint.yml` to `.swiftlint.yml`. SwiftLint 0.65.1.
- **Two tiers.** On a laptop every rule is a warning, so a local run reports and does not fail. In CI the same rules are errors:
  detekt reads `detekt.yml` and then `detekt-ci.yml`, and SwiftLint runs with `--strict`.
- **CI only.** Install nothing on a Mac. The kit's jobs `ui-android-lint` and `ui-ios-lint` show the exact steps.
- **Your own UI kits and modules:** add UI kits to `forbiddenPatterns` (detekt). Add your own module names to the allow-list in `no_import_outside_allowlist` (SwiftLint).
- Do not silence a rule with a disable comment. The lint does not stop one: `blanket_disable_command` flags only a disable that
  is never switched back on, and `superfluous_disable_command` flags only a disable that hides nothing. A single
  `swiftlint:disable:next` passes both. The kit's disable-comments check is what catches it: a disable comment on an added line
  fails unless the PR names an ADR that justifies it.
- The kit's fixture apps are `tests/fixtures/android` and `tests/fixtures/ios`: one good screen, one bad screen.

## The sample child walk (story #504)

The kit's own CI (the Python test job) walks a made-up child through the path a real child takes: `tests/test_sample_child_walk.py`.
The child has TypeScript-style test names, a dev branch for the code, the kit on its own branch (rule 24), a screens list and a workflow
copied from the `Wiring CI` example. The kit sits in `knowledge/shipquick_latest`, as in a real child. The walk runs `adopt.sh`,
`adopt.sh --check`, a bump branch, `adopt.sh --gate-files`, commits through the real hooks, and pushes the gate-files PR and the code PR for
real. The pre-push stage picks its own base. The code PR must print `ok` for every walked `check_local.sh` check. It runs in under a minute.

A new check joins the walk in the same PR: name it in `WALKED` or `NAMED` in that test, with a reason. A new `checks.yml` job goes in `CHECKS_YML`.
The walk does not run the GitHub jobs of `checks.yml` (follow-up row, 13 Nov 2026).

To run the walk against an old kit, set `WALK_KIT_SHA=<sha>`. It shows the step where that kit failed.

## A child skips its slow jobs with its own map (story #498, ADR-019)

A child with a slow job (a device build, an end-to-end run) can skip it when the change cannot reach it. The child writes a map, the kit's
reader decides, and a last job proves it. `adopt.sh` writes none of this: the child's build jobs and its map are the child's own.

1. Write `.shipquick/change_map.json`: each area names its jobs and the paths that turn it on, and `free` lists the paths that need no slow job.
   A path no row names turns every area on, so a new folder is never skipped by mistake.
2. Copy the workflow below into the child's build workflow. Add one `if:` to each slow job, and name every slow job in the `gate` job's `needs`.
3. Run `adopt.sh <child> --check`. It tells you when the caller has no concurrency block (one run per PR).

Every area turns on when: the map, the workflow's `changes` job or its header changed in the PR, the pin `knowledge/shipquick_latest` moved
(a kit bump), the event is not a pull request or a push, or anything cannot be read. The map is read from the base branch, so a PR cannot
weaken the rule it is judged by. The reader runs from the kit at the pinned commit, so a bump is always a full run. The `gate` job fails when a job of
an area that is on did not succeed, and when a needed job is missing.

```yaml
name: Build
on:
  pull_request:
  push:
    branches: [main]
concurrency:
  group: build-${{ github.event.pull_request.number || github.run_id }}
  cancel-in-progress: true
permissions:
  contents: read
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      app: ${{ steps.map.outputs.app }}
      decision: ${{ steps.map.outputs.decision }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          fetch-depth: 0
          submodules: true
      - id: map
        env:
          EVENT: ${{ github.event_name }}
          BASE: ${{ github.base_ref }}
          BEFORE: ${{ github.event.before }}
        run: |
          if [ "$EVENT" = "push" ]; then
            base="$BEFORE"
          else
            base="origin/${BASE:-main}"
            git fetch -q origin "${BASE:-main}" 2>/dev/null || true
          fi
          mkdir -p "$RUNNER_TEMP/map"
          if git show "$base:.shipquick/change_map.json" > "$RUNNER_TEMP/map/change_map.json" 2>/dev/null \
              && python3 knowledge/shipquick_latest/scripts/change_map.py decide --base "$base" --head HEAD --event "$EVENT" \
                --map "$RUNNER_TEMP/map/change_map.json" --outputs "$GITHUB_OUTPUT" \
                --ci .github/workflows/build.yml --guard .shipquick/change_map.json --guard knowledge/shipquick_latest --decision-job changes; then
            exit 0
          fi
          printf 'decision={"all":true}\n' >> "$GITHUB_OUTPUT"
  app-tests:
    needs: [changes]
    if: needs.changes.outputs.app != 'false'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - run: echo "the child's slow job goes here"
  gate:
    needs: [changes, app-tests]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          submodules: true
      - env:
          DECISION: ${{ needs.changes.outputs.decision }}
          NEEDS: ${{ toJSON(needs) }}
        run: |
          printf '%s' "$DECISION" > "$RUNNER_TEMP/decision.json"
          printf '%s' "$NEEDS" > "$RUNNER_TEMP/needs.json"
          python3 knowledge/shipquick_latest/scripts/change_map.py gate --decision "$RUNNER_TEMP/decision.json" --needs "$RUNNER_TEMP/needs.json" --map .shipquick/change_map.json
```

A map for it:

```json
{"areas": {"app": {"jobs": ["app-tests"], "paths": ["app/**"]}}, "free": ["docs/**", "*.md", ".github/**"]}
```

`tests/test_child_map_doc.py` runs the commands of this snippet, and the sample child walk runs it in a generated child.

## Checklist for each child

Do these in order, in the child repo. One step at a time.
0. Run `bash knowledge/shipquick_latest/scripts/adopt.sh . --check` first (story #446) and keep its output for the PR.
1. Bump the submodule to the release tag: `git -C knowledge/shipquick_latest fetch --tags && git -C knowledge/shipquick_latest checkout <release tag>`, then `git add knowledge/shipquick_latest`.
2. Run `bash knowledge/shipquick_latest/scripts/adopt.sh . --ref <release tag>`. A rule-24 child adds `--kit-branch <branch>` and runs it on that branch.
3. Commit and push the files through a PR. A rule-24 child also copies `shipquick-call.yml` to `main` in a PR.
4. Run the command `adopt.sh` printed, to make `shipquick-checks / gate` a required check.
5. If the caller names a kit branch, protect that branch and require pull request reviews there.
6. A private child: add a fine-grained token that can read it to ShipQuick's `SHIPQUICK_CHILD_TOKEN`, or the daily scan names it as skipped.
7. Wait for one PR whose `shipquick-checks / gate` is green. Then run `adopt.sh . --check`. It must print `adopted`.

## Run `adopt.sh . --check` before you push a bump (story #446)

A bump PR once went red in CI on two things a local run could have caught: commit subjects over 72 characters, and empty Dev and Production links past milestone D1. The git hooks were configured but never installed in that repo, so the commit-msg guard never ran. `adopt.sh . --check` now checks what the child's CI will check, so run it **before every push of a bump branch**, and paste its output in the PR:
- **Hooks.** The ShipQuick hooks are in `.pre-commit-config.yaml` and the git hooks folder is empty: it fails and prints `pre-commit install`. A normal `adopt.sh` run installs them itself (it writes only the hooks folder). Without `pre-commit` on the machine it prints the install line and `--check` keeps failing. The `pre-commit` feature off means nothing to install.
- **Commit subjects.** Every non-merge commit since the base branch (`origin/<kit branch>`, else `origin/dev`, `origin/main`, `origin/master`) must have a subject of 72 characters or fewer. The line names the commit and its length. With no base branch the check is skipped.
- **Environments.** `check_environments.sh` runs on the child's `CLAUDE.md` with the milestone in its caller, so empty or placeholder links fail here with the same words as CI.

Every session in a project with configured but uninstalled hooks also sees one warning line at start (the plugin's session-start hook), so the gap shows up before the first commit.

## Adding a child

Add its `owner/repo` to `docs/children.md` once (a one-line PR to ShipQuick, or let the owner do it). Add `private` only when `gh repo view` says it is private. Write one `# <name>: <what GitHub shows>. Next: <step>` note above its line. Then follow the checklist above.

## UI platforms (story #187, S9)

`adopt.sh <child> --platforms android,ios[,web]` wires a child to the kit's UI libraries (ADR-012). Nothing is installed on the machine that runs it.
- `ui/platforms/android-settings.snippet.kts` and `ui/platforms/ios-package.snippet.swift`: the one line to paste (`includeBuild` and SPM `.package(path:)`), both pointing into `knowledge/shipquick_latest/ui/`.
- `ui/platforms/lint/`: the lint configs and the Konsist test, copied for the child's CI.
- `ui/platforms/PROTECTED.txt`: the lint paths the child should protect from loosening.
- `ui/platforms/KIT_PIN`: the kit commit the lint and the snippets were written for.
- `ui init` is not run by `adopt.sh`. It needs npm and the Astryx CLI, so it runs in CI: `bash knowledge/shipquick_latest/scripts/ui.sh init`. The script prints this line.
- `--check --platforms ...` prints `platforms: OK <list>`, or `platforms: not ready` with what is missing or stale.

## The offline vendor backup

A child never fetches the vendor backup. It is a private repo, read only by the kit's own CI with a token. It fetches the ShipQuick submodule commit and nothing else. ShipQuick keeps
a copy of its pinned npm and Compose packages in another repo, `satvik-jain-iitd/shipquick-vendor-backup`, in case a source
goes closed. A clone or a submodule update never fetches it, so nobody downloads its 286 MB.
Read `docs/VENDOR_BACKUP.md`.
