# <project>: Project Facts

Protocol: follow knowledge/shipquick_latest/CLAUDE.md

This file holds facts about this project only. It never repeats a ShipQuick rule. If a rule is missing or wrong, fix it in ShipQuick, not here.

## Environments
See `knowledge/shipquick_latest/docs/ENVIRONMENTS.md`. Both lines are required once the project is past milestone D0; `scripts/check_environments.sh` fails CI otherwise.
- Dev link: <url, or "not deployed yet (D0)">
- Production link: <url, or "not deployed yet (D0)">

## Stack
- Language and version: <for example Python >= 3.12 < 3.14>
- Platform limits: <for example Apple silicon only, never Rosetta; ADR-NNN>
- Run-time limits: <for example no GUI, no downloads at run time; ADR-NNN>

## Folders
- <folder>: <what lives there>
- <models/>: <for example gitignored, shipped in the zip; ADR-NNN>

## Decisions
- Architecture and scope decisions live in `docs/decisions/ADR-NNN.md`. List the ones a new session must know: <ADR-NNN: one line each>
