# ui/: the spec layer

This folder says what each component is. It works for any platform and any child.
Rule 38 and `docs/COMPONENT_LIBRARY.md` say why. `UPSTREAM.md` says what is copied from Meta.

## One component, two files

Each component has a folder: `components/<Name>/`.

1. `<Name>.doc.mjs` is the doc. Its shape is `schema/doctypes/component/type.ts`.
   It says what the component is for, the do and don't list, accessibility, anatomy and props.
   `platforms` names the library part on Android, iOS and web. `null` means "not on this platform".
   Write the body as plain JSON after `export default`. Then Node and Python can both read it.
2. `<Name>.contract.json` is the contract. Its shape is `schema/contract/types.ts`.
   - `core`: props every platform has.
   - `platforms`: props one platform adds. They never remove or rename a core prop.
   - `webOnly`: web props left out of the core. Each one gives a `reason`.
   - `sameMeaning`: a core prop whose name a toolkit also uses, with the same meaning,
     and why. Example: `"onClick": "a press, as in Compose"`.

A dense twin (same facts, fewer tokens) can sit in the doc as `export const docsDense`.
How to write it: `guides/dense-writing.md`.

## The guard

Run `python3 scripts/check_ui_docs.py` (or `--root <folder>` in a library repo). It fails when:
- a component folder has no doc or no contract;
- a doc or contract breaks its JSON schema (`schema/*.schema.json`);
- a doc names a prop the contract does not have, or a contract prop has no doc;
- an enum prop's doc type does not list the exact values, like `'sm' | 'md' | 'lg'`;
- any prop, web-only too, is typed by a bare name (like `ButtonType`) or mixes values with `string`;
- a prop is named twice, or the doc has other text after its JSON (only `export const <name> = {...}` may follow);
- the folder has no components at all.

It runs in `scripts/check_local.sh` and in CI (job `ui-docs`).
The feel tokens (motion, haptics, touch target) live in `design/tokens.json`.
