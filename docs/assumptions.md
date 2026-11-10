# Assumptions

Every assumption the code or the rules rest on, one row each. Never delete a row; mark it wrong and add the fix.

| Date | Assumption | Where it is used | Status |
|---|---|---|---|
| 2026-11-10 | A workflow's `on:` block is read by indent: a trigger key sits two or more spaces under `on:`, or the value is inline (`on: [workflow_run]`). A flow-style `on:` map with nested braces is not parsed. | `scripts/check_workflow_security.py` `is_risky` | open |
| 2026-11-10 | A checkout step is one list item (the dash column bounds it). A `ref:` or `repository:` line inside that item, with a PR-head expression, is the PR head checkout. | `step_span`, `head_checkouts` | open |
| 2026-11-10 | A shell command is one logical line: a trailing backslash joins the next line, and `--ignore-scripts` must sit on that same command. An `npm ci` split by any other construct is not seen. | `run_commands`, `check_file` | open |
| 2026-11-10 | `npm i` counts as an install (it is an alias of `npm install`). `npm` flags placed before the subcommand (`npm --prefix x ci`) are not seen. | `NPM_INSTALL` | open |
| 2026-11-10 | `run:` values that only name npm in a `name:` or a comment are not commands, so they are not checked. | `RUN_KEY` | open |
| 2026-11-10 | `vendor-backup.yml` has no real `npm ci` run line: its `npm ci --offline` text sits in a `name:` line and the install runs inside `restore_vendor.sh`. So the repo's own workflows pass without an exception. | `.github/workflows/vendor-backup.yml` | open |
