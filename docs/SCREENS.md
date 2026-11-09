# A design story proves the screen, not just names it

Story #146 (GoServe feedback #146), validated shape from GoServe story #821, PR #823. A design story's
acceptance is "this screen matches this board." Rule 31 and `scripts/check_frontend_design.sh` only ever
checked that the PR **names** a board (`Design board: <name>`, `Approved: <date>`): naming is cheap and
checkable with a regex, producing a picture is not, so a story could pass every text check while the screen
itself drifted. This mechanism makes the picture a precondition, not a courtesy.

## What a project adopts

Four pieces, all opt-in (a project with none of them is unaffected, the same way `docs/frontend-paths.txt`
being absent skips story #121's own check):

1. **`docs/screens.txt`** — one screen per line: `name | path | viewport (WxH) | setup step`. `#` comments
   and blank lines are ignored. Example (from GoServe):
   ```
   welcome | /customer/ | 412x915 | welcome
   menu    | /customer/ | 412x915 | menu
   ```
   A screen the harness cannot reach yet is **named in a comment**, never silently dropped.
2. **`scripts/screens.sh`** — copy ShipQuick's own (it is generic: `knowledge/shipquick_latest/scripts/screens.sh`
   is symlinked, or your own project copies it verbatim, no edits needed). It orchestrates your own
   `npx playwright test` against your own spec:
   - `screens.sh` (no flag): render only. PNGs go to `$SCREENS_OUT` (default `<app-dir>/screens-out`),
     nothing is compared. Used by the CI step that uploads the artefact on every run, pass or fail.
   - `screens.sh --check`: render and compare with the accepted pictures. Non-zero when a screen changed.
   - `screens.sh --update`: replace the accepted pictures. Run **on CI**, never a laptop (see below), and
     the diff of the baseline PNGs it produces is itself the thing the reviewer looks at.
   - Configure once per project with env vars: `SCREENS_APP_DIR` (where to run `npx playwright test` from,
     default the repo root), `SCREENS_SPEC` (the spec file, relative to `SCREENS_APP_DIR`, default
     `tests/e2e/screens.spec.ts`).
3. **One Playwright spec** (a project writes its own; start from `docs/templates/screens.spec.ts`) that
   reads `docs/screens.txt`, walks a `STEPS` map keyed by the setup-step column, and asserts
   `toHaveScreenshot()` for each screen. A screen naming an **unknown** step fails loudly in its own test,
   not silently skipped — the template's first test proves this. The template's own `toHaveScreenshot` call
   already passes `{ maxDiffPixels: 10 }`, so a copied template is right even before touching your config.
4. **In `playwright.config.ts`**, a baseline path that lands on a protected directory name (the existing
   `*baseline*` glob in `scripts/protected_paths.txt` only protects what you name correctly), and the same
   threshold as a project-wide default:
   ```ts
   export default defineConfig({
     // No OS in the baseline file names: they are made on CI only (see below), never a laptop.
     snapshotPathTemplate: "{testDir}/screens-baseline/{arg}{ext}",
     expect: { toHaveScreenshot: { maxDiffPixels: 10, animations: "disabled" } },
     // ...
   });
   ```
   `screens-baseline` matches `*baseline*` already; do not rename it without adding the new name to
   `scripts/protected_paths.txt` in the same PR.

## The four things that make it deterministic

Evidenced by GoServe's own mutation test (below): skipping any one of these turns the gate into noise within
a few runs, because the picture differs for reasons that have nothing to do with the screen changing.

1. **Mock the clock.** `page.clock.install({ time: <fixed date> })` before anything that reads it (a
   greeting, a relative timestamp).
2. **Await fonts.** `await page.evaluate(() => document.fonts.ready)` before the screenshot, and
   **self-host the fonts** (`app/public/fonts` or equivalent) — a font that fails to load from a CDN in CI
   changes every picture at once, silently.
3. **Disable animations.** `expect: { toHaveScreenshot: { animations: "disabled" } }` in
   `playwright.config.ts`.
