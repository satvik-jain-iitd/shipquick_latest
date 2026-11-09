# Upstream: what we copied, and from where

Source: https://github.com/meta/astryx (MIT, Meta Platforms).
Commit: `86a32152f4ede57783bc72574bc3ec363755d53d` (branch `main`, read 9 Nov 2026).
Licence: `ui/LICENSE.meta-astryx.txt`. Every copied file keeps its Meta copyright line.
We never call our product "Astryx". Rule 38, ADR-012.

## Files

| Ours | Upstream path | Change |
|---|---|---|
| `schema/doctypes/component/type.ts` | `packages/cli/authoring/doctypes/component/type.ts` | Two fields added: `platforms: {android, ios, web}`, and `platformUsage: {android?, ios?, web?}` with the type `PlatformUsageDoc` (upstream's `UsageDoc` fields `description`, `bestPractices`, `accessibility`; story #228, ADR-012); and on `SingleComponentDoc.props`, an optional `platform` per prop (story #228); and `platformApi: {android?, ios?, web?}` with the type `PlatformApiDoc` (`family`, `variants` of `ApiVariantDoc {name, note | props, status?, replacement?}`, `supporting` of `ApiSupportingDoc {name, use, status?, replacement?}`: the API list rows the doc covers), and doc-level `status` (`ApiStatus`: `deprecated` or `unavailable-ios`) with `replacement` (story #231, ADR-012) |
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

Story S3 (#183) does not copy the CLI; it pins it. See the next section.

## The CLI (story #183): used as shipped, not copied

`ui/tool/` pins `@astryxdesign/cli` and `@astryxdesign/core` at exactly `0.7.11` from npm (tag `v0.7.11`,
commit `df8a86a3ae9d0b2d6337c5cf3369488a6f5ac838`), with core's peers. Nothing of the CLI is copied into the kit.
The integration manifest fields we use (`docs`, `agentDocs.append`, `issuesUrl`) were read at that tag in
`packages/cli/authoring/integration/type.ts`. Why: ADR-012, "What the CLI serves".

To upgrade: change both pins in `ui/tool/package.json`, run `npm install --ignore-scripts --save-exact` there
to rewrite the lockfile, then run the `ui-cli` CI job and read the release notes.

Why `@astryxdesign/cli` sits under `dependencies` and the rest under `devDependencies`: that is how the owner's
install wrote it, and `ui/tool/` is a private tool package that is never published or shipped, so the split
changes nothing. Moving it would need a fresh install that only the owner can run here.

## The Swift theme emitter (story #184): read, not copied

Astryx has `packages/native/scripts/swift-ios-theme.mjs` (tag `v0.7.11`, commit `df8a86a3ae9d0b2d6337c5cf3369488a6f5ac838`).
It turns resolved CSS custom properties into `Tokens.swift`. Our input is a W3C `design/tokens.json`, so no file was copied
and nothing in the kit carries the Meta header for it. Ideas we used: a header that names the regenerate command, committed
output, a test that fails when a file drifts, and a reserved-word check on names. Our own emitter is `scripts/emit_tokens.py`.
