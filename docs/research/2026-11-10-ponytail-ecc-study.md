# Study: Ponytail and ECC, what ShipQuick takes, adapts, or leaves

Date: 10 Nov 2026. Reader: shipquick-qa. Method: both repos cloned read-only and read in full (Ponytail 216 files by one reader; ECC 4,701 files by two readers, then cross-checked). Clones are never executed.

Sources and tiers (rule: `web-research` skill):
- **Ponytail** (`dietrichgebert/ponytail`, v5.3.3, MIT, 29 Oct 2026). Mechanisms exist in code: Tier A. Benchmark numbers: Tier B (the author's own runs; the author sells a waitlist and takes sponsors). Confidence 0.7. Two independent runs (KuldeepB19, RicardoCostaGit) point the same way but note "higher process cost on large completion-forced tasks".
- **ECC** (`affaan-m/ecc`, commit d2ef268, v2.2.3, MIT, 1 Oct 2026; ECC Pro $19 a seat). Mechanisms: Tier A. Claims about results: Tier C. Confidence 0.4. Of 44 process mechanisms, one (GateGuard) was measured, and the result was null.
- **ShipQuick itself**: 38 rules, none measured. `docs/research/experiments.md` did not exist before PR #308. Rule 10 says "no claim without a test". Our own kit had never been tested.

## 1. Adopt (ShipQuick lacks it, we take it)

| # | What | Where it comes from | ShipQuick today | Story |
|---|---|---|---|---|
| A1 | **Bench harness for the kit.** One headless `claude -p` run per task. Arms: `no-kit` and `kit`. 10 to 20 XS tasks from our own child stories. Hidden checks that run the code. `--selftest`: the good and bad reference must pass and fail before any API spend. `--rescore` offline. Median per task, then geometric mean, then bootstrap interval. Superseded results are never deleted. | ponytail `benchmarks/agentic/run.py`, `tasks.py`, `judge.py`, `complete.py`, `results/*.md` | Nothing. One Haiku eval, n=1. | #311, #312 |
| A2 | **Rules reach every subagent.** A SubagentStart hook injects the load-bearing rules in dense form. SessionStart does the same and prints `.shipquick/mode`. | ponytail `hooks/ponytail-subagent.js`, `ponytail-runtime.js`; Ponytail issue #252 (SessionStart context never reaches subagents) | No hook at all. Rules are CLAUDE.md prose. A second reviewer or a Haiku builder sees only what the brief says. | #313 |
| A3 | **Rule-copy canary.** A child CLAUDE.md must carry the kit's rule block byte for byte. 10 load-bearing phrases must be present in CLAUDE.md and the named skills, or CI goes red and names the file. | ponytail `scripts/check-rule-copies.js`; ECC `tests/ci/code-reviewer-false-positive-guard.test.js` (15 phrases pinned) | Rule 19 says "copy into the child". Nothing checks drift. | #316 |
| A4 | **Review finding shape.** Each finding is a concrete case (this input gives this wrong result), in four parts (what, problem, fix, if we skip). Read the callers, not only the diff. A `shortcut:` comment is a decision, not a finding. Report only over 80% confidence. Zero findings is a valid result. End with `Verdict:` and `Not checked:`. | ponytail `skills/ponytail-review/SKILL.md`; ECC `agents/code-reviewer.md` | Rule 30 says "comment on every file" and gives no shape. `review_merge.sh` does not ask for `Verdict:` or `Not checked:`. | #317 (doc), #318 (gate) |
| A5 | **Three blocking PreToolUse hooks.** (a) Block `--no-verify` and `core.hooksPath`. (b) Warn when a file in `scripts/protected_paths.txt` is edited (the same list `review_merge.sh` reads). (c) Warn when a `NOTES`, `TODO`, `SCRATCH`, `WIP` markdown file is made outside `docs/`. | ECC `bash-hook-dispatcher.js`, `config-protection.js`, `doc-file-warning.js` | Rule 37 catches this at merge time only, not at edit time. | #320, #321, #322 |
| A6 | **Release gate script.** Tag only when the release notes file exists, `gate` is green on the exact SHA, and the tag equals the version in the notes. | ECC `scripts/ci/verify-release-gates.js`; ponytail `check-versions.js` (seven manifests must equal the tag) | v0.9.0 and v0.10.0 were tagged by hand with no check. | #324 |
| A7 | **Workflow security lint.** `pull_request_target` with a head checkout is refused. `npm ci` must carry `--ignore-scripts`. | ECC `scripts/ci/validate-workflow-security.js` | SHA pins and dependency review exist. This does not. | #325 |
| A8 | **Desk reads the Ponytail ledger.** `~/.config/ponytail/band/<project>.csv` already records cost, tokens, agent time, reuse and tests per task on this Mac. The Desk adds one column. No new measuring code. This gives the Haiku versus Sonnet cost per story for free. | ponytail `hooks/band/metrics.ts`, `board.ts` | The Desk shows GitHub state only. | #323 |
| A9 | **Codebase map at session start.** 2,000 characters, top-level names per folder, by regex, no model. Feeds the "already in this codebase?" rung. | ponytail `hooks/ponytail-map.js` (MIT, vendored) | Rule 20 radar covers external reuse only. | #314 |
| A10 | `adopt.sh --check` tells a child when the Ponytail plugin is off. | Ponytail install docs | Nothing. | #326 |
| A11 | **Shortcut ledger.** Every `shortcut:` or `ponytail:` comment is listed; one with no upgrade trigger is flagged. | ponytail `ponytail-debt` skill | Nothing. | #327 |
| A12 | **Cost and loop guard.** Five identical tool calls in a row warn. Session cost over a limit warns, then blocks edits. | ECC `context-monitor`, `cost-warn` hooks | Nothing. | #315 |
| A15 | **TDD evidence check.** A code PR must carry `## Red` naming a test that is in the diff. | Our own rule 5, made checkable | Rule 5 is prose. | #319 |

## 2. Adapt (take the idea, change the shape)

| Idea | Source | Our shape | Story |
|---|---|---|---|
| Validators in CI for agents, skills, commands and hooks (frontmatter and dead references) | ECC `scripts/validate-*.js` | One validator for `docs/` cross-links and `scripts/` `--help` consistency. Low priority. | follow-up |
| A transcript analyser that finds corrections and reverts and proposes a rule | ECC `conversation-analyzer` | `tasks/lessons.md` and `docs/LEARNINGS.md` stay manual. One line at session end in `docs/process-trace.md`: the smallest rule edit. No new agent. | none |
| Paired run before any rule change. Ponytail 2026-06-22: the #245 fix went from 0/3 to 6/6 by operational wording alone; plain prose stayed at 0/3. | ponytail `benchmarks/results/` | ADR-014: a change to a kit rule's wording must beat the current kit on the bench before it merges. | #312 |
| Rules split by path (`.claude/rules/*.md` with `paths:`) | Claude Code docs, https://code.claude.com/docs/en/memory (read 10 Nov 2026) | Supported. A path rule loads only when Claude reads or edits a matching file (Read, Write, Edit, or a Bash read of one file), so a subagent that edits through other Bash commands may not get it. Move UI rules 31 and 38 only after the paired run on the bench (#312) shows no regression. Status: pending test. | #328 |

## 3. Pinch of salt (do not copy)

- **ECC's breadth.** 71 agents, 314 skills, 98 commands. This is a catalog, the opposite of our rule 29 (useful checks only). The `eval-harness` skill says "Supported candidate execution backends: none"; the pass@k numbers are typed by hand. `contexts/` is advertised in the README and no hook loads it. continuous-learning v1 is deprecated, v2 observer is off by default, confidence decay has no code, and nobody measured whether "instincts" help. `performance.md` says "Haiku 90% of Sonnet, 3x savings" with no source. `verification-loop` is prose only.
- **GateGuard, ECC's one measured mechanism.** 336 trials. Gate on: 25 of 48. Gate off: 18 of 48. p = 0.21, "not confirmed". Cost up 35 to 45%. Lesson: a gate that asks the model for facts before it may edit is costly and does not raise quality. Our A5 hooks block or warn. They never ask questions.
- **Haiku ceiling** (Ponytail 2026-06-22, Tier B, 0.7). "grep every caller, fix the shared function" scored 0 of 6 on Haiku 4.5 in both arms; Sonnet and Opus scored 6 of 6 with the rule. llama 3B: noise, no stable effect. For our Haiku coder plan: multi-step reasoning rules do not transfer to a small model. So XS must truly be XS, the reviewer traces the callers, and the bench (A1) measures this again on Haiku 5.5. Our one pass today is n=1.
- **Ponytail's numbers.** Minus 53% code and minus 26% cost on Opus, on the author's own tasks. The independent runs say tool calls and cost can rise on large completion-forced tasks. We take the method, not the prompt (the prompt is already installed).
- **More memory layers.** ECC stacks a pre-compact Haiku summary, session temp files, instincts and unified memory, and its own cost tracker wrote zero rows for 52 days with nobody noticing. We have claude-mem and `docs/process-trace.md`. That is enough.
- **PR burst guard, issue guard, CODEOWNERS, stale bot.** Not needed until outside contributors arrive. Noted, not built.

## 4. What ShipQuick has that neither repo has

Two-account roles checked by CI. Team blocks checked by CI. Design-first gate. UAT checklist gate. Freeze as a file. Protected paths. Child adoption pin check. Live roadmap from issues. Radar first. Model-load doctrine. A merge gate like `review_merge.sh`. We are ahead on process and behind on measurement (A1) and runtime enforcement (A2, A5).

## 5. Order

Lane 1: A0 (#310), A1a (#311), A1b (#312). Lane 2: A2 (#313), A9 (#314), A12 (#315). Lane 3: #316 to #328 in issue order. Epic #309. Owner yes: 10 Nov 2026, "haan start kro".

## Decision rule for this doc

Rows are never deleted. A wrong row is marked superseded with a date and a link to the newer row.
