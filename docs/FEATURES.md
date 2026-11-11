# Features: what each ShipQuick feature does and how to change it

A project turns ShipQuick features on or off in one file, `.shipquick/features.json`. The kit keeps the list,
the defaults and the plain words in `scripts/features_default.json` (ADR-016). A project with no file runs every
feature at its default. `scripts/features.sh get` shows what is on.

## How to change one

Only the owner changes a feature. He types the line himself, for example:

    ! bash scripts/features.sh set roadmap off

That rewrites `.shipquick/features.json`. The file is a protected path, so the change reaches the project only through
a pull request the owner merges. An agent that edits the file on its own branch changes nothing: the check that judges
the pull request reads the file from the base branch, never from the branch under review.

Turning a feature off always means the owner does more by hand. It never means a check is skipped without his say.
`adoption` and `gate` are locked: `features.sh set` refuses them and the reader always says they are on, because they
guard every other feature.

Today the file and the reader exist, and `adopt.sh` writes the file and honours `pre-commit` and `roadmap`. The CI jobs
and scripts learn to read their own flags in the next stories of epic #86 (F4 to F8); until then a flag for them is
recorded but not yet obeyed.

## Roadmap and issues

| id | Name | What it does | If you turn it off | Default |
|---|---|---|---|---|
| `roadmap` | Live roadmap | Builds a page from your issues and pull requests that shows what is done, what is now and what is next. | No roadmap page is built or updated. Nothing else changes. | on |
| `hosted-roadmap` | Hosted roadmap page | Reserved for a roadmap page on the web that anyone with the link can open. Nothing uses it yet. | Nothing changes, because no hosted page exists yet. | off |
| `close-on-merge` | Close issues on merge | Closes the story issue a pull request names with Closes #N once it is merged, and asks every pull request to name one. | Issues stay open after a merge and a pull request need not name one. You close them by hand. | on |

## Merging and modes

| id | Name | What it does | If you turn it off | Default |
|---|---|---|---|---|
| `lanes` | Work lanes | Tells agents to keep up to three separate lines of work open at once, one per set of files. | Agents keep one line of work open at a time. Work is slower, never less safe. | on |
| `modes` | Manual, semi and auto modes | Lets you choose how much agents may do: ask you for every merge, some, or none. | The mode always reads manual: agents never merge on their own. | on |
| `merge-gate` | Agent merge gate | Lets a reviewer agent merge a pull request after every check is green and it is approved. | No agent merges anything. You merge every pull request by hand. | on |
| `uat-on-main` | Test on dev before main | Asks for a checklist of real tests on the dev link before a change goes live. | A change can go live without the checklist. | on |
| `freeze` | Release freeze | Lets you stop all merges to the live branch with one file, until you lift it. | You cannot freeze the live branch. Merges to it are never blocked for a freeze. | on |

## Checks on every pull request

| id | Name | What it does | If you turn it off | Default |
|---|---|---|---|---|
| `environments` | Dev and live links | Checks that the project writes down both its dev link and its live link, and keeps them apart. | The project may run without a dev link written down. | on |
| `team-block` | Handoff block | Asks every pull request to end with a short note for the reviewer saying what is needed. | Pull requests need no reviewer note. | on |
| `roles` | Who builds, who reviews | Checks that the account that writes a change is not the one that approves it. | The same account may write and approve a change. | on |
| `story` | Story needs a who and a done | Checks that each story a pull request closes says who does it and when it is done. | A pull request may close a story that says neither. | on |
| `disable-comments` | No quiet switch-offs | Fails a pull request that adds a comment turning a check off, unless it names the decision that allows it. | A check may be turned off with a comment and nobody is asked. | on |
| `frontend-design` | Design first for screens | Asks that every change to a screen names the approved design it follows, and shows the real screen next to it. | Screen changes need no approved design. | on |
| `design-tokens` | No loose colours or fonts | Fails a web style line that adds a colour or font value directly, instead of using the shared design values. | Colours and fonts may be written straight into style files. | on |
| `component-registry` | Ready-made screen parts only | Checks that screens are built from the shared library of screen parts, not drawn by hand. | Screens may be hand-drawn instead of using the library. | on |
| `rule-copies` | One copy of each rule | Fails when two copies of the rules text drift apart. | Copies of the rules may differ and nobody is told. | on |

## Local checks

| id | Name | What it does | If you turn it off | Default |
|---|---|---|---|---|
| `pre-commit` | Checks before each commit | Runs quick checks on your computer before each commit, so mistakes are caught early. | No checks run before a commit. CI still catches them later. | on |

## Always on

| id | Name | What it does | If you turn it off | Default |
|---|---|---|---|---|
| `adoption` | Kit is really installed | Checks that the project carries the ShipQuick checks for real, at the version it says. This guards all the others. | Cannot be turned off. | always on (locked) |
| `gate` | The final gate | Collects every check into one pass or fail that a merge waits for. This guards all the others. | Cannot be turned off. | always on (locked) |
