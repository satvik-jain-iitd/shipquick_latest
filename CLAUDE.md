# shipquick_latest: Project Rules

Read first: `docs/PLAN.md` (the plan and case study) and `docs/process-trace.md`.

Standing rules, every session:
1. First action: read `docs/process-trace.md`. Last action before "done": append this session's steps to it (one row each: date, step, actor, what, artifact, owner contact asked / volunteered / reviewed).
2. Every owner message that changes direction gets bullets in `docs/discussions/<START_DATE>.md`.
3. Every idea the owner states is logged at once with `~/Desktop/SecondBrain/tools/idea.py` and one line in `docs/ideas.md`.
4. Work only from GitHub issues. Branch `feat/<issue>-<slug>` from `dev`. PR feat -> dev (self-review checklist, CI green). PR dev -> main at each demo increment; the owner merges main.
5. TDD: failing test first, named after the Gherkin scenario, failure pasted in the PR. Tests listed in `docs/tests/test-cases.md`.
6. Ponytail: only the code the story needs. No GUI, tray, VAD, streaming, LLM cleanup (ADR-010).
7. Definition of Ready before a story starts; Definition of Done before it closes (docs/PLAN.md Part D).
8. Decisions that change architecture or scope get `docs/decisions/ADR-NNN.md` in the same PR.
9. Apple-silicon native only. Never Rosetta. Python >= 3.12 < 3.14 (ADR-008).
10. Models live in `models/` (gitignored, shipped in the zip). Never download at run time (ADR-007).
11. Branches: `main` is protected, never push direct. `dev` is integration. Feature branches `feat/<issue>-<slug>` come from `dev`, merge back via PR.
12. PRs stay small: max 50 files. Commits follow `COMMIT_GUIDELINES.md`. Merge only when all gates pass: green CI, one approval (not the author), zero unresolved comments, branch up to date, not a Draft, issue linked with `Closes #N`. `Closes #N` only auto-closes on a merge into `main`. After a merge into `dev`, run `python3 scripts/close_linked_issues.py <pr>` (dry run, then `--yes` after one owner yes); it closes only linked story issues, never epics, never for an open or unmerged PR. Full rules in `docs/PR_RULES.md`. Coverage tracked in `docs/PR_COVERAGE.md`.
13. Pre-commit runs on every commit: no secrets, no files over 500KB, no merge markers, markdown blocks closed.
14. Branch prefixes: `feat/` features, `fix/` bugs, `docs/` docs, `design/` design system, `test/` tests, `chore/` maintenance, `ci/` pipelines. Design changes get `docs/decisions/ADR-NNN.md` in the same PR.
15. One bug = one issue. Never club unrelated bugs. Every bug gets severity + user story + owner + milestone before any fix work.
16. Triage before fixing: read, assign severity, link user story, assign owner, add `triaged`, move on board. Update `docs/bugs/ACTIVE_BUGS.md` on every status change.
17. Every issue and PR gets a milestone (D0-D6) and an assignee. Demo artifacts stay labeled and closed; they are placeholders, not real work.
18. PM and agile process lives in `pm/agile/`. A sprint is one week and one GitHub milestone (`S<nn>`). A PI is a D increment (an epic). Rank work by value only, never hours or story points. Size is T-shirt only (`XS, S, M, L, XL`). Write the sprint plan, review, and retro in `pm/agile/sprints/S<nn>/`. Versions use SemVer `vX.Y.Z`.