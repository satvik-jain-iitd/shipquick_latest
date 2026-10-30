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

`.github/workflows/checks.yml` (the reusable workflow this calls) runs every PR gate a child needs — team block, `Closes #n`, design-first, UAT on main, environments — plus one more job, **adoption**, that runs first and fails loudly when:
- the caller's pin (`shipquick_ref`) does not equal the commit the child's `knowledge/shipquick_latest` submodule is actually at, or
- the child's `.pre-commit-config.yaml` carries no ShipQuick hooks.

Either failure prints the one command to fix it: `bash knowledge/shipquick_latest/scripts/adopt.sh .`.

The same verdict runs locally and before a commit ever reaches GitHub: `bash knowledge/shipquick_latest/scripts/adopt.sh . --check` prints "adopted" or "not adopted: <why>" and exits 1 when not adopted.

## Layer 2: a child with no caller at all

Layer 1 only fires once a child is wired enough to have the caller running. A child that never ran `adopt.sh`, or deleted the caller, has no CI of its own to fail. `docs/children.md` is the registry (one `owner/repo` per line); `scripts/adoption_scan.py`, run daily by `.github/workflows/adoption-scan.yml`, reads it and opens one `feedback` issue **in this repo** for any child whose default branch has no `shipquick-call.yml`, or pins a ShipQuick commit more than 14 days old. It reuses an existing open issue (comments instead of opening a second one) for the same child.

## Adding a child

Add its `owner/repo` to `docs/children.md` once (a one-line PR to ShipQuick, or let the owner do it). Everything else is automatic from there.
