# Review Shape: how a review finding looks

Every review of a change uses this shape. It applies to the reviewer session, a review
subagent, and any review a child project runs. The rule is in `CLAUDE.md` (rule 30).

Source: the `ponytail-review` skill and the ECC `code-reviewer` agent, read in the 10 Nov 2026 study
(`docs/research/2026-11-10-ponytail-ecc-study.md`). The shape is ours; no code was copied.

## The rules

1. **Report only when over 80% sure.** A guess is not a finding. Say the doubt in `Not checked:` instead.
2. **Each finding has a concrete case.** Name the input or state and the wrong result. No case, no finding.
3. **Read the callers, not only the diff.** A changed function can break code the diff does not show.
   Grep every caller before you call a finding real.
4. **A `shortcut:` comment is a decision, not a finding.** A comment like
   `shortcut: global lock, per-key locks when throughput matters` names its limit. Report it only when
   the expected load already crosses that limit.
5. **Zero findings is a valid result.** Do not invent findings to look busy. End with `Verdict: Ship.` and `Not checked:` as below.
6. **Protected PRs get a second, fresh review.** A PR on a protected path (see `scripts/protected_paths.txt`)
   gets a second review by a fresh agent that reads the code, not the first review's notes.

## The four parts of a finding

Every finding has all four parts. Each part is one or two short sentences.

- **What this is:** what the code does, in plain words.
- **Problem:** the wrong result, with the concrete case.
- **Fix:** the smallest change that works. Prefer a fix that deletes code.
- **If we skip:** what breaks, and for whom.

Example:

```
2. **Orders land on the wrong day** (`billing/close_day.py:L40-52`)
   - **What this is:** At midnight this job closes the day and bills all orders of that day.
   - **Problem:** It takes "today" from the server clock, which runs in UTC. An order placed
     at 00:30 in Berlin is billed on the day before.
   - **Fix:** Compute the day once in the shop's time zone.
   - **If we skip:** Late orders show the wrong date, and accounting fixes them by hand.
```

## Groups

Group findings by weight. Skip an empty group. Number them across all groups, so the owner can say "fix 2 and 5".

- **Must fix:** bug, security, data loss, breaks at the expected load.
- **Should fix:** risky code with no test, real slowness, duplicate code, code that should not exist.
- **Nice to have:** small speed-ups, shorter forms.

## The end of every review

The review always ends with these lines, in this order:

- `Verdict: Ship.` or `Verdict: Fix first.` with the numbers, for example `Verdict: fix 1 and 3 first.`
- `Not checked:` one line on what mattered and was not checked. Write `Not checked: nothing.` when all was checked.

## Out of scope

- Style taste, "consider using X", vague worries, and missing docstrings on simple helpers.
- Changing code. A review lists findings. The coder fixes them.
