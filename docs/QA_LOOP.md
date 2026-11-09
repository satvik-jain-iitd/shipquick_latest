# The QA loop

Story #162. One loop that checks a whole app, finds bugs before the owner does, and gets better after each run.
It works for any app: web, Android, iOS or a CLI. The skill `qa-loop` points here (section 13).
The references live in `docs/qa-loop/`. The tools live in `scripts/qa/`.

## 1. Why

ShipQuick says how to design a screen and how to build it. It did not say how to check the whole app.
So each session made up its own way, and nothing carried over to the next run.

Worked example (GoServe, 9 Nov 2026). The first screen alone had 4 bugs. The owner found 2 of them himself.
He turned the internet off and opened the app. No written case covered "open while offline".
Each bug the owner finds costs a phone session, a message and a fix round.

Applies when: a project has approved designs (a canvas, boards or screens) and a running app on a dev link.
Sections 2 and 3 also apply to any project that writes plans, ADRs or stories.

Does not apply to: backend-only work with no screens (sections 6, 7 and 10), and a one-line fix with no plan.

## 2. Roles: the elephant, the goldfish and the owner

This comes from Google's Elephant-Goldfish model (EGM). Source: https://github.com/google/elephant-goldfish-model
(tier A, Apache-2.0). Confidence that it helps us: 0.7, until a project test says more.

- **Elephant**: the session that runs the loop. It holds the whole journey, every screen in order, the
  approvals and the old bugs. It writes the cases and the audit.
- **Goldfish**: a fresh subagent with no chat history. It is read-only. It gets only what a cold user would
  get: one screen image, or only the written steps, or only the document.
- **Owner**: decides trade-offs, confirms bugs, and says yes to changes. Judgment is never handed to a model.

The gap between the two is a finding. If the elephant says "it is clear from the last screen" and the
goldfish is lost, the screen leans on memory. A user who arrives cold (from an alert, after a week) is lost too.

The four goldfish tests:
1. **Comprehension**: can a cold reader explain it back? If not, it lacks context.
2. **Critic**: what was missed? Repeat until only nits are left.
3. **Implementation readiness**: can a developer build it first time, from the issue and the board alone?
4. **Mean review**: tear the PR apart against the board.

Write the rubric before the work. Keep three things, not the chat: the description, the rubric, the output.
A goldfish that fails or returns nothing is "not run". It is never "zero findings". Retry it once.
Details and the essay's steps: `docs/qa-loop/egm.md`.

## 3. Where EGM gates the kit

- **Plans and ADRs**: an EGM review runs before approval. The owner can waive it, in writing, in the record.
- **Story at Ready**: a readiness goldfish gets only the issue and its board. Every question it asks is
  answered in the issue before a developer starts.
- **PR**: a mean-review goldfish gets only the diff, the board and the story. Its findings go in the review.

These are rules for now. Machine checks come later (section 14).

## 4. The QA home

Each project keeps one folder for the loop. The default is `docs/qa/`.

| File | Holds |
|---|---|
| `README.md` | The design canvas link, the dev and prod links, roles, labels, who the user is, the product promise |
| `journey.md` | Every screen in user order, what it is for, where the user comes from and goes next |
| `screens/NN-<board>.md` | One file per screen: design review, controls, cases, owner comments |
| `attacks.md` | The project's own new attacks (the shared ones are in `docs/qa-loop/attacks.md`) |
| `escapes.md` | Bugs the cases missed, each with its five-part lesson |
| `runs.jsonl` | One line per case result |
| `design-audit.jsonl` | One line per design finding |
| `progress.md` | Each screen's state: open, in review, locked |
| `flows/<journey>.json` | Every tap: from screen, control, to screen, status |

Templates for each file: `docs/qa-loop/templates.md`.

## 5. Cadence: one screen at a time

Batches make a reviewer rush. So the loop moves one screen at a time.
1. A goldfish reviews one screen, then stops.
2. After each screen, update `progress.md`. Send the owner one screen card: the board name, what is good,
   the top issues, and the exact steps for his hand checks.
3. The owner tests while the loop goes on.
4. When his checks are in, ask: "Is screen <name> locked?" A locked screen is not opened again in this run.
5. Bugs are filed and sent to the developer at once. They do not wait for the lock. The developer is never idle.
6. Reports grow one screen at a time. The header shows "Screen N of M added, K locked".

## 6. Track 1, sanity: the design and the app match

For each screen, render the board and the app in the same state, at the same size. Put them side by side.
Check the full height, all four edges and every word. A mismatch is a bug (section 9).
This is the same check the coder makes before a PR: see "Build from the board" in `docs/DESIGN_PROCESS.md`
section 2 and `docs/SCREENS.md`. Tools: `scripts/qa/render_boards.mjs` for boards.

## 7. Track 2, QA cases

One file per screen, `screens/NN-<board>.md`.
1. Review the board first. Name a gap only when it is real: the exact board, before and after, and a reason
   with its source. No gap: write "No design gaps".
2. List every control: button, link, field, toggle, swipe, back and system back. Say what must happen, and
   what must happen when it fails.
3. Write cases `TC <screen>.<n>`: exact steps, the exact link, the expected result, and the check type
   (`auto`, `probe` or `owner`). Cover happy, sad, edge and error cases.
4. Pick attacks from `docs/qa-loop/attacks.md` and the project's own list. Pick the ones with the best yield
   first. Add new attacks every run.
