# Assumptions

Every assumption the project runs on, with the story that made it. Rows are added at the end; a wrong one is marked, never deleted (rule 26).

| Date | Story | Assumption | Why | Check that would prove it wrong |
|---|---|---|---|---|
| 10 Nov 2026 | #319 (A15) | A code file is any changed file that is not `.md` or `.txt` and not under `docs/` or `pm/`. A `.yml` workflow or a `.sh` script counts as code. | A TDD rule needs a line between "code" and "docs". CI workflows change behaviour, so they count as code. | A code change that lands under `docs/` or `pm/` with no test, or a doc-only PR that fails because of a `.yml` file. |
| 10 Nov 2026 | #319 (A15) | A PR into `main` (promotion) and a PR from `main` (back-merge) are exempt from the TDD check. | Rule 24: `main` holds run-critical code only and the changes there were already reviewed on `dev`. | A feature PR that targets `main` directly (it would be exempt by mistake). |
| 10 Nov 2026 | #319 (A15) | A test is named by its path (`tests/test_x.py`), with an optional `::test_name`. The path must equal a file in the PR diff. A file that only gets deleted is not evidence. | The check reads the body as text and the diff from git; it does not parse test function names. | A test named by a bare file name (`test_x.py`) that the check rejects, or a deleted file that passes. |
| 10 Nov 2026 | #319 (A15) | Before a push, `check_local.sh tdd` reads the commit log as the PR body, the same way the frontend-design and story checks do. CI reads the real PR body. | No PR body exists before a push. | A commit message that names a test and passes locally but fails in CI (the body differs). |