4. **Baselines are made on CI, never a laptop.** Fonts and anti-aliasing differ per operating system. The
   first CI run is red with no baseline; commit *that run's* artifact images as the baseline, and the next
   run passes. `scripts/screens.sh --update` run on a Mac can silently replace a CI-made baseline with a
   Mac-rendered one — close this by putting the baseline directory on `scripts/protected_paths.txt` (any
   directory whose name contains `baseline` already matches the kit's existing `*baseline*` glob) and never
   running `--update` outside CI.

## The threshold, and the mutation test that sets it

`maxDiffPixels: 10` in `playwright.config.ts`'s `expect.toHaveScreenshot`. Not a ratio: GoServe first tried
`maxDiffPixelRatio: 0.001` (0.1 percent) and a one-letter typo (`10 digit number` → `10 digit numbr`) slipped
through at about 47 of 2.6 million pixels — well under 0.1 percent, far above what a person would call
unchanged. Ten raw pixels allows a stray anti-aliased edge and nothing else.

**Run this mutation test after adopting the pattern, and again after any threshold change**: change one
letter in text the screen renders, run `scripts/screens.sh --check`, and confirm it fails and names the
pixel count. Put it back, confirm `--check` passes. Do not loosen the threshold because of a flake without
re-running this test — a flake is almost always one of the four determinism items above, not the threshold.

## Also set `retries: 0` for the screens spec

Playwright's default CI retry (`retries: process.env.CI ? 1 : 0`) lets a flaky screen pass on its second
try, which defeats the whole point: a screens spec exists to catch exactly the kind of change retries are
meant to paper over. Scope it with `test.describe.configure({ retries: 0 })` at the top of the screens spec,
or a separate Playwright project with its own `retries: 0`, so the rest of the e2e suite keeps its own retry
policy.

## Wiring CI

`scripts/screens.sh` and the spec need your own preview/build step first (project-specific, so this lives
in your own `ci.yml`, never the reusable `checks.yml` — the same reason `check_frontend_design.sh` only ever
reads your config, never ships a renderer). After your existing e2e step:

```yaml
- name: Upload the screen renders and diffs
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: screens
    path: |
      <app-dir>/screens-out
      <app-dir>/test-results
    if-no-files-found: ignore
    retention-days: 14
```

`always()` matters: the renders and diff images are most useful exactly when the job is red.

## The PR body: `Render:`

Once `docs/screens.txt` has at least one real line, `scripts/check_frontend_design.sh` requires a `Render:`
line in the PR body (alongside `Design board:` and `Approved:`, story #121) pointing at the CI run or
artifact — the same refusal shape as a missing board. A project with no `docs/screens.txt`, or one with only
comments, is unaffected.

## The approval: `Render: <board> -- matches`

A `Render:` link proves a picture exists. It does not prove anyone looked at it (story #153). So the
reviewer opens the render beside the board, at the same scale and full height, and writes this line in the
approving review's body:

```
Render: <the PR's Design board name> -- matches
```

`scripts/review_merge.sh` reads the approving review and refuses the merge without that line
(`scripts/check_design_reviewed.py`; "match", "matches" or "matching", any dash, any case). The board name
must be the one in the PR's `Design board:` line. It applies to the same PRs as the `Render:` line: a
`Design board:` line in the body and a configured `docs/screens.txt`.

## Baselines are never from the first build alone

A screenshot test compares the app with its own baseline, not with the board (story #161). If the first
baseline is taken from a wrong build, every later run passes on the wrong screen. So a new or changed
baseline is accepted only in a PR whose approval carries the `-- matches` line above: the render was compared
with the board first. A baseline is never made from the first build alone, and never from a laptop.

## Applies when / does not apply to

**Applies when**: a project has a design board a screen is supposed to match, and a way to run itself
headless with Playwright already installed.

**Does not apply to**: a backend-only or CLI project; a screen whose content changes every run (live data, a
map tile) unless the project can freeze it; a `dev -> main` promotion or `main -> dev` back-merge (skipped
the same way `check_frontend_design.sh` already skips those, story #121).
