# Assumptions

Every assumption the kit makes, with the story that made it. Never delete a row; mark it `wrong` and add the fix.

| Date | Story | Assumption | Why it is open | Status |
|---|---|---|---|---|
| 2026-11-10 | #327 | An upgrade trigger is a verb (add, upgrade, switch, move, replace, use, swap) with `when` or `if` later in the same sentence, or `upgrade to` / `upgrade when`, or a `when` clause with a condition word (matters, passes, exceeds, grows, reaches, becomes, needs, hits, goes over, is over, is above). Anything else is `no-trigger`. | A human reads the comment and may disagree on a phrase like "wrap with X where an app needs it", which the rule tags `no-trigger`. Owner can widen the list in `scripts/check_shortcuts.py` with a fixture. | open |
| 2026-11-10 | #327 | `--write` logs every shortcut (not only `no-trigger` ones), so `docs/follow-ups.md` is the ledger. Each row carries a `[sc:<key>]` key (sha1 of file and normalised text, 12 hex) so a second run adds nothing, and a line move does not make a duplicate. | The spec says "one row per new shortcut"; if the owner wants only the untriggered ones, change the filter in `write_rows`. | open |
| 2026-11-10 | #327 | The ledger scans tracked files with a source suffix only (no markdown), skipping `tests/`, `fixtures/`, vendored or built folders. A file that is not UTF-8 is skipped. | Shortcut comments in docs are not debt; a vendored copy is not ours to fix. | open |
| 2026-11-10 | #327 | The CI job `shortcut-ledger` is warn-only and is not in the `gate` needs list, so it never blocks a PR. `check_local.sh` prints the count after its checks. | The owner may later want a threshold; that is a new story. | open |