5. Give one goldfish only the written owner steps. Rewrite every step it cannot follow without guessing.
6. A full run adds journeys: first install to first success, reinstall, second device, a week away,
   account switch, prod and dev side by side, an alert opened cold.

Run order: the automated suite first, then probes, then the owner by hand.
Only failing cases and real-device cases go to the owner. One case per message, with the exact link
("dev" or "prod" named), numbered steps, and what he should see.

## 8. Runners per platform

Each platform names its `auto` runner, its `probe`, and what stays an `owner` check.

| Platform | `auto` | `probe` | `owner` |
|---|---|---|---|
| Web and PWA | Playwright tests in CI | Playwright on each browser engine and viewport; offline; throttled network; an installed app after a new deploy | A real phone browser and the installed app |
| Android | Compose UI tests or Espresso | `adb`: airplane mode, kill the app, deny a permission, rotate, large font | A real device: alerts, camera, payments |
| iOS | XCUITest | Simulator: network link conditioner, large text, dark mode | A real iPhone: alerts, Face ID, payments |
| CLI | Golden-output tests: exact output and exit code | Bad input, no network, a missing file, a read-only folder, a very long argument | The owner's own shell and machine |

A driver for mobile probes that exists already: `willcoliveira/qualiow-exploratory-testing-skills`
(Maestro shim for iOS and Android; radar run, `docs/research/repo-radar.md`). Borrow it before writing one.

## 9. Triage and fix

- Severity: critical, high, medium, low (`docs/qa-loop/templates.md`).
- Side: `design`, `app`, `both` or `env`. An `env` bug still asks: should the app have handled it? If yes,
  it is an app bug.
- One issue per bug, labels `qa` and `bug`, plus `design-canvas` when a board changes. Body: before, expected
  after, why, steps, case id, found by, attack id.
- A design story goes to the canvas owner. It changes only the named board.
- A code story goes to the coder at once, most severe first. Run the readiness goldfish on it first.
- Every fixed bug gets an automated regression test named after its case id and issue. The issue closes only
  when that test passes.

## 10. Track 3, the design audit

This is the roadmap. It never becomes stories. A finding that is really a bug moves to section 9.
1. **Goldfish pass**: a fresh subagent sees one screen image only. It answers as a cold user first
   (`docs/qa-loop/goldfish_cold_user.md`), then as a critic with the standard (`goldfish_design_critic.md`).
2. **Elephant pass**: with `journey.md`, judge the fit. What came before and after? Is it consistent? Is a
   step extra? Is the promise kept? How are the best moment and the last screen?
3. **Lens pass**: the named lenses in `docs/qa-loop/design-lenses.md` (Nielsen, WCAG 2.2, Apple HIG,
   Material 3, Rams, Norman). Each finding names its lens and its source.
4. Each finding: the screen, a box on the image, what we see, good or bad, why, how to improve, impact,
   effort, and a bucket (now, next or later). Praise what works with the same care.
5. Build the report with `scripts/qa/audit_report.py`. Publish it as one page and update the same link.
6. Each new run marks old findings `resolved`, `still open` or `new`.

## 11. The learning loop

At the end of each run:
1. Print the scorecard: `python3 scripts/qa/scorecard.py <qa_home>`. It shows attack yield, coverage debt
   (bugs without a passing automated test), escapes and the stop rule.
2. For each escape (a bug the owner found outside the cases), write a row in `escapes.md` with five parts:
   situation, root cause, fix, applies when, does not apply to. Add the new attack and the new case it made.
3. If the loop itself caused the miss, propose the exact change. Ask the owner one yes or no. On a yes, keep
   the old copy, apply the change, bump `params.version`, and add a changelog line. Undo is one copy back.
4. A change that helps every project goes to ShipQuick as a feedback issue (rule 33).

## 12. The stop rule

The suite is done when N full runs in a row find zero new bugs. Each of those runs must add at least M new
attacks and cover every screen. Defaults: N = 2, M = 3 (`scripts/qa/params.json`).
Then tell the owner the app can freeze. Send the scorecard and the design audit link.

## 13. Install the skill

The skill is a thin pointer in the kit: `skills/qa-loop/SKILL.md`. It names this page, the references and
the tools. Install it once per Mac:

```
bash knowledge/shipquick_latest/scripts/install_skill.sh
```

In ShipQuick itself, run `bash scripts/install_skill.sh`. It links `~/.claude/skills/qa-loop` (and
`shipquick-feedback`) to the kit. It is safe to run twice. If a real `~/.claude/skills/qa-loop` folder is
already there, it is never touched: move it aside, then run the script again.

Then start the QA home: copy the file list in section 4 into `docs/qa/`, and fill `README.md` first.
Project facts (links, users, the promise) go there, never in the kit.

## 14. Later gates (follow-up stories, not built yet)

- A release PR fails when the QA home has no full run in the last 7 days, or the scorecard shows coverage
  debt or a critical bug.
- A story PR fails when its story has no readiness-goldfish note. A plan PR fails with no EGM review record.
- The scorecard self-test runs in CI (story #162 adds the test; the release gate is the follow-up).

## 15. Limits

- Goldfish subagents run within the project's subagent cap. One goldfish per screen.
- No personal data (phone numbers, emails, addresses, places) in issues, screenshots, logs or reports.
- Never say "works" without a test that proved it, on the same link and device the owner uses.
- The reviewer never edits app code. The coder never edits the canvas.
