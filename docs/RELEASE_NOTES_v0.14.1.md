# ShipQuick v0.14.1 (13 Nov 2026)

A patch release (`pm/agile/RELEASE_GUIDE.md`). It fixes one check. It comes from feedback #490: a gate-files PR on a kit-branch child was blocked by the tdd check. Nothing else changes.

## What a child gains

- **A gate-files PR passes the tdd check.** A PR whose changed files are only the gate files (`scripts/gate_files.txt`, ADR-017) is exempt, as a kit bump is. The exemption reads the pin and both list files from their files.
- **A clear stop for a broken list.** A missing or empty `scripts/adopt_files.txt` or `scripts/gate_files.txt` makes the check exit 1 with one line that names the file. It never guesses the exempt set.

## What breaks for children on the bump

Nothing. A child that does not use a gate-files PR sees no change in its tdd check.

## What a kit-branch child does after the bump

1. Bump on a branch cut from the kit branch, as before. Merge it into the kit branch.
2. On each code branch, push the gate-files PR. It now passes the tdd check without a `## Red` section, because it holds no code.
3. Keep `## Red` for every PR that changes code.

## Not yet

- `.gitmodules` is exempt from the tdd check by its path. A PR can change its content without a test. The pin is still protected, which stops an auto merge (follow-up row, 13 Nov 2026).
- The full test suite in `tests/test_adopt.py` gave varying failures on one Mac run (see the #492 PR body). CI's full run was green on the merge commit of #492.
