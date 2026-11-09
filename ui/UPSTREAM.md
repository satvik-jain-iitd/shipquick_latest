# Upstream: what we copied, and from where

Source: https://github.com/meta/astryx (MIT, Meta Platforms).
Commit: `86a32152f4ede57783bc72574bc3ec363755d53d` (branch `main`, read 9 Nov 2026).
Licence: `ui/LICENSE.meta-astryx.txt`. Every copied file keeps its Meta copyright line.
We never call our product "Astryx". Rule 38, ADR-012.

## Files

| Ours | Upstream path | Change |
|---|---|---|
| `schema/doctypes/component/type.ts` | `packages/cli/authoring/doctypes/component/type.ts` | One field added: `platforms: {android, ios, web}` |
| `schema/doctypes/base/type.ts` | `packages/cli/authoring/doctypes/base/type.ts` | None |
| `schema/contract/types.ts` | `packages/native/src/contract/types.ts` | `sameMeaning` takes the map shape of upstream's `NativeAdditions.sameMeaning` (`fromComponentDoc.ts`), because we write contracts by hand |
| `schema/platforms.ts` | `packages/native/src/platforms.ts` | None |
| `guides/dense-writing.md` | `.claude/skills/dense-compression-protocol.md` | A header comment only |
| `LICENSE.meta-astryx.txt` | `LICENSE` | None |

Ours, not copied: `schema/component.schema.json` and `schema/contract.schema.json` (JSON twins of the two
type files, so Python checks run without Node), `scripts/check_ui_docs.py` (the idea of upstream's
`docPropReferences.test.ts` and `docPropLiterals.test.ts`, checked against our contracts), and `components/Button/`.

## How to pull an upstream change

1. Pick the new commit. Read its changes to the files above.
2. Copy each file again. Put back the change named in the table.
3. Update the commit line here. Run `python3 scripts/check_ui_docs.py` and the tests.
4. One PR. Name the old and new commit in it.

Story S3 (#183) adds the copied CLI (`ui/cli/`) to this file.
