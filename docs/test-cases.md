# Test Cases Convention

Each story becomes one GitHub issue labelled `story`, linked to its epic issue labelled `epic`.

Each scenario below is copied into the issue and into the matching test name.

## S0. Foundations and process

**S0.1 Repo and branches.**
```gherkin
Scenario: repository exists with protected main and a dev branch
  Given a private GitHub repo "<PROJECT_NAME>"
  When I list branches
  Then "main" and "dev" exist
  And main only accepts changes through pull requests
```

**S0.2 Docs tree from this plan.**
```gherkin
Scenario: every section of the plan has one home in docs/
  Given docs/PLAN.md
  When I open docs/README.md
  Then every Part A, B, C and D section links to exactly one file
```

**S0.3 CI.**
```gherkin
Scenario: CI runs tests
  When I push a commit to dev
  Then GitHub Actions runs pytest and reports a status on the commit
```

**S0.4 Issues.**
```gherkin
Scenario: every epic and story exists as an issue with labels, on a board
  (Backlog / Doing / Review / Done).
```

**S0.5 Linked issues close after a merge into dev.**
```gherkin
Scenario: linked story issues close by hand when a PR merges into a non-default branch
  Given a PR with "Closes #N" lines in its body
  When the PR state is MERGED and the base is not the default branch
  Then a dry run lists each open story issue it would close and each one it skips
  And closes nothing
  When the owner says yes
  Then each open story issue is closed with the comment "Done in PR #X (merged to <base>)."
  And epics are never closed
  And nothing is closed when the PR is open, or closed without a merge
  And nothing is closed when the base is the default branch, GitHub does that
```
Tests: `tests/test_close_linked_issues.py`.

**S0.6 Teammate block checked by code.**
```gherkin
Scenario: a teammate block is checked by code before it is relayed
  Given a block "To <role>, from <role>, re <ref>:" with numbered lines and a last line "Need from you: ..."
  When I run scripts/check_block.py on it
  Then it prints "Block OK" and exits 0
  When the block is empty, has a bad header, no numbered line, a bad last line, over 120 words, or a secret
  Then it prints one reason and exits 1
  And CI runs the same check on the "## For the reviewer" section of every PR body
```
Tests: `tests/test_check_block.py`.

**S0.7 Blocks to the owner say when to act.**
```gherkin
Scenario: a block to the owner is an ordered to-do with a merge line
  Given a block "To owner, from <role>, re <ref>:"
  When every numbered line starts with "Now:", "After <event>:" or "Not yet:"
  And exactly one line reads "Merge: now | not yet | nothing to merge"
  Then scripts/check_block.py prints "Block OK" and exits 0
  When a numbered line has no time word, or the Merge: line is missing or doubled
  Then it prints one reason and exits 1
  And a block to any other role is not affected
```
Tests: `tests/test_check_block.py`.

**S0.8 CI is least-privilege and pinned.**
```gherkin
Scenario: a workflow cannot write to the repo and cannot run moved code
  Given every file in .github/workflows
  Then each has the top-level setting "permissions: contents: read"
  And every "uses:" is pinned to a 40-character commit SHA with its release tag in a comment
  And .github/dependabot.yml updates the "github-actions" ecosystem every week
  And CI runs on a PR into any base branch, so the upper layers of a stack are checked too
```
Tests: `tests/test_ci_must_have.py` (`test_s08_*`).

**S0.9 Secrets and bad dependencies are caught before a merge.**
```gherkin
Scenario: a planted secret and a vulnerable dependency are caught
  Given the CI job "secret-scan" (gitleaks, SHA-256 checked) and the job "dependency-review"
  When a commit adds a key such as API_SECRET_KEY = "<random string>"
  Then secret-scan fails and the gate job fails
  And on a pull request the scan reads only the PR's own commits, on a push it reads the whole history
  And a PR that adds a vulnerable package fails dependency-review when the Dependency graph is on
  And without the graph, dependency-review warns and passes
```
Tests: `tests/test_ci_must_have.py` (`test_s09_*`). The red run is shown in the PR.

**S0.10 Every CI check also runs on the Mac.**
```gherkin
Scenario: scripts/check_local.sh runs the CI hygiene checks before a push
  Given a branch with commits on top of origin/dev
  When I run scripts/check_local.sh
  Then it fails for a merge marker at the start of a line, an unclosed markdown block, a file over 500KB,
       a commit subject that is not conventional, more than 50 changed files, or a secret
  And a marker named inside a string does not fail
  And on commit the secret check reads only the staged files (secrets-staged), on push it reads the whole history
  And .pre-commit-config.yaml runs the fast checks on commit and all of them on push
```
Tests: `tests/test_ci_must_have.py` (`test_s10_*`).

**S0.11 The roadmap page tells the owner where the project stands.**
```gherkin
Scenario: GitHub issues and pull requests become one plain-words page
  Given issues (epics and user stories, with a "## Business" line) and open pull requests
  When the page is rendered
  Then it shows Vision, Delivered (folded shut, newest first), Now, Next and a Board of four columns
  And a story with green checks is in Review, red or draft checks or the label "doing" is Doing, no pull request is To do, closed is Done
  And text from GitHub is escaped and the page has no script
  And a project with more than 100 issues says so on the page
```
Tests: `roadmap/render.test.js` (`S0.11`). Run: `node --test roadmap/*.test.js`.

**S0.12 The roadmap page is plain Markdown from GitHub data.**
```gherkin
Scenario: ROADMAP.md says where the project stands
  Given a project's issues and open pull requests, and its roadmap.json (title, vision)
  When roadmap/roadmap.js writes the page
  Then it has Vision, Delivered (folded shut), Now, Next and Board in that order, with a link to every issue
  And text from GitHub cannot add a link, a tag or a table cell
  And the page has no clock, so an unchanged project writes the same file
  And a GitHub error or a roadmap.json without title or vision stops the run and writes nothing
  And a project with more than 100 issues says so
```
Tests: `roadmap/roadmap.test.js` (`S0.12`).

**S0.13 The roadmap runs on GitHub Actions alone.**
```gherkin
Scenario: a reusable workflow keeps ROADMAP.md on a roadmap branch
  Given .github/workflows/roadmap.yml (workflow_call) and a calling file in the project
  When an issue, a finished CI run, the daily timer or a manual run fires (never a pull request: that would run unreviewed code with write rights)
  Then the job reads only its own repo with the built-in token (contents write, issues, pull requests, checks, statuses read)
  And ROADMAP.md is saved on the branch roadmap, and an unchanged page makes no commit
  And settings come from roadmap.json in the project, and ShipQuick holds no project names
  And no n8n code is left in roadmap/ or in the docs
  And CI runs the node tests
```
Tests: `tests/test_roadmap_workflow.py` (`test_s13_*`), `tests/test_ci_must_have.py` (`test_s13_ci_runs_the_roadmap_node_tests`).

**S0.14 Several stories are built at the same time with few merge conflicts.**
```gherkin
Scenario: parallel lanes, append-only logs and a release branch
  Given rule 23 allows up to 3 stacks open, one per lane, and a lane is a set of stories that touch the same files
  When two branches each add a row at the end of docs/process-trace.md (or LEARNINGS.md)
  Then they merge with no conflict and both rows are kept (.gitattributes merge=union)
  And without that file the same merge conflicts (the control)
  And CHANGELOG.md and ideas.md are not on the list (rows of ideas.md get status edits)
  And the sprint lane template asks for the files each story touches, and for foundation work first
  And a release goes through release/vX.Y.Z with main merged in, so any merge method works, and an optional back-merge of main into dev after the tag
  And the roster allows one reviewer and up to 3 coders, each in a worktree
```
Tests: `tests/test_parallel_lanes.py` (`test_s14_*`).


S0.14 also covers (story #64): a new row in `docs/process-trace.md` writes `-` in the `#` column (rule 1), two branches that each add a `-` row merge with no conflict, and the first union merge trick (`.git/info/attributes`) is in the lane template and in how a child project inherits this. Tests: `tests/test_parallel_lanes.py`.

**S0.15 The owner picks how much the agents do alone.**
```gherkin
Scenario: one word per project says Manual, Semi or Auto
  Given scripts/mode.sh and .claude/commands/mode.md
  When the mode is not set, mode.sh get exits 3 and says to ask the owner
  Then set then get gives the same word, a wrong word is refused, and every git worktree shares the word
  And git does not track it, and rule 0 in CLAUDE.md asks for it at session start
  And only the owner sets it, by typing a `!` line; /mode shows the mode and prints that line, and no agent runs set
  And docs/MODES.md says who reviews, who merges and what still stops in each mode
```
Tests: `tests/test_mode.py` (`test_s15_*`).

**S0.16 Only a coded gate merges, and only in Auto.**
```gherkin
Scenario: scripts/review_merge.sh refuses unless every rule holds
  Given a stub gh and a pull request that passes every rule
  When the mode is semi, manual or not set, or the PR is a draft, closed or has conflicts
  Or the approval is by someone else, of an older commit, or cancelled by a later request for changes
  Or one review thread is unresolved, a check fails or is pending (also one with no conclusion yet), no check ran, or the body has no "Closes #n" (a story PR; release:, chore: and Dependabot are exempt, the same rule as CI)
  Then it exits 1 with "refused: <rule>" and runs no merge
  And when every rule holds it runs gh pr merge --merge once, with the review account's token, and skipped or neutral checks do not block
  And right after the merge it closes the linked story issues with the same token (story #70), and if closing fails it exits 4 and says what to run
```
Tests: `tests/test_review_merge.py` (`test_s16_*`).


**S0.19 A fresh clone matches the README (story #69).**
```gherkin
Scenario: someone clones ShipQuick and follows the README
  Given every path in the README tree and every folder in the structure guide exists
  When they clone the repo and run scripts/check_local.sh sizes markers md-blocks
  Then it passes
  And the Quick Start names pre-commit install, the local checks, roadmap.json and scripts/mode.sh set
  And scripts/check_placeholders.py lists every <PLACEHOLDER> left, and passes when none are left
```
Tests: `tests/test_clone_path.py` (`test_s19_*`).

**S0.17 A story pull request links its issue, so the roadmap can mark it done.**
```gherkin
Scenario: the PR body needs Closes #n
  Given scripts/check_closes.py runs as a step of the team-block job with the PR title, author and body
  When the body has no "Closes #<n>" (or "Closes #N", or only "See #70")
  Then the check fails and says why
  And a title that starts with release: or chore: (also chore(deps):) passes, and so does Dependabot
  And a title that only mentions the word (feat: release the thing) is not exempt
  And Fixes #n and Resolves #n count too, by the same link rule as close_linked_issues.py
```
Tests: `tests/test_check_closes.py` (`test_s17_*`).

**S0.18 A child project adopts ShipQuick with one command.**
```gherkin
Scenario: scripts/adopt.sh copies or updates five things and never harms the child's own files
  Given a child git repository with a ci.yml named "Child CI"
  When adopt.sh runs on it
  Then .gitattributes has the union lines, the roadmap caller is pinned to the ShipQuick commit and names "Child CI", roadmap.json is a stub, mode.md is copied and the pre-commit hooks exist
  And a second run changes nothing and says so
  And the child's own roadmap.json, .gitattributes lines and .pre-commit-config.yaml are kept
  And without a ci.yml the caller has no workflow_run trigger, and a bad --ref or a folder that is not a git root is refused
  And the generated caller matches ShipQuick's own caller except for the pin and the CI name
```
Tests: `tests/test_adopt.py` (`test_s18_*`). Also (story #68): `mode.sh get` with no mode prints one clear line, with no shell error about the missing file.


**S0.20 The default branch comes from the repo being merged, not from the folder (bug #88).**
```gherkin
Given GH_REPO names a repo whose default branch is "master"
And the folder's own git remotes point at a repo with another default branch
When close_linked_issues.py runs for a merged PR
Then it compares the PR base with "master", the default of GH_REPO's repo
```
Tests: `tests/test_close_linked_issues.py` (the fake gh answers `repo view` with a wrong repo).

## Story #87: the merge method
```gherkin
Scenario: the merge gate picks a merge method
  Given a stub gh and a pull request that passes every rule in Auto mode
  When the base branch requires linear history and no flag is given
  Then it runs gh pr merge --squash
  And with --method rebase it runs --rebase whatever the setting
  And with no flag and no such setting it runs --merge as before
  And with --method fast it exits 2 and merges nothing
```
Tests: `tests/test_review_merge.py` (`test_q0_*`).

## Design canvas layout (#105)

```gherkin
Scenario: a canvas is laid out from a manifest
  Given a canvas with boards and a manifest that names sections and rows
  When canvas_stage lays it out
  Then every board is placed once with its state prefix, nothing overlaps, each section has a background artboard listed first that holds everything inside it, no tile is taller than 8000 px, and the same input gives the same layout
  And a board the manifest forgets lands in an Unsorted row, and a box outside its board stops the run
```
Tests: `tests/test_canvas_stage.py` (S1 to S8).

## Story #155: a story names who does it
```gherkin
Scenario: a story without a full Who does it line is refused at Ready
  Given a user-story issue linked from a pull request with Closes #n
  When its body has no "Who does it:" line, or the line is empty, a placeholder, or misses the screen or how often
  Then check_story.py exits 1 and names the line to write
  And a story with "Who does it: <actor>, <app or screen>, <how often>" filled in passes
  And a pull request that links no issue passes
```
Tests: `tests/test_check_story.py` (`test_s155_*`).

## Story #153 and #161: the approval says the render matches the board
```gherkin
Scenario: a frontend PR approved on the code diff alone is not merged
  Given a PR with a Design board line, in a repo with docs/screens.txt configured
  When the approving review has no "Render: <that board> -- matches" line
  Then review_merge.sh refuses and names the line to write
  And with the line, naming the same board, it merges
  And a repo with no docs/screens.txt, or a PR with no Design board, is unaffected
```
Tests: `tests/test_check_design_reviewed.py` (`test_s153_*`, `test_s161_*`), `tests/test_review_merge.py` (`test_s153_*`).

## Publish the canvas from canvas.json (#163)

```gherkin
Scenario: the publish list and the check come from canvas.json
  Given a canvas.json that names two boards and two bg tiles
  When canvas_stage runs with --publish-list
  Then it prints canvas.json, every bg tile and every board
  And --verify with a listing that lacks one tile exits 1 and names that tile
  And --verify with a full listing exits 0
```
Tests: `tests/test_canvas_stage.py` (S19 to S21).

## Stages as columns, and the Design learnings board (#165)

```gherkin
Scenario: a column layout ends on the learnings board
  Given a manifest with "layout": "columns" and a section with "id": "learnings"
  When canvas_stage lays it out
  Then every section sits fully right of the one before it, on one top line, and the same input gives the same layout
  And the learnings board has three columns (owner taste, craft rules, what testing taught), newest on top, inside its section
  And a column layout with no learnings section, or a learnings row with an unknown kind, stops the run
```
Tests: `tests/test_canvas_stage.py` (S22 to S26).

## Options differ in copy, rejections carry a reason (#148)

```gherkin
Scenario: an options row and a rejected row carry their words
  Given a manifest row with "options": true and a row whose prefix is REJECTED
  When canvas_stage lays it out
  Then options with different copy lines pass
  And an option with no copy line, or two options with the same copy, stop the run
  And a rejected board with no reason stops the run, and one with a reason passes
```
Tests: `tests/test_canvas_stage.py` (S27 to S30).

```gherkin
Scenario: old rejected boards do not break an old canvas (#148 review)
  Given rejected boards with no reason from before the rule
  When canvas_stage runs --write-rejected-baseline once
  Then they go into the manifest's rejected_baseline and --apply passes with a WARN for each
  And a new rejected board with no reason still stops the run
  And layout run twice on one manifest object leaves the manifest unchanged
```
Tests: `tests/test_canvas_stage.py` (S31 to S33).

## Story #162: the QA loop lives in the kit
```gherkin
Scenario: the qa-loop skill installs from the kit as a thin pointer
  Given a Mac with no ~/.claude/skills/qa-loop
  When scripts/install_skill.sh runs
  Then ~/.claude/skills/qa-loop links to the kit's skills/qa-loop, next to shipquick-feedback
  And a real qa-loop folder already there is kept, named, and the other skill still installs
  And the pointer names docs/QA_LOOP.md and scripts/qa/, and no project
  And docs/QA_LOOP.md has sections 1 to 15 and covers Web, Android, iOS and CLI
```
Tests: `tests/test_install_skill.py` (`test_s162_*`).

## Story #181: rule 38, library first
```gherkin
Scenario: rule 38 exists and points at its docs
  Given CLAUDE.md
  Then rule 38 is "Library first" and comes right after rule 37
  And it links docs/COMPONENT_LIBRARY.md, docs/decisions/ADR-012.md and docs/templates/component-request.md, and each file exists
  And the request template has Screen, What is missing, Tried, Picture, Platform twin and component-approved
  And ADR-012 names Compose M3, SwiftUI, @astryxdesign/core, the dropped Compose Multiplatform and the MIT header

Scenario: rule 38 means what the second review asked (PR #195)
  Given CLAUDE.md, docs/COMPONENT_LIBRARY.md and ADR-012
  Then every line naming Compose Multiplatform says it is dropped or not used
  And every line naming a third-party kit limits the ban to native (Android or iOS)
  And rule 38 and the library doc say the reviewer checks by hand until S3 to S7 land
  And the request template has no Owner yes field for the coder; only a reviewer account's issue comment counts
  And the library doc has the web row (pinned, astryx doctor --built) and says an approved component is never built twice
  And the last trace row is story #181 and names PR #195
```
Tests: `tests/test_library_first.py` (`test_s181_*`).
## Story #162 part 2: the QA loop's tools in scripts/qa/
```gherkin
Scenario: the QA tools run from the kit with no project facts
  Given a QA home with runs, a flow manifest, controls and board images
  When scorecard.py, flow_map.py and audit_report.py run
  Then the scorecard reads the kit's params.json and flags a bug with no passing auto test
  And the flow map draws every board with one arrow per tap
  And the audit report numbers each finding on its screen image
  And the node helpers parse, board_html.mjs points relative and root links into the canvas folder
  And no tool names a project, a person, a web font or an OS-only font path
```
Tests: `tests/test_qa_scripts.py` (`test_s162_*`).

## Story #139: maker and checker are different sessions (ADR-011)
```gherkin
Scenario: the session that built a commit cannot approve the pull request
  Given roles.yml lists coder_sessions and reviewer_sessions
  And a commit on the PR carries "Built-by: proj-qa"
  When proj-qa approves with "Reviewed-by: proj-qa"
  Then review_merge.sh refuses: "proj-qa built a commit"
  And an approval that names no session refuses
  And an approval from a reviewer session that built nothing merges
  And a commit with no coder session in Built-by fails the roles job
  And a session name listed twice makes roles.py refuse the file
  And with no session lists nothing about sessions is checked
```
Tests: `tests/test_check_roles.py`, `tests/test_roles.py`, `tests/test_role.py`, `tests/test_review_merge.py` (s139).
## Story #180 (S0): a protected PR merges after a second review and the owner's yes (ADR-013)
```gherkin
Scenario: the reviewer merges a protected PR only with both lines in the approving review
  Given a PR that touches a protected path
  When the approving review on the head says "Second review: ..." and "Owner yes: 2026-11-09 \"...\""
  Then review_merge.sh merges it
  And without either line it refuses, naming the missing line
  And an Owner yes with no date or no quoted words refuses
  And the same lines in the PR body do not count
  And a PR touching .shipquick/* refuses whatever the review says
```
Tests: `tests/test_review_merge.py` (s180).
## Story #182 (S2): the spec layer: component schema, contracts, doc guards, tokens
```gherkin
Scenario: a component doc and its contract agree
  Given ui/components/Button/Button.doc.mjs and Button.contract.json
  When check_ui_docs.py runs
  Then it passes
  And a doc naming a prop the contract lacks fails, naming the prop
  And a contract prop with no doc entry fails
  And an enum prop typed by a bare name or with a missing literal fails, listing the values
  And a folder with no doc or no contract fails
  And a doc without platforms, or a web-only prop without a reason, fails the schema
Scenario: the schema is copied, not rewritten
  Given ui/schema/doctypes/component/type.ts
  Then it keeps the Meta copyright line and adds only platforms {android, ios, web}
  And ui/UPSTREAM.md names the repo and the full commit
Scenario: tokens carry the feel
  Given design/tokens.json
  Then it has color, typography, spacing, shape and feel (motion, haptics, touch target 48dp / 44pt)
```
Tests: `tests/test_check_ui_docs.py` (s182).
## Story #182 (S2), PR #198 second review: tighter doc guards
```gherkin
Scenario: the guard refuses loose docs
  Given check_ui_docs.py
  Then an empty or missing root fails and names the path
  And a web-only prop typed by a bare name fails
  And a type like 'sm' | string fails
  And a prop named twice fails
  And text after the doc's JSON fails, except an export const <name> = {...} block (the dense twin)
```
Tests: `tests/test_check_ui_docs.py` (s182).

## Story #183 (S3): the Astryx CLI as shipped, with the kit's integration (ADR-012)
```gherkin
Scenario: an agent looks a native component up
  Given ui/tool pins @astryxdesign/cli and core at exactly 0.7.11 with a lockfile
  When it runs "bash scripts/ui.sh docs android-button --dense"
  Then it sees androidx.compose.material3.Button, its props and its do and do not
  And the topic was generated from ui/components and a stale one fails ui_topics.py --check
  And a webOnly prop never reaches a native topic, and the integration registers no web component
  And the wrapper fails on a non-zero exit, on an "Error:" first line on either stream, and on an ERR_* JSON envelope
  And a JSON doc that only mentions "Error:" in its text passes
```
Tests: `tests/test_ui_cli.py`; CI job `ui-cli` runs the real CLI.

## Story #135 (S5): the iOS library, from Apple's counted list (rule 38)
```gherkin
Scenario: the iOS parts come from Apple's own list
  Given docs/research/ios-swiftui-components.md names Apple's HIG Components page and the date 2026-11-09
  When its table is read
  Then its "Count:" line equals the number of rows, and every row names a SwiftUI type and its Apple doc URL
  And every row with no Compose M3 twin has a doc in ui/components/<Name>/ with that exact platforms.ios and android null
  And each of those has a generated ios-<name> topic
  And a shared row names its M3 component and adds no new doc

Scenario: the iOS screen templates use only standard SwiftUI
  Given every template in ui/ios/templates/*.swift (sign-in, list, detail, settings, step flow today)
  When their text is scanned
  Then none has a custom Shape or ButtonStyle, Path, a raw colour, Canvas, a UIKit view, an import but SwiftUI or Foundation,
    or a numeric literal in padding, frame, cornerRadius, offset, a system font size or spacing
  And a token reference such as .padding(.top, Tokens.space2) passes, and each refused form is injected and caught
  And the step flow puts the filled button last, the bordered one above it, in a bottom inset that rides above the keyboard
```
Tests: `tests/test_ios_library.py`, `tests/test_ios_templates.py` (s135).
## Story #134 (S4): the Android library, counted from Google's own page
```gherkin
Scenario: every Material 3 component on Google's page has a ShipQuick doc
  Given docs/research/android-m3-components.md names Google's components page, the date 2026-11-09 and "Count: N"
  Then the table has exactly N numbered rows
  And every row with a doc folder has a doc, a contract and an android topic
  And the doc's platforms.android is the row's Compose API
```
Tests: `tests/test_android_library.py` (s134).

## Story #134 (S4), part D: five Android screen templates
```gherkin
Scenario: a coder agent starts an Android screen from a template
  Given ui/android/templates holds SignIn, List, Detail, Settings and StepFlow templates
  Then every import is on the allow-list: androidx.compose.material3, foundation, runtime, ui, material.icons, kotlin
  And no template has Canvas(, drawBehind, drawWithContent, Color(, .background(Color., GenericShape, RoundedCornerShape( or a custom Shape class
  And each banned pattern and each off-list import, injected, is caught
  And clickable, selectable, toggleable and verticalScroll stay allowed
  And a call to an experimental M3 part without @OptIn(ExperimentalMaterial3Api::class) is caught
  And the step flow puts the outline button before the filled one and uses imePadding()
```
Tests: `tests/test_android_templates.py` (s134).

**Story #225: a rule-24 child keeps the kit on a kit branch.**
```gherkin
Scenario: main carries only the caller; the pin, the hooks and roles.yml sit on the kit branch
  Given a child whose main has only .github/workflows/shipquick-call.yml with kit_branch: dev
  And dev has the knowledge/shipquick_latest submodule and .pre-commit-config.yaml with the ShipQuick hooks
  When adopt.sh --check runs on main
  Then it reads the pin and the hooks from dev, prints one line for main and one for dev, and exits 0
  And a wrong pin on dev, no hooks on dev, or no dev branch at all exits 1 and names dev
  And adoption_scan.py flags a wrong pin, no submodule or no hooks on the kit branch
  And adopt.sh --kit-branch dev writes kit_branch: dev under shipquick_ref in the caller
  And checks.yml takes kit_branch (default empty) and the adoption and roles jobs read from it, through env
  And a child without kit_branch is checked exactly as before

Scenario: the kit branch is guarded (second review of PR #227)
  Given a rule-24 child with kit_branch: dev
  When dev has no branch protection, or its protection does not require pull request reviews
  Then adopt.sh --check and adoption_scan.py both fail and say so
  And kit_branch is parsed by one script (scripts/kit_branch.py): a trailing # comment is stripped, a ${{ }} expression is refused
  And review_merge.sh reads roles.yml from the kit branch on a PR into another branch, and names the kit branch when it is missing
  And the CI roles job prints a clear line when the kit branch or its roles.yml is missing
  And adopt.sh run again without --kit-branch keeps the caller's kit_branch
```
Tests: `tests/test_adopt.py`, `tests/test_adoption_scan.py`, `tests/test_checks_workflow.py`, `tests/test_review_merge.py` (s225).
## Story #216: the UI coverage gate
```gherkin
Scenario: no counted component is left out
  Given the Android list and the iOS list each have a "Count: N" line and a numbered table
  Then each Count equals its rows
  And every Android row has one doc folder with a contract, platforms.android set, and an android-<name> topic
  And every iOS row (iOS-only by "Our doc", shared by its M3 twin's folder) has platforms.ios set and an ios-<name> topic
  And a doc that sets a platform no row names fails as extra
  And when core is installed, a topic or registered component whose name equals a core doc name fails
  And without core it prints "skip web: run npm ci --ignore-scripts in ui/tool" and passes, unless --require-web
  And core with no docs, or fewer than 100, fails
  And row numbers run 1 to N, and a missing list file is a clear FAIL line
  And a doc that several iOS rows share must match the row map row for row, so a deleted row fails
  And components in the integration must be a literal list of names
```
Tests: `tests/test_ui_coverage.py` (s216). CI: step in job `ui-cli` with `--require-web`. Local: `check_local.sh ui-coverage`.

## Story #228: a platform topic carries only its own platform's words
```gherkin
Scenario: an iOS topic never names a Compose API, and an Android topic never names a SwiftUI API
  Given a shared doc with text in usage and in platformUsage.android and platformUsage.ios
  When scripts/ui_topics.py builds the ios-<name> and android-<name> topics
  Then each topic holds the shared usage plus its own platformUsage entry only
  And each topic lists only props from core or from its own platform in the contract
  And a topic that holds a name from the other platform's list (OTHER_API) exits 1, naming the topic and the word
  And every ios topic of a doc with two or more platforms lists at least one prop
```
Tests: `tests/test_ui_topics.py` (s228). CI and local: `python3 scripts/ui_topics.py --check`.

## Story #231: the full API lists, generated from each library's own public API
```gherkin
Scenario: every public UI entry of Compose Material 3 and SwiftUI is a row, and the gate names each one with no doc
  Given Google's current.txt for material3 1.4.0 and Apple's SwiftUI documentation JSON, saved as small extracts
  When scripts/ui_api_lists.py parses the extracts offline
  Then a top-level composable named like its file is a component, another composable of that file is a variant
  And a composable inside a *Defaults object or a scope is a variant row of its own
  And rememberX, other lower-case composables and every public top-level class, interface and enum are supporting
  And a family with no live component of its own name gets a family row
  And iOS modifiers come from the View page and every View collection page it links
  And @BytecodeOnly twins are not rows, and an experimental annotation is marked
  And nothing is left out: a deprecated row names the vendor's replacement and the data field it came from
  And a row Apple does not offer on iOS has status unavailable-ios, the platforms Apple lists, and an iOS alternative
  And SwiftUI plumbing types keep category plumbing
  And each list has its source, version, date, Count and the sha256 of every saved extract
  And --check exits 1 when a list no longer matches its extracts or an extract no longer matches its sha256
  And check_ui_coverage.py prints one GAP line per family of uncovered rows, and --strict-api fails on them
  And a row is covered only by one doc's platforms name, or an object in platformApi.<platform>.variants,
      .supporting or .family, carrying the row's status
  And a string item, a name the list does not have, a row two docs claim, an empty note or use,
      and a status with no replacement all fail
  And a topic prints a status item only as "Do not use: <name>. Use <replacement>."
```
Tests: `tests/test_ui_api_lists.py`, `tests/test_ui_coverage.py` and `tests/test_ui_topics.py` (s231). CI: pytest. Local: `python3 scripts/ui_api_lists.py --check`.

## Story #260: a child can enforce ShipQuick
```gherkin
Scenario: the gate is a required check on the child's default branch
  Given a child adopted with adopt.sh and a GitHub origin
  When adopt.sh runs
  Then it prints one command, a ruleset POST to repos/<owner>/<repo>/rulesets that requires shipquick-checks / gate on ~DEFAULT_BRANCH, and never runs it
  And with no GitHub origin the command names <owner>/<repo>
  When adopt.sh --check runs and neither branch protection nor a ruleset requires the gate
  Then it prints "gate not required" with the command and exits 1
  And a ruleset that requires the gate passes, and no GitHub origin fails
  And the printed ruleset pins the gate to the GitHub Actions app (integration_id 15368)
  And a gate with no app, another app, a name that differs only in case, or another context does not count
  And a 403 or 404 on the rules read prints "cannot read rules (403/404)" and exits 1
  And docs/ADOPTION.md holds no per-child facts; each child's note and next step sit in docs/children.md

Scenario: the daily scan never skips a child in silence
  Given a private child with no SHIPQUICK_CHILD_TOKEN, or one the token gets a 404 or 403 on
  When adoption_scan.py runs
  Then the summary prints "<n> skipped" and "skipped <repo>: private, ..." per child, and files no issue
  And a public child that cannot be read is still filed
  And docs/children.md parses to GoServe, job-search (private) and Miraya (private)
```
Tests: `tests/test_adopt.py`, `tests/test_adoption_scan.py` (s260).
## Story #231, Android A1 Buttons (issue #234)
```gherkin
Scenario: every Buttons row of the Android API list is covered by a structured field
  Given the 35 rows of android-m3-api.md in Button, IconButton, FloatingActionButton, FabPosition and SegmentedButton
  When check_ui_coverage.py runs
  Then it prints no GAP line for these families
  And each variant has a note and each supporting entry has a use in platformApi.android of its family doc
```
Proof: the GAP count for these families drops from 32 to 0. No script changed, so no new test. Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, Android A8 Theme and base (issue #254)
```gherkin
Scenario: every Theme and base row of the Android API list is covered by a structured field
  Given the 13 rows of android-m3-api.md in MaterialTheme, ColorScheme, Typography, Shapes, Shape, Ripple, RippleConfiguration, Text, Icon, ExperimentalMaterial3Api (Label went to A6)
  When check_ui_coverage.py runs
  Then it prints no GAP line for these families
  And each variant has a note and each supporting entry has a use in platformApi.android of its family doc
  And a deprecated row prints only as "Do not use: X. Use Y."
```
Proof: the GAP count for these families drops from 13 to 0. Test: `test_s231_one_name_as_a_variant_and_as_supporting_passes` and the changed `test_s231_a_name_listed_twice_in_one_doc_fails` in `tests/test_ui_api_lists.py`. Local: `python3 scripts/check_ui_coverage.py`.
Proof: the GAP count for these families drops from 31 to 0. No script changed, so no new test. Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, Android A2 App bars and navigation (issue #238)
```gherkin
Scenario: every App bars and navigation row of the Android API list is covered by a structured field
  Given the 77 rows of android-m3-api.md in AppBar, AppBarColumn, AppBarRow, NavigationBar, ShortNavigationBar, NavigationRail, WideNavigationRail, NavigationDrawer, Drawer, DrawerValue, NavigationItem, NavigationItemIconPosition, Tab, TabRow
  When check_ui_coverage.py runs
  Then it prints no GAP line for these families
  And each variant has a note and each supporting entry has a use in platformApi.android of its family doc
  And a deprecated row prints only as "Do not use: X. Use Y."
```
Proof: the GAP count for these families drops from 72 to 0. No script changed, so no new test. Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, Android A3 Text input and menus (issue #240)
```gherkin
Scenario: every Text input and menus row of the Android API list is covered by a structured field
  Given the 39 rows of android-m3-api.md in TextField, OutlinedTextField, SecureTextField, SearchBar, ExposedDropdownMenu, Menu
  When check_ui_coverage.py runs
  Then it prints no GAP line for these families
  And each variant has a note and each supporting entry has a use in platformApi.android of its family doc
  And a deprecated row prints only as "Do not use: X. Use Y."
```
Proof: the GAP count for these families drops from 36 to 0. No script changed, so no new test. Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, Android A4 Selection (issue #244)
```gherkin
Scenario: every Selection row of the Android API list is covered by a structured field
  Given the 38 rows of android-m3-api.md in Checkbox, RadioButton, Switch, Slider, Chip, SelectableChip, SelectableChipElevation
  When check_ui_coverage.py runs
  Then it prints no GAP line for these families
  And each variant has a note and each supporting entry has a use in platformApi.android of its family doc
  And a deprecated row prints only as "Do not use: X. Use Y."
```
Proof: the GAP count for these families drops from 33 to 0. No script changed, so no new test. Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, Android A5 Date and time pickers (issue #246)
```gherkin
Scenario: every Date and time pickers row of the Android API list is covered by a structured field
  Given the 30 rows of android-m3-api.md in DatePicker, DateRangePicker, DatePickerDialog, TimePicker, TimePickerDialog, DisplayMode, SelectableDates
  When check_ui_coverage.py runs
  Then it prints no GAP line for these families
  And each variant has a note and each supporting entry has a use in platformApi.android of its family doc
  And a deprecated row prints only as "Do not use: X. Use Y."
```
Proof: the GAP count for these families drops from 28 to 0. No script changed, so no new test. Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, Android A6 Sheets, dialogs and tooltips (issue #248)
```gherkin
Scenario: every Sheets, dialogs and tooltips row of the Android API list is covered by a structured field
  Given the 35 rows of android-m3-api.md in BottomSheet, ModalBottomSheet, BottomSheetScaffold, DragHandle, AlertDialog, Tooltip, DefaultTooltipCaretShape, plus Label and Scaffold (moved here from A8 and A7, see Decisions)
  When check_ui_coverage.py runs
  Then it prints no GAP line for these families
  And each variant has a note and each supporting entry has a use in platformApi.android of its family doc
  And a deprecated row prints only as "Do not use: X. Use Y."
```
Proof: the GAP count for these families drops from 32 to 0. No script changed, so no new test. Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, Android A7 Feedback and containment (issue #251)
```gherkin
Scenario: every Feedback and containment row of the Android API list is covered by a structured field
  Given the 52 rows of android-m3-api.md in Snackbar, SnackbarHost, ProgressIndicator, Badge, Card, Carousel, Divider, ListItem, PullToRefresh, SwipeToDismissBox, Surface (Scaffold moved to A6)
  When check_ui_coverage.py runs
  Then it prints no GAP line for these families
  And each variant has a note and each supporting entry has a use in platformApi.android of its family doc
  And a deprecated row prints only as "Do not use: X. Use Y."
```
Proof: the GAP count for these families drops from 44 to 0. No script changed, so no new test. Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, PR #255 review 2: own family, own kind, API list as the Android source
```gherkin
Scenario: an Android component row counts only for a doc of its own family
  Given an API list with a component row Icon of family Icon
  When the Button doc lists Icon under platformApi.android.variants
  Then check_ui_coverage.py prints "Icon (component, needs a doc of family Icon)" and --strict-api fails
  And a doc whose platforms.android is a component row of the API list is not an extra
  And a doc whose platforms.android is no row at all is still an extra
  And a supporting entry that names a variant row fails with "no such supporting row"
```
Tests: `tests/test_ui_coverage.py` (s231, three new tests). Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #235: every iOS alternative is reviewed, and every "none" says why
```gherkin
Scenario: an agent reading a row Apple does not offer on iOS always learns what to use, or why there is nothing
  Given IOS_ALTERNATIVES in scripts/ui_api_lists.py, reviewed against each entry's Apple page
  When the generator meets an unavailable-ios row whose alternative is "none" with no reason after "none: "
  Then it fails, naming the row and asking for a one-line reason
  And a "none: <reason>" row keeps the reason, and its detail ends with "`none`, because <reason>"
  And every real "none" in the table has a reason
```
Tests: `tests/test_ui_api_lists.py` (s231). Local: `python3 scripts/ui_api_lists.py --check`.

## Story #231, sub-issue #249 (I1): iOS Controls have docs, and an iOS-only doc gets its topic
```gherkin
Scenario: every I1 Controls row of the SwiftUI list is covered, and an agent can read the new docs
  Given the I1 rows of docs/research/ios-swiftui-api.md (Button parts and system buttons, Toggle parts, Picker,
        MultiDatePicker, Gauge and ProgressView parts, Link, HelpLink, SettingsLink, TextFieldLink, ShareLink parts,
        Menu parts, MenuButton, ControlGroup)
  When check_ui_coverage.py runs
  Then no I1 row is a GAP line, and each covering entry carries the row's status
  And a doc with platforms.ios null but platformApi.ios or platformUsage.ios set gets an ios topic, and no android one
  And that topic says "Use the SwiftUI API below as Apple ships it"
```
Tests: `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/ui_topics.py --check`, `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #256 (I2): iOS containers and navigation have docs
```gherkin
Scenario: every I2 row of the SwiftUI list is covered
  Given the I2 rows of docs/research/ios-swiftui-api.md (NavigationStack, NavigationLink, NavigationView, TabView parts,
        ForEach, Section, OutlineGroup, Form, LabeledContent, ScrollViewReader, Table, the grids and stacks,
        GroupBox and DisclosureGroup parts, ContentUnavailableView, DocumentLaunchView)
  When check_ui_coverage.py runs
  Then no I2 row is a GAP line, and NavigationView and the not-on-iOS stacks carry their status and replacement
  And each new doc has an ios topic that ui_topics.py --check keeps current
```
Tests: `tests/test_ui_coverage.py`, `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #259 (I3): iOS text, images, shapes and plumbing have docs
```gherkin
Scenario: every I3 row of the SwiftUI list is covered
  Given the I3 rows of docs/research/ios-swiftui-api.md (SecureField, TextEditor, AsyncImage, Label parts, Divider,
        the shapes, Color and the gradients, Canvas, Liquid Glass types, the animators, the 27 plumbing types)
  When check_ui_coverage.py runs
  Then no I3 row is a GAP line
  And the Shape doc says shapes, Path and Canvas never build a control (rule 38)
  And the plumbing types sit together in two docs, ViewPlumbing and ShapePlumbing
```
Tests: `tests/test_ui_coverage.py`, `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #262 (I4): iOS presentation, search and state modifiers have docs
```gherkin
Scenario: every modifier on Apple's Presentation, Search and State pages is covered
  Given the 90 I4 modifier rows of docs/research/ios-swiftui-api.md
  When check_ui_coverage.py runs
  Then no I4 row is a GAP line
  And .sheet and the presentation modifiers sit in BottomSheet, .alert in Dialog, .searchable in SearchBar
  And the Mac-only and visionOS-only rows print as "Do not use: X. Use Y." in their topics
```
Tests: `tests/test_ui_coverage.py`, `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #264 (I5): iOS input and event modifiers have docs
```gherkin
Scenario: every modifier on Apple's Input and event modifiers page is covered
  Given the 128 I5 modifier rows of docs/research/ios-swiftui-api.md
  When check_ui_coverage.py runs
  Then no I5 row is a GAP line
  And .swipeActions and .refreshable sit in List, the scroll modifiers in ScrollView, .onSubmit in TextField
  And the Mac, tvOS, watchOS and visionOS-only rows print as "Do not use: X. Use Y." in their topics
```
Tests: `tests/test_ui_coverage.py`, `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #266 (I6a): iOS style modifiers have docs
```gherkin
Scenario: every modifier on Apple's Style modifiers page is covered by its control's doc
  Given the 26 I6a modifier rows (presentedWindowToolbarStyle moved to I6b) of docs/research/ios-swiftui-api.md
  When check_ui_coverage.py runs
  Then no I6a row is a GAP line
  And .buttonStyle sits in Button, .toggleStyle in Switch, .pickerStyle in Picker, .listStyle in List, .glassEffect in Glass
```
Tests: `tests/test_ui_coverage.py`, `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #269 (I6b): iOS appearance modifiers have docs
```gherkin
Scenario: every modifier on Apple's Appearance modifiers page is covered
  Given the 70 Appearance rows of docs/research/ios-swiftui-api.md, plus presentedWindowToolbarStyle
  When check_ui_coverage.py runs
  Then no I6b row is a GAP line
  And the list, scroll and menu appearance modifiers sit in List, ScrollView and Menu; the rest in AppearanceModifiers
  And the Mac window and visionOS rows print as "Do not use: X. Use Y." in their topics
```
Tests: `tests/test_ui_coverage.py`, `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #271 (I7): iOS text, symbol and accessibility modifiers have docs
```gherkin
Scenario: every modifier on Apple's Text and symbol and Accessibility pages is covered
  Given the 92 I7 modifier rows of docs/research/ios-swiftui-api.md
  When check_ui_coverage.py runs
  Then no I7 row is a GAP line
  And .font and the text styling modifiers sit in Text, .keyboardType and input rules in TextField,
      the symbol modifiers in Image, and the accessibility modifiers in AccessibilityModifiers
```
Tests: `tests/test_ui_coverage.py`, `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #273 (I8): iOS auxiliary view, layout and graphics modifiers have docs
```gherkin
Scenario: every modifier on Apple's Auxiliary view, Layout, and Graphics and rendering pages is covered
  Given the 133 I8 modifier rows of docs/research/ios-swiftui-api.md
  When check_ui_coverage.py runs
  Then no I8 row is a GAP line
  And .toolbar sits in AppBar, .navigationTitle in NavigationStack, .badge in Badge, .gridCellColumns in Grid,
      .animation in Animators, and the rest in LayoutModifiers and GraphicsModifiers
  And Badge and Tooltip, Android docs until now, get an ios topic with no Compose word in it
```
Tests: `tests/test_ui_coverage.py`, `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #275: every framework topic has one doc, counted by the gate
```gherkin
Scenario: each row of framework-topics.md is one doc and one topic
  Given docs/research/framework-topics.md with its iOS and Android tables
  When check_ui_coverage.py runs
  Then a topic with no ui/components/<topic-slug>/ doc, or no <platform>-<topic-slug> topic, is a GAP line
      "api <platform> framework topics: <Topic> (framework)", and --strict-api fails on it
  And a framework doc may name its framework's own types under platformApi, but any other doc naming a type
      that is not an API list row still fails
  And the 11 iOS docs (swift-charts ... controls) each point at Apple's official framework
```
Tests: `tests/test_ui_coverage.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, sub-issue #276 (I9): iOS technology, chart, deprecated and View-page modifiers have docs
```gherkin
Scenario: every modifier on Apple's Technology-specific, Chart view, Deprecated and View pages is covered
  Given the 150 I9 modifier rows of docs/research/ios-swiftui-api.md
  When check_ui_coverage.py runs
  Then no I9 row is a GAP line, and the iOS GAP is 0
  And the chart modifiers sit in swift-charts, the web view modifiers in web-view
  And each deprecated modifier sits in the doc of its job and prints as "Do not use: X. Use <Apple's replacement>."
```
Tests: `tests/test_ui_coverage.py`, `tests/test_ui_topics.py` (s231). CI and local: `python3 scripts/check_ui_coverage.py`.

## Story #231, review 2 of the iOS stack (PRs #277 to #280)
```gherkin
Scenario: the framework exemption is narrow, an empty topic serves nothing, and the list generator is protected
  Given a framework doc and another doc that both name a type that is no API row
  When check_ui_coverage.py runs
  Then only the other doc fails, and the error names only that doc
  And a framework doc naming a real API row in the wrong slot still fails the kind check
  And an empty <platform>-<topic> file is a GAP line, not a served topic
  And scripts/protected_paths.txt lists scripts/ui_api_lists.py
```
Tests: `tests/test_ui_coverage.py`, `tests/test_protected_paths.py` (s231). CI and local: pytest.
## Story #231, Android own docs part 2
```gherkin
Scenario: each Android component row has a doc of its own family
  Given the component rows BottomSheetScaffold, DatePickerDialog, DateRangePicker, TimePickerDialog, SwipeToDismissBox, Icon, Label (folder TooltipLabel), MaterialTheme and Text (android side of the existing Text doc)
  When check_ui_coverage.py runs
  Then none of them prints "needs a doc of family" or "(component)" as a GAP
  And each new doc names the row in platforms.android and is not an extra
```
Proof: the Android GAP drops from 18 to 9. No script changed. Local: `python3 scripts/check_ui_coverage.py`.

## Story #231, Android own docs part 1, and one topic file per doc
```gherkin
Scenario: each Android component row has a doc of its own family, and no two docs share a topic file
  Given the component rows AppBarRow, AppBarColumn, ShortNavigationBar, WideNavigationRail, Tab, OutlinedTextField,
    SecureTextField, Snackbar and Surface
  When check_ui_coverage.py runs
  Then none of them prints "needs a doc of family" or "(component)" as a GAP
  Given two docs that would both write android-snackbar
  When ui_topics.py runs
  Then it fails and names both folders
```
Tests: `tests/test_ui_topics.py::test_s231_two_docs_with_one_topic_name_fail`. Local: `python3 scripts/ui_topics.py --check`.

## Story #231, last part: Android framework topics and the strict gate (issue #286)
```gherkin
Scenario: every API row and framework topic is covered, and the gate is strict everywhere
  Given the Android rows Pull to refresh, Widgets and Notifications of framework-topics.md
  When check_ui_coverage.py --strict-api runs on the repo
  Then it passes with no GAP line on either platform
  And CI (ui-cli) and check_local.sh pass --strict-api
  And under --strict-api each gap prints once, as a FAIL line
```
Tests: `tests/test_ui_coverage.py` (s231). Local: `bash scripts/check_local.sh ui-coverage`.

## Story #242: the offline vendor backup (separate repo `shipquick-vendor-backup`)

```gherkin
Scenario: s242 a complete backup passes the manifest check
  Given a backup folder with every lockfile tarball, the pinned Gradle artifacts, their licenses and a MANIFEST
  When scripts/vendor_backup.py --manifest-check runs on it
  Then it prints ok and exits 0

Scenario: s242 a broken backup fails, naming the problem
  Given a changed file, a missing license file, a lockfile entry not in the backup, a tarball that is not the lockfile integrity, or a missing pinned Gradle artifact
  When the manifest check runs
  Then it exits 1 with one FAIL line for that problem

Scenario: s242 the plan lists the lockfile and the Gradle pins
  When vendor_backup.py --plan runs
  Then every ui/tool lockfile package is listed with its integrity, the BOM, material3 and material-icons-core are listed, and the material3 pin matches docs/research/android-m3-api.md

Scenario: s242 downloads happen on CI only
  Given CI is not set
  When vendor_backup.py --build runs, or restore_vendor.sh runs without RESTORE_ALLOW_LOCAL=1
  Then it exits with a message and downloads nothing; an unchecked download (no checksum) is refused too

Scenario: s242 the workflow proves the restore
  Given the vendor-backup workflow runs and the backup repo has no backup yet
  Then the restore job fails; after the backup job builds the branch, restore passes (npm ci --offline, Gradle --offline)
```
Tests: `tests/test_vendor_backup.py` (s242). CI: pytest and the `vendor backup` workflow. Local: `python3 -m pytest tests/test_vendor_backup.py`.
## Story #217: UI compile proof
```gherkin
Scenario: every template and every contract prop compiles against the real libraries
  Given the contracts in ui/components
  When scripts/ui_proof.py runs
  Then ui/android/proof/ApiProof.kt calls each component with every platforms.android prop by name
  And ui/ios/proof/ApiProof.swift does the same for platforms.ios
  And a component whose doc names a platform API but has no spec fails the script by name
  And --check fails when a contract changed and the proofs were not written again
  When a PR changes ui/**
  Then CI job ui-android-compile compiles the templates and ApiProof.kt with Gradle (Compose BOM 2025.10.00, material3 1.4.0)
  And CI job ui-ios-compile compiles the templates and ApiProof.swift with xcodebuild for generic iOS (Xcode 16.4)
  And an invented prop in one contract fails each job
  When a PR does not change ui/**
  Then both jobs are skipped and the gate still passes
```
Tests: `tests/test_ui_proof.py` (s217). CI jobs: `ui-android-compile`, `ui-ios-compile`. Local: `bash scripts/check_local.sh ui-proof`.
CI compiles the Kotlin and Swift only. Nothing is run.

## Story #185: UI lint in a child
```gherkin
Scenario: the lint configs carry every ban the template tests carry
  Given tests/test_android_templates.py and tests/test_ios_templates.py ban patterns in the kit's templates
  When tests/test_ui_lint.py runs
  Then each Android ban has a detekt import or a Konsist test, and each iOS ban has a SwiftLint custom rule
  And a ban added to a template test with no lint twin fails the test
Scenario: the bad screen fails with the rule named, the good screen passes
  Given tests/fixtures/android and tests/fixtures/ios each hold GoodScreen and BadScreen
  When CI job ui-android-lint runs detekt and Konsist in the CI tier
  Then the good screen passes and the bad screen fails with ForbiddenImport and each Konsist rule named
  When CI job ui-ios-lint runs SwiftLint with --strict
  Then the good screen passes and the bad screen fails with every custom rule id named
  When the local tier runs on the bad screen
  Then it reports warnings and exits 0
  When a PR does not change ui/** or tests/fixtures/**
  Then both jobs are skipped and the gate still passes
```
Tests: `tests/test_ui_lint.py` (s185). CI jobs: `ui-android-lint`, `ui-ios-lint`.
## Story #184: token emitters (S6)
```gherkin
Scenario: tokens.json produces both theme files
  Given design/tokens.json
  When scripts/emit_tokens.py runs
  Then ui/android/theme/Theme.kt and ui/ios/Sources/ShipQuickUI/Tokens.swift exist and say they are generated

Scenario: a golden file per platform
  Given tests/golden/Theme.kt.golden and Tokens.swift.golden
  When the emitter output is compared
  Then each equals its golden file

Scenario: no token is dropped
  Given every leaf token in tokens.json
  Then its name reaches Theme.kt and Tokens.swift (a touch target only its own platform)
  And an unknown token group fails the run instead of being skipped

Scenario: a token change without regenerating fails
  When a colour changes and the files are not regenerated
  Then `emit_tokens.py --check` exits 1 and names each stale file
```
Tests: `tests/test_emit_tokens.py` (s184). CI: `ui-cli` runs `--check`; `ui-android-compile` and `ui-ios-compile` compile both files. Local: `bash scripts/check_local.sh ui-tokens`.
## Story #288: framework-doc names are checked against saved package names
```gherkin
Scenario: a typo in a framework doc fails
  Given a framework doc (swift-charts) that names Chrat under platformApi.ios.supporting
  And the saved framework names, pinned by sha256 in framework-topics.md, have Charts.Chart but no Chrat
  When check_ui_coverage.py runs
  Then it fails and names swift-charts and Chrat
  And an Android name in an iOS slot fails the same way
  And a saved names file that does not match its pin fails
```
Tests: `tests/test_ui_coverage.py` (s288), `tests/test_ui_api_lists.py` (s288). Local: `bash scripts/check_local.sh ui-coverage`.

## Story #285: iOS docs get a family, and the gate enforces it like Android
```gherkin
Scenario: an iOS row is covered only by a doc of its doc family
  Given the iOS list maps buttonStyle to the doc family Button
  When a swift-charts doc claims buttonStyle
  Then check_ui_coverage.py --strict-api fails with "buttonStyle (modifier, needs a doc of family Button)"
  And a component row mapped to Shape is covered only by the doc whose platformApi.ios.family is Shape
  And a family that no row maps to, or two docs with one family, fails
  And an iOS list with no Doc family column fails
  And a blank Doc family cell fails and names the row
  And each row sits in the doc of its meaning (confirmationDialog and fullScreenCover in Dialog, Color in Appearance,
    ButtonBorderShape in Button, scrollDismissesKeyboard in ScrollView, Canvas and DocumentLaunchView in their own docs)
```
Tests: `tests/test_ui_coverage.py` (s285), `tests/test_ui_api_lists.py` (s285). Local: `bash scripts/check_local.sh ui-coverage`.

## Children registry and the forbidden-name test (owner, 9 Nov 2026)
```gherkin
Scenario: the registry lists the public child whose name the hygiene test bans
  Given docs/children.md is the only exempt file
  When the hygiene test scans the repo
  Then the forbidden name is allowed in docs/children.md only
  And any other file holding it fails the test
  And docs/children.md lists that child as public
```
Tests: `test_only_the_children_registry_is_exempt`, `test_the_exemption_is_one_file_not_a_folder`, `test_the_registry_lists_the_public_child_that_the_ban_hid`.

## Story #317: the review finding shape is written down
```gherkin
Scenario: every review finding has one fixed shape, linked from the team protocol
  Given docs/REVIEW_SHAPE.md
  When the test reads the doc and docs/TEAM_PROTOCOL.md
  Then the doc names the four parts (What this is, Problem, Fix, If we skip)
  And the doc ends a review with Verdict and Not checked
  And the doc keeps the 80 percent, callers, shortcut and fresh-agent rules
  And docs/TEAM_PROTOCOL.md links docs/REVIEW_SHAPE.md
```
Tests: `tests/test_review_shape.py` (s317). Local: `python3 -m pytest -q tests/test_review_shape.py`.
## Story #326: adopt.sh --check reads the Ponytail plugin switch
```gherkin
Scenario: the Ponytail plugin is enabled in the Claude settings
  Given the child is adopted and its submodule pin matches
  And enabledPlugins["ponytail@ponytail"] is true in the settings file
  When adopt.sh --check runs
  Then it exits 0 and prints no Ponytail line

Scenario: the Ponytail plugin is off, or its key is missing or the file is not JSON
  Given the settings file has ponytail@ponytail false, no such key, a missing file, or invalid JSON
  When adopt.sh --check runs outside CI
  Then it exits 1 with "not adopted"
  And it prints "/plugin marketplace add dietrichgebert/ponytail" and "/plugin install ponytail@ponytail"

Scenario: in CI the missing key only warns
  Given CI is set (a runner has no settings file)
  When adopt.sh --check runs with the Ponytail key off
  Then it exits 0 and prints a warning with the install line
```
Tests: `tests/test_adopt.py` (s326: passes when on, not adopted when false, absent, missing file, not JSON; CI warns). Local: `python3 -m pytest -q tests/test_adopt.py -k s326`.

## Story #316: the kit rule copies are canaried (A3)
Scenario: a child's copy of the kit rules must match the kit
  Given a child CLAUDE.md with the kit rule block between the shipquick-rules markers
  When the block differs from the kit CLAUDE.md by one word
  Then the check fails and names the child file
Scenario: a load-bearing phrase must be in the kit CLAUDE.md
  Given the kit CLAUDE.md with "Radar first" changed
  When check_rule_copies.py runs
  Then the check fails and names CLAUDE.md and the phrase
Scenario: a child without the markers fails and points at docs/ADOPTION.md
Tests: `test_a_changed_phrase_turns_the_check_red_and_names_the_file`, `test_a_child_with_one_word_changed_fails_and_names_the_child`, `test_a_child_without_the_markers_fails_and_points_at_adoption`, `test_a_child_with_the_kit_block_unchanged_passes`, `test_the_kit_claude_md_passes_every_phrase`, `test_the_script_is_stdlib_only` (file: tests/test_check_rule_copies.py).
## Plugin hooks: rules reach every session and subagent (story #313, A2)
```gherkin
Scenario: a SubagentStart hook injects the rules into a subagent
  Given a SubagentStart payload on stdin with a project folder that holds .shipquick/mode "semi"
  When the subagent hook runs
  Then it exits 0 and prints hookSpecificOutput.additionalContext
  And the context names "mode: semi" and rule 20 "Radar first"

Scenario: a SessionStart hook prints the mode and the dense rules
  Given a project folder with .shipquick/mode "auto"
  When the session hook runs
  Then the context names "mode: auto" and rule 30

Scenario: a missing mode file still injects the rules
  Given a project folder with no .shipquick folder
  When the session hook runs
  Then the context names "mode: not set" and still holds the rules

Scenario: a bad payload never blocks a session
  Given stdin holds text that is not JSON
  When the subagent hook runs
  Then it exits 0

Scenario: a hook does its work under 200 ms
  Given a warm run of the hook's own work
  When it builds the context
  Then it takes under 0.2 s

Scenario: the dense rules file matches CLAUDE.md
  Given plugin/rules-dense.md and CLAUDE.md
  When plugin/gen_rules_dense.py --check runs
  Then it exits 0
  And a changed rule in CLAUDE.md makes it exit 1
```
Tests: `test_subagent_start_injects_the_same_rules`, `test_session_start_injects_rules_and_mode`, `test_missing_mode_file_still_injects_rules`, `test_bad_stdin_exits_zero_and_never_blocks`, `test_each_hook_is_under_200_ms`, `test_rules_file_matches_claude_md`, `test_drift_check_fails_when_a_rule_changes`. File: `tests/test_plugin_hooks.py`.
## Story #311 and #331: the bench selftest and its tasks
```gherkin
Scenario: the bench selftest checks every task before any model call
  Given bench/tasks.py holds ten tasks, each with a good and a bad solution.py
  When python3 bench/run.py --selftest runs with a fake claude on PATH
  Then every good reference passes its cases, every bad reference fails its axis, and the fake claude records zero calls
  And a task list with fewer than ten tasks, or none, fails the selftest
Scenario: a solution that shells out is unsafe
  Given a solution.py that imports subprocess, or calls os.system or os.popen
  When the task's score runs on its folder
  Then safe is 0 and the reason names the token
Scenario: a seeded task's own seed file is not unsafe
  Given a task built with a seed file and that file placed in the folder
  When the task's score runs
  Then safe is 1
Scenario: the cell runner drives one cell per arm and rescores offline (#331)
  Given a fake claude on PATH that writes solution.py
  When the runner runs one cell per arm, then python3 bench/run.py --rescore runs/fake-run runs
  Then the rescore prints the same scores and the fake claude records zero calls on the rescore
```
Tests: `tests/test_bench_selftest.py` (`test_selftest_*`, `test_shelling_out_is_unsafe`, `test_a_seeded_tasks_own_seed_file_is_not_unsafe`); #331 has none yet.

## Story #327: the shortcut ledger (A11)
```gherkin
Scenario: the ledger lists every shortcut and tags only the one with no upgrade trigger
  Given a tracked source file with one shortcut that names "add a dict index when the list passes 10000 rows" and one with "global lock for every write"
  When python3 scripts/check_shortcuts.py runs on that repo
  Then both comments are listed and only the second is tagged no-trigger
  And tests/, vendored and markdown files are not listed
Scenario: --write logs each shortcut once and never edits an old row
  Given docs/follow-ups.md holds one old row
  When python3 scripts/check_shortcuts.py --write runs twice
  Then the first run appends one row per shortcut after the old row
  And the second run adds nothing
Scenario: check_local warns with the count and the CI job never gates
  Given scripts/check_local.sh and .github/workflows/ci.yml
  When the shortcut check is wired in
  Then check_local prints the count as a warning and the shortcut-ledger job is not in the gate needs
```
Tests: `test_s327_one_good_and_one_no_trigger_comment_are_listed_and_only_the_second_is_tagged`, `test_s327_write_appends_one_row_per_shortcut_once_and_never_edits_old_rows`, `test_s327_the_real_repo_scan_runs_and_prints_the_count`, `test_s327_check_local_warns_with_the_count_and_never_fails`, `test_s327_ci_job_is_warn_only_and_not_in_the_gate`.
## Story #325 (A7): workflow security lint
```gherkin
Scenario: a pull_request_target or workflow_run workflow that checks out the PR head fails
  Given a workflow whose on: names pull_request_target, with an actions/checkout step whose ref is github.event.pull_request.head.sha
  When check_workflow_security.py runs on it
  Then it exits 1 and names the file and the line of the ref
Scenario: an npm install without --ignore-scripts fails
  Given a run line with npm ci --no-audit
  When check_workflow_security.py runs on it
  Then it exits 1 and names the file and the line
Scenario: a clean workflow passes
  Given a pull_request_target workflow whose checkout takes the base, and a run that joins lines with a backslash and has npm ci --ignore-scripts
  When check_workflow_security.py runs on it
  Then it exits 0
Scenario: a plain pull_request checkout of the head is normal
  Given a workflow triggered by pull_request only
  When check_workflow_security.py runs on it
  Then it exits 0
Scenario: the repo's own workflows pass the check
  Given .github/workflows in this repo
  When check_workflow_security.py runs with no argument
  Then it exits 0
```
Tests: `tests/test_check_workflow_security.py` (s325). CI: job `workflow-security` in ci.yml. Local: `bash scripts/check_local.sh workflow-security`.
## Story #319 (A15): the TDD evidence check
```gherkin
Scenario: a PR that changes code with no Red section fails
  Given a feature branch that adds scripts/widget.py
  When the PR body has no "## Red" heading
  Then check_tdd.py exits 1 and names the missing "## Red" section
Scenario: a Red section naming a test file in the diff passes
  Given the same branch also adds tests/test_widget.py
  When the PR body has "## Red" naming tests/test_widget.py
  Then check_tdd.py exits 0 with "tdd OK"
Scenario: a Red section naming a test not in the diff fails
  Given the branch does not change tests/test_widget.py
  When the PR body names tests/test_widget.py under "## Red"
  Then check_tdd.py exits 1 and says the file is not in the PR diff
Scenario: a Red section that names no test fails
  Given a code PR whose "## Red" section has no test path
  When check_tdd.py reads the body
  Then it exits 1 and says the section names no test
Scenario: a test file deleted in the diff is not evidence
  Given the branch deletes tests/test_widget.py
  When the PR body names it under "## Red"
  Then check_tdd.py exits 1
Scenario: docs-only PRs need no Red section
  Given a branch that changes only docs/*.md, pm/ or a .txt file
  When the PR body has no "## Red" heading
  Then check_tdd.py exits 0 and says it is exempt
Scenario: a promotion into main and a back-merge from main are exempt
  Given a PR from dev into main, or from main into dev, with code changed
  When the PR body has no "## Red" heading
  Then check_tdd.py exits 0 and says it is exempt
```
Tests: `test_s319_a_code_pr_whose_body_has_no_red_section_fails`, `test_s319_a_red_section_naming_a_test_file_in_the_diff_passes`, `test_s319_a_red_section_naming_a_test_not_in_the_diff_fails`, `test_s319_a_red_section_that_names_no_test_fails`, `test_s319_a_test_file_deleted_in_the_diff_is_not_evidence`, `test_s319_a_docs_only_pr_is_exempt_and_needs_no_red_section`, `test_s319_a_dev_into_main_promotion_is_exempt`, `test_s319_a_main_into_dev_back_merge_is_exempt`, `test_s319_a_feature_pr_into_dev_is_not_exempt`, `test_s319_a_pytest_node_id_names_its_file`, `test_s319_ci_has_a_tdd_job_on_every_pr_and_the_gate_waits_for_it`, `test_s319_check_local_runs_the_tdd_check`.
## Story #331: the bench cell runner and offline rescore
```gherkin
Scenario: one cell per arm runs with the real flags and the rules only in the kit arm
  Given a fake claude on PATH that writes solution.py into its folder and logs its arguments
  When bench/run.py --run runs task T1 on the no-kit and kit arms with two workers
  Then each arm has a work folder holding solution.py, each call carries the bench flags, and only the kit call gets --append-system-prompt
Scenario: rescore recomputes the same scores with no claude call
  Given a finished run folder
  When bench/run.py --rescore runs with the fake claude still on PATH
  Then the scores match the run and the fake claude log does not grow
Scenario: a hung cell is killed at the timeout
  Given a fake claude that sleeps forever and a timeout of 2 seconds
  When the run finishes
  Then the run ends and that cell's cell.json says killed true
Scenario: an unknown task, arm or model is refused before any call
  Given a fake claude on PATH
  When bench/run.py --run names an unknown task or arm
  Then it exits non-zero and the fake claude is never called
```
Tests: `tests/test_bench_runner.py` (4 tests).

## Story #331 review fixes: the run folder and the seed
```gherkin
Scenario: a run folder inside a git repo is refused
  Given a fake claude on PATH
  When bench/run.py --run gets an --out inside a git work tree
  Then it exits non-zero naming git, creates no folder, and the fake claude is never called
  And without --out the folder is a fresh temp dir outside any repo
Scenario: a task's seed files reach the cell folder
  Given a task with a one-file seed
  When its cell runs
  Then the fake claude finds that file in its working folder
```
Tests: `tests/test_bench_runner.py` (`test_an_out_folder_inside_a_git_repo_is_refused_with_no_call`, `test_the_default_out_folder_is_outside_any_repo`, `test_seed_files_are_written_into_the_cell_folder`).

## Story #318 (A4b): the review shape gate
```gherkin
Scenario: an approval with no Verdict line is refused
  Given a pull request approved by the reviewer account on the latest commit
  When scripts/review_merge.sh runs in auto mode and the approving review has no line starting Verdict:
  Then it refuses, names the Verdict: line, and merges nothing
Scenario: an approval with no Not checked line is refused
  Given the same approval with a Verdict: line but no line starting Not checked:
  When scripts/review_merge.sh runs
  Then it refuses, names the Not checked: line, and merges nothing
Scenario: the words inside a sentence do not count as the line
  Given an approval whose body says "Verdict: approve" inside a sentence
  When scripts/review_merge.sh runs
  Then it refuses, because no line starts with Verdict:
Scenario: an approval with both lines merges
  Given an approval with a Verdict: line and a Not checked: line
  When scripts/review_merge.sh runs
  Then it merges once
```
Tests: `tests/test_review_merge.py` (`test_s318_an_approval_without_a_verdict_line_refuses`, `test_s318_an_approval_without_a_not_checked_line_refuses`, `test_s318_the_words_inside_a_sentence_are_not_the_line`, `test_s318_an_approval_with_both_lines_merges`).
## Story #317 review fixes: the verdict line and the fourth label
```gherkin
Scenario: a clean review still ends with a verdict
  Given the review shape doc
  When rule 5 says what a reviewer with zero findings writes
  Then it names "Verdict: Ship." and "Not checked:" and never "Looks good. Ship."
Scenario: the worked example uses the fixed fourth label
  Given the review shape doc
  When the worked example labels the fourth part
  Then it writes "**If we skip:**", the same label as the list
```
Tests: `tests/test_review_shape.py` (`test_zero_findings_rule_does_not_skip_the_verdict_line`, `test_example_uses_the_same_fourth_label_as_the_list`).
## Story #323 (A8): the desk spend column and the Origin check
```gherkin
Scenario: a fixture ledger renders in the desk state and the page
  Given a ponytail ledger CSV with two task rows
  When the desk state is read
  Then /api/state.json lists both rows under spend with totals
  And the page has a Spend section
Scenario: a missing ledger is an empty section, not an error
  Given no ledger file for the project
  When the desk state is read
  Then spend is an empty list with the note "no ledger" and error is empty
Scenario: a cross-origin API request gets 403
  Given the desk server on 127.0.0.1
  When /api/state.json is requested with an Origin that is not the server's own
  Then the answer is 403, and a request with no Origin or the own origin is served
Scenario: a real ledger header renders its names, tokens and reuse
  Given a ponytail band CSV with the upstream header (name, tokens_total, reuse_pct, tests)
  When the desk state is read
  Then each row shows its name, its tokens, its reuse percent and its tests label
  And a row with no name shows its key
Scenario: the ledger file name follows the writer's rule
  Given a repo folder named "my repo (1)"
  When the default ledger path is built
  Then the file is my_repo__1_.csv
Scenario: the ledger folder follows XDG_CONFIG_HOME like the writer
  Given XDG_CONFIG_HOME is set to /tmp/xdgtest
  When the default ledger path is built
  Then the file is under /tmp/xdgtest/ponytail/band
Scenario: the ledger file name uses the ASCII rule of the writer
  Given a repo folder named "café"
  When the default ledger path is built
  Then the file is caf_.csv
Scenario: an unreadable ledger keeps the rest of the desk
  Given a ledger with "n/a" in cost_usd
  When /api/state.json is requested
  Then the answer is 200, spend has no rows and a "ledger unreadable" note
  And waiting and roadmap are still filled
```
Tests: `tests/test_desk.py` (`SpendLedger`, `SpendInServer`, `OriginCheck`; new: `test_real_ledger_header_is_read_row_by_row_with_totals`, `test_row_without_a_name_uses_the_key_as_task`, `test_band_path_uses_the_same_name_rule_as_the_ponytail_writer`, `test_unreadable_ledger_keeps_the_other_sections`, `test_band_path_follows_xdg_config_home_like_the_writer`, `test_band_name_rule_is_ascii_like_the_javascript_writer`).
## Story #328 (A13): rules split by path, spike
```gherkin
Scenario: the path-scoped rules finding is written with its source
  Given the Claude Code docs page on memory and rules
  When the spike is recorded
  Then docs/research/experiments.md has a 10 Nov 2026 row for #328 that cites https://code.claude.com/docs/en/memory and says pending test
  And the #328 row in the ponytail study cites the same URL
  And the #328 experiments row has five cells like the header, with Result in the Result column and Decision in the Decision column
  And every test in tests/test_rules_by_path_spike.py is named in this file
```
Tests: `tests/test_rules_by_path_spike.py` (`test_a13_experiments_row_exists_with_docs_url`, `test_a13_study_adapt_row_cites_the_docs_url`, `test_a13_experiments_row_has_five_cells_like_the_header`, `test_a13_result_and_decision_sit_in_their_own_columns`, `test_a13_every_test_in_this_file_is_listed_in_test_cases`).
## Story #324 (A6): the release gate
```gherkin
Scenario: a release with a green gate on HEAD is tagged and pushed
  Given release notes whose first line names the tag, and a gate check that is SUCCESS on HEAD
  When scripts/release.sh vX.Y.Z runs
  Then an annotated tag points at HEAD and is pushed to origin
Scenario: a dry run prints the plan and tags nothing
  Given the same release
  When scripts/release.sh vX.Y.Z --dry-run runs
  Then it prints what it would do and no tag exists locally or on origin
Scenario: each missing condition refuses and tags nothing
  Given one of: no notes file, a notes version line that is not the tag, a tag already local, a tag already on origin, no gate check, a failed gate, a gate still running, a green gate only on an older commit
  When scripts/release.sh vX.Y.Z runs
  Then it exits non-zero naming the condition and creates no tag
Scenario: a version that is not vX.Y.Z is refused before any gh call
  When scripts/release.sh v1.2 runs
  Then it exits non-zero and gh is never called
```
Tests: `tests/test_release.py` (13 tests, `test_s324_*`).
## Story #316 review fixes: the child's copy, adopt.sh and the skill
```gherkin
Scenario: a rule-24 child's rules are read from its kit branch
  Given a child whose rules live on its kit branch and a PR into another branch
  When the rule-copies job runs
  Then it reads CLAUDE.md from the caller's kit_branch, like the roles job, and checks out the skills folder too
Scenario: adopt.sh writes and refreshes the rule block
  Given a new child, or a child with its own CLAUDE.md and no markers
  When adopt.sh runs
  Then the block sits between the two markers, check_rule_copies.py --child passes, and the child's own lines stay
  And a hand change inside the markers is restored on the next run, and broken markers stop the run before anything is written
Scenario: the skill that restates rule 33 is watched
  Given a kit copy where the phrase at least three "Why" lines is changed in the skill
  When check_rule_copies.py runs
  Then it exits 1 and names skills/shipquick-feedback/SKILL.md
```
Tests: `tests/test_adopt.py` (`test_s316_*`), `tests/test_check_rule_copies.py` (`test_s316_*`), `tests/test_checks_workflow.py` (`test_s316_rule_copies_reads_the_child_claude_md_from_the_kit_branch`).
## Story #319 review fixes: Dependabot, the local check and the template
```gherkin
Scenario: a Dependabot PR is not blocked by the tdd job
  Given the weekly Dependabot PR that changes only workflow files
  When the tdd job runs
  Then it prints "Dependabot: tdd exempt" and exits 0 before the check, like team-block
Scenario: a coder learns where the Red section goes before the first push
  Given check_local.sh, COMMIT_GUIDELINES.md and the PR template
  Then the usage line names tdd, the header and the guidelines say the Red section is in a commit body before a push, and the template has a Red section above Test Output
```
Tests: `tests/test_check_tdd.py` (`test_s319_dependabot_is_exempt_in_the_tdd_job_like_team_block`, `test_s319_check_local_usage_and_header_name_tdd`, `test_s319_commit_guidelines_say_a_code_branch_carries_a_red_line`, `test_s319_the_pr_template_has_a_red_section_above_test_output`).
## Story #312: the bench report (dry parts)
```gherkin
Scenario: the run says where it put the folder
  Given a finished bench --run
  When it ends
  Then its last line is "run folder: <the folder>"
Scenario: cell numbers come from the claude JSON and survive a rescore
  Given a fake claude that prints cost, output tokens and turns
  When the run finishes and then --rescore runs
  Then results.json holds those numbers and the lines of code of solution.py, before and after
Scenario: the report compares the arms task by task
  Given results for two tasks, two arms and three runs each
  When bench/report.py runs
  Then each task ratio is the kit median over the no-kit median, the table shows their geometric mean and a 95% bootstrap interval, and a metric nobody recorded shows n/a
Scenario: the decision is written down
  Then ADR-014 says a kit rule wording change must beat the current kit in a paired run, and experiments.md has a pending row for the bench
```
Tests: `tests/test_bench_report.py`, `tests/test_bench_runner.py` (`test_run_prints_the_run_folder_last`, `test_cell_metrics_come_from_the_claude_json_and_the_solution`).

## Story #327 review fixes: wrapped comments, string literals, the follow-ups file
```gherkin
Scenario: a wrapped comment is read whole
  Given a # or // comment whose upgrade trigger sits on the next comment line
  When the ledger scans it
  Then it is listed once, tagged ok, with the full text; a new marker on the next line is its own comment
Scenario: a marker in a string literal is not a comment
  Given a line with an odd number of quotes before the marker, or a closer followed by markup
  When the ledger scans it
  Then the string is not listed, and the text stops at the first closer
Scenario: --write is careful with docs/follow-ups.md
  Given no follow-ups file, a file with no header row, or a second table below the follow-ups table
  When --write runs
  Then it prints one line and writes nothing for the first two, and the new rows land right after the follow-ups table for the third
Scenario: the warn-only job cannot block a merge
  Then the shortcut-ledger job has continue-on-error: true and check_local.sh usage names shortcuts
```
Tests: `tests/test_check_shortcuts.py` (`test_s327_a_wrapped_comment_*`, `test_s327_a_new_marker_*`, `test_s327_a_marker_inside_a_string_*`, `test_s327_write_without_*`, `test_s327_rows_land_right_after_*`, `test_s327_a_follow_ups_file_without_the_header_row_*`, `test_s327_the_ci_job_cannot_block_a_merge_*`).
## Story #325 review fixes: three wrong answers of the workflow lint
```gherkin
Scenario: a later step with a head ref is not blamed on a clean checkout
  Given on has a schedule cron list or a list form, and a clean checkout, then a paths-filter step with a head ref
  When the lint runs
  Then it exits 0, and a real head checkout after a cron list still fails
Scenario: every install carries its own flag
  Given npm ci --ignore-scripts && npm install, or a cd chain with a second npm ci
  When the lint runs
  Then it exits 1 and names the line; installs that each carry the flag pass
Scenario: a folded block is one command
  Given run: > with npm ci on one line and --ignore-scripts on the next
  When the lint runs
  Then it exits 0, while a literal | block still checks each line
```
Tests: `tests/test_check_workflow_security.py` (`test_s325_a_later_step_with_a_head_ref_is_not_blamed_on_a_clean_checkout`, `test_s325_the_flag_must_sit_on_each_install_command`, `test_s325_a_folded_block_joins_its_lines_with_a_space`, `test_s325_check_local_usage_and_unknown_list_name_workflow_security`).
## Story #313 review fixes: the mode, the dense rules and the budget
```gherkin
Scenario: the hook reads the mode the way mode.sh does
  Given a repo whose mode is in .git/shipquick-mode, or in a tracked .shipquick/mode, or in a worktree of that repo
  When SessionStart runs from the repo, a subfolder or the worktree, or CLAUDE_PROJECT_DIR points at the repo
  Then the context says the same mode as mode.sh get; the tracked file wins; a word that is not a mode reads as not set
Scenario: the dense rules keep what each rule is for
  Then the dense text keeps "end your reply with one fenced block", "an agent never runs set", "The coder opens every PR" and "The author never reviews their own PR", and stays under 6000 characters
Scenario: the manifest and the budget are honest
  Then SessionStart also matches fork, plugin.json names an author, and ADR-015 states the in-process and whole-process times
```
Tests: `tests/test_plugin_hooks.py` (`test_the_mode_is_read_from_the_git_common_dir_like_mode_sh`, `test_a_tracked_mode_file_wins_over_the_common_dir_file`, `test_the_mode_is_found_from_a_subfolder_and_a_worktree`, `test_claude_project_dir_is_preferred_when_set`, `test_a_word_that_is_not_a_mode_reads_as_not_set`, `test_the_dense_rules_keep_the_instruction_each_rule_exists_for`, `test_the_dense_text_is_still_short_enough_to_inject_every_session`, `test_the_session_matcher_covers_fork_and_the_manifest_names_an_author`, `test_adr_015_states_the_time_budget_honestly`).

## Story #314 (A9): the codebase map at session start
```gherkin
Scenario: the map names the functions and classes of each folder
  Given a folder with Python, shell, TypeScript, Swift and Kotlin source
  When the map is built
  Then each folder line lists its top-level names, and names that start with an underscore are left out
Scenario: tests, vendored and hidden folders are skipped
  Given tests/, node_modules/, knowledge/ and a dot folder with source
  When the map is built
  Then none of their names appear
Scenario: scripts and plugin come first, and the budget holds
  Given many folders and scripts/ and plugin/ among them
  When the map is built
  Then scripts/ and plugin/ are the first lines, the text is at most 2000 characters and it says how many folders it left out
Scenario: shell functions without parentheses and Kotlin enum, annotation, value and inline classes are listed
  Then `function name {`, `enum class`, `annotation class`, `value class` and `inline class` names appear in the map
Scenario: the SessionStart hook appends the map, and a failed map never blocks
  When SessionStart runs in a project, the context holds the map after the rules
  When the project folder is missing, the hook still prints the rules and exits 0
```
Tests: `tests/test_codebase_map.py` (`test_names_come_from_each_language_and_private_ones_are_left_out`, `test_tests_vendored_and_hidden_folders_are_skipped`, `test_scripts_and_plugin_are_listed_first`, `test_the_map_stays_within_the_budget_and_says_what_it_left_out`, `test_the_map_of_this_repo_lists_scripts_within_budget`, `test_session_start_appends_the_map_to_the_rules`, `test_a_map_failure_never_blocks_the_session`, `test_a_folder_with_no_source_gives_an_empty_map`, `test_a_shell_function_without_parentheses_is_listed`, `test_kotlin_enum_annotation_value_and_inline_classes_are_listed`).
## Story #322, scratch markdown warning (A5c)
```gherkin
Scenario: a new scratch markdown file outside docs warns and names the single-source file
  Given a Write to TODO-plan.md at the project root
  When the PreToolUse hook runs
  Then it prints a warning that names docs/follow-ups.md
  And a Write to DRAFT-release.md names docs/plans/

Scenario: a file outside the pattern, or a pattern file inside docs, .claude or .github, is silent
  Given a Write to README.md, or to docs/NOTES-2026.md, or to a file in a docs/ subfolder that is a symlink into a vault
  When the PreToolUse hook runs
  Then it prints nothing and exits 0
  And bad stdin exits 0 and prints nothing

Scenario: a Write to a scratch file that already exists is silent (it is an edit, not a new file)
  Given TODO.md is already on disk at the project root
  When a Write targets TODO.md
  Then the PreToolUse hook prints nothing and exits 0
```
Tests: `tests/test_scratch_md.py` (`test_a_new_todo_file_outside_docs_warns_and_names_follow_ups`, `test_a_draft_file_names_docs_plans`, `test_a_file_outside_the_pattern_is_silent`, `test_a_pattern_file_inside_docs_is_silent`, `test_a_pattern_file_inside_a_symlinked_docs_folder_is_silent`, `test_a_pattern_file_inside_claude_or_github_is_silent`, `test_bad_stdin_exits_zero_and_prints_nothing`, `test_a_write_to_an_existing_todo_file_is_silent`, `test_the_hook_is_registered_for_write_before_use`). Local: `python3 -m pytest -q tests/test_scratch_md.py`.
## Story #321 (A5b): the protected path warning
```gherkin
Scenario: editing a protected path in auto mode warns the coder
  Given a repo in auto mode whose scripts/protected_paths.txt lists scripts/review_merge.sh
  When an Edit or Write targets scripts/review_merge.sh, or a file under .github/workflows/
  Then the hook prints "protected path, owner merges: <path>" and exits 0
Scenario: an unlisted path prints nothing
  When an Edit targets src/app.py
  Then the hook prints nothing and exits 0
Scenario: manual mode and files outside the repo print nothing
  Given the same listed path in manual mode, or a file outside the repo
  Then the hook prints nothing and exits 0
Scenario: the hook never blocks
  Given input that is not JSON
  Then the hook exits 0 with no output
```
Tests: `tests/test_protected_warn.py` (`test_editing_a_listed_path_in_auto_mode_prints_the_warning`, `test_a_glob_line_matches_a_nested_path`, `test_an_unlisted_path_prints_nothing`, `test_a_listed_path_in_manual_mode_prints_nothing`, `test_a_file_outside_the_repo_prints_nothing`, `test_bad_stdin_exits_zero_and_never_blocks`, `test_the_hook_is_registered_on_pretooluse_edit_and_write`).

## Story #321 review fixes (PR #350): the warning reaches a child and the model
```gherkin
Scenario: a child project with the vendored list gets the warning
  Given a child repo in auto mode whose knowledge/shipquick_latest/scripts/protected_paths.txt lists .github/workflows/*
  When an Edit targets .github/workflows/ci.yml
  Then the hook prints "protected path, owner merges: .github/workflows/ci.yml" and exits 0
Scenario: the warning is given as additional context to the model
  Given a listed path in auto mode
  Then the hook output has hookSpecificOutput.additionalContext with the warning, hookEventName PreToolUse, and no permissionDecision
```
Tests: `tests/test_protected_warn.py` (`test_a_child_with_the_vendored_list_gets_the_warning`, `test_the_warning_reaches_the_model_as_additional_context`).

## Story #321 review fix 3 (PR #350): an edit in a git worktree
```gherkin
Scenario: an edit in a worktree is judged by the edited file's own checkout
  Given a repo in auto mode with a worktree under .claude/worktrees/lane-x, and CLAUDE_PROJECT_DIR set to the main checkout
  When an Edit targets <worktree>/scripts/review_merge.sh
  Then the hook prints "protected path, owner merges: scripts/review_merge.sh" and exits 0
```
Tests: `tests/test_protected_warn.py` (`test_an_edit_in_a_worktree_warns_when_the_session_points_at_the_main_checkout`).
## Story #320 (A5a): the Bash hook blocks git hook bypasses
```gherkin
Scenario: a git commit or push that skips the hooks is blocked
  Given a Bash tool call with "git commit --no-verify", "git push --no-verify" or "git -c core.hooksPath=... commit"
  When the PreToolUse hook runs
  Then it exits 2 and the reason starts with "git_guard: blocked" on stderr
Scenario: a git config that redirects the hooks folder is blocked
  Given a Bash tool call with "git config core.hooksPath .husky"
  When the PreToolUse hook runs
  Then it exits 2; a read such as "git config --get core.hooksPath" passes
Scenario: a harmless command passes silently
  Given "git status", "git push -n origin dev" or "ls -la"
  When the PreToolUse hook runs
  Then it exits 0 and prints nothing
Scenario: the bypass text inside a quoted argument of another command passes
  Given "echo \"git commit --no-verify\"" or "gh pr create --body \"core.hooksPath is not allowed\""
  When the PreToolUse hook runs
  Then it exits 0; a real bypass after "&&" in the same line is still blocked
Scenario: a bypass hidden by a line continuation, an env var, or a long-option prefix is blocked
  Given "git commit -m fix \\" then a new line "--no-verify", "GIT_CONFIG_PARAMETERS=... git commit", "git --config-env=core.hooksPath=X commit", "git commit --no-veri" or "git push --no-veri"
  When the PreToolUse hook runs
  Then it exits 2 with the reason on stderr
```
Tests: `tests/test_git_guard.py` (`test_bypass_is_blocked_with_reason` (eight cases added for the review round: continuation, env vars, --config-env, --no-veri), `test_harmless_command_passes_silently`, `test_bypass_text_inside_a_quoted_argument_passes`, `test_other_tools_and_broken_input_pass`, `test_hook_is_registered_for_bash_pre_tool_use`).
## Story #315: the loop and cost guard
```gherkin
Scenario: four different calls are not a loop
  Given four Edit calls with four different inputs in one session
  When the PostToolUse guard runs after each
  Then nothing is printed
Scenario: five identical calls warn loop, and a sixth is denied before it runs
  Given five identical Edit calls recorded in one session
  When the PostToolUse guard runs on the fifth, and the PreToolUse guard runs on a sixth identical call
  Then the fifth prints "loop: the same call 5 times" and the sixth gets a deny with the same text
Scenario: a different call breaks the streak
  Given five identical calls, then a call with another input
  When the PreToolUse guard runs on the other call
  Then nothing is printed, so the call is allowed
Scenario: the same input on another tool is not a loop
  Given calls alternating Edit and Write, then a Bash call with the same input
  When the PostToolUse guard runs on the Bash call
  Then no loop warning is printed
Scenario: under the warn line prints nothing
  Given a transcript whose usage costs 0.50 dollars
  When the PostToolUse guard runs
  Then nothing is printed
Scenario: over the warn line warns about cost
  Given a transcript whose usage costs 6 dollars and the block line is set to 100
  When the PostToolUse guard runs
  Then the warning says "cost:" and "warn line", and no deny is given
Scenario: over the block line denies Edit, Write and Bash before they run
  Given a transcript whose usage costs 6 dollars
  When the PreToolUse guard runs on an Edit call
  Then the deny reason says "cost:" and "block line"
Scenario: the block line comes from the environment
  Given SHIPQUICK_COST_BLOCK is 2.5 and a transcript that costs 3 dollars
  When the PreToolUse guard runs
  Then the call is denied with "block line"
Scenario: cost is priced per model and per token class
  Given one Haiku output million tokens and one Sonnet cache-read million tokens
  Then session_cost is the Haiku output price plus the Sonnet cache-read price
Scenario: a missing transcript costs nothing and never blocks
  Given a transcript path that does not exist
  When the PreToolUse guard runs
  Then nothing is printed
Scenario: a bad threshold falls back to the default
  Given SHIPQUICK_COST_WARN is "two dollars" and a transcript that costs 3 dollars
  When the PostToolUse guard runs
  Then the warning names the warn line at the default 2 dollars
Scenario: the hooks file registers the guard
  Then PostToolUse runs guard.py post for every tool, and PreToolUse runs guard.py pre for Edit, Write and Bash
```
Tests: `tests/test_guard_hook.py` (`test_five_identical_calls_warn_loop`, `test_a_sixth_identical_call_is_denied_before_it_runs`, `test_over_the_block_line_denies_edit_before_it_runs`, `test_cost_is_priced_per_model_and_per_token_class`, and the other tests in that file).

## Story #315, PR #347 review fixes: offset read and opus price
```gherkin
Scenario: a grown transcript is read only from the saved offset
  Given a transcript that cost 3 dollars on the first call, then grows by one 3 dollar record, and its first bytes change in place
  When the PostToolUse guard runs on the second call
  Then the warning says "$6.00", so the old bytes are not counted again
  Test: test_a_grown_transcript_is_read_from_the_saved_offset
Scenario: an opus output million costs the opus output rate
  Given a transcript with one claude-opus-4-1 record of 1,000,000 output tokens
  When the cost is read
  Then the cost is 75 dollars, and rate_for picks the opus row
  Test: test_opus_is_priced_at_opus_list_not_sonnet
```

## Story #315, PR #347 review fixes (round 2): loop deny for Edit and Write only, cost warning once per dollar
```gherkin
Scenario: six identical Bash calls are not denied by the loop
  Given five identical Bash calls recorded in one session
  When the PreToolUse guard runs on a sixth identical Bash call
  Then nothing is printed, so the poll is allowed (post already warned on the fifth)
  Test: test_six_identical_bash_calls_are_not_denied_by_the_loop
Scenario: six identical Write calls are still denied by the loop
  Given five identical Write calls recorded in one session
  When the PreToolUse guard runs on a sixth identical Write call
  Then the deny reason says "loop: the same call 5 times"
  Test: test_six_identical_write_calls_are_still_denied_by_the_loop
Scenario: a cost warning is printed once per dollar
  Given a transcript that costs 3 dollars, and two PostToolUse calls in one session
  When the guard runs on the first call, then on the second
  Then the first prints the warn line, and the second prints nothing
  Test: test_a_cost_warning_is_printed_once_per_dollar
```

## Story #357: the child's milestone is a caller input
```gherkin
Scenario: the environments job reads the milestone from the caller
  Then checks.yml has a milestone input with default D1, passes it to check_environments.sh through env MILESTONE (never inline in run:), and its description says D0 exempts
Scenario: adopt.sh writes, keeps and validates the milestone
  When adopt.sh runs with --milestone D2, the caller has `milestone: D2`; a later run without the flag keeps it, once; a run with no flag and no line writes none; --milestone X9 is refused and the caller is untouched; an existing line that is quoted, lowercase, D7 or has a trailing comment is refused, not dropped
```
Tests: `tests/test_check_environments.py::test_s357_checks_yml_environments_job_reads_the_milestone_input`, `tests/test_adopt.py::test_s357_milestone_is_written_once_kept_over_two_runs_and_a_bad_flag_is_refused`, `test_s357_a_run_without_the_flag_and_without_a_line_writes_no_milestone`, `test_s357_an_existing_milestone_line_that_does_not_match_is_refused_not_dropped`.

## Story #188 (S10): a Design system board on the canvas
```gherkin
Scenario: the registry renders a board with every component row, right after Design learnings
  Given a manifest in columns layout with a learnings section and a "registry" path to a fixture registry of three rows (two platforms)
  When the layout runs
  Then project/design-system.dc.html holds an Android and an iOS column, every component name on its base, its status (given, "twin #n" or "no twin yet") and its doc link (given or the kit's default), painted in the manifest's ink
  And the board sits in the learnings section, in the same row as the learnings board, fully to its right, with the LEARNINGS prefix
  Test: test_S34_the_registry_renders_a_board_with_every_component_row_under_its_platform_right_after_learnings
Scenario: a missing registry or an unknown platform is a problem, and no registry key means no board
  Given the manifest names a registry file that does not exist, or one whose row has platform "web"
  Then the run reports a problem naming the file or the row
  And without the "registry" key no design-system board is made
  Test: test_S35_a_missing_registry_or_an_unknown_platform_is_a_problem_and_no_registry_key_means_no_board
Scenario: --check fails naming a stale design-system board until --apply regenerates it
  Given --apply has written the board and --check passes
  When the registry loses a row and --check runs
  Then it exits 1 and prints "STALE project/design-system.dc.html"; after --apply, --check passes again
  Test: test_S36_check_fails_naming_a_stale_design_system_board_until_apply_regenerates_it
Scenario: a registry in a rows layout with no learnings section is a problem, not silence (review of #368)
  Given a manifest with "registry" set, the default rows layout and no section with id "learnings"
  When the layout runs
  Then the run reports a problem naming "registry" and "learnings", and no design-system board is made
  Test: test_S37_a_registry_in_a_rows_layout_with_no_learnings_section_is_a_problem_not_silence
Scenario: a registry that is JSON but not a components object is a problem, not a traceback (review of #368)
  Given the registry file holds [], or {"components": ["Stepper"]}, or {"components": "x"}
  When the layout runs
  Then no exception is raised and the run reports a problem naming the path and "components"
  Test: test_S38_a_registry_that_is_json_but_not_a_components_object_is_a_problem_not_a_traceback
```
Tests: `tests/test_canvas_stage.py::DesignSystem`.


## Story #174: a workflow file with zero jobs is named and failed

**S174.1 Zero jobs is named and failed.**
```gherkin
Scenario: a workflow file in another indent style with no jobs is named and failed
  Given a workflow file whose "jobs:" key is indented, so no job can be read
  When check_timeouts.py checks that file
  Then the output has a line "no timeout-minutes: <file>: no jobs found"
  And the exit code is 1, never "timeouts OK"
```
Test: `tests/test_check_timeouts.py::test_s174_a_file_with_zero_jobs_is_named_and_failed`


## Story #218: the two-tier iOS lint runner with a baseline
```gherkin
Scenario: the CI tier is strict and reads the baseline
  Given a child with ui/tool/ios_lint.sh and CI=1 (or CI=true, as GitHub sets it)
  When the runner lints a Swift file
  Then swiftlint runs with --strict, --config ui/ios/lint/swiftlint.yml and --baseline ui/ios/lint/swiftlint-baseline.json
  And swiftformat runs with --lint and ui/ios/.swiftformat, so a format change fails the job
Scenario: the local tier only warns
  Given no CI variable
  When the runner lints a Swift file
  Then swiftlint runs without --strict, still with the baseline, and swiftformat gets --lenient, and the exit code is 0
Scenario: only the changed Swift files are linted
  Given a repo where one committed Swift file changed, one Swift file is new and untracked, and a markdown file changed
  When the runner runs with no file argument and LINT_BASE=HEAD
  Then exactly the two Swift files reach swiftlint and swiftformat
  And with nothing changed the runner prints "no Swift file changed" and runs no tool
Scenario: a missing swiftlint fails CI and only warns locally
  When swiftlint is not on PATH
  Then the CI tier exits non-zero and the local tier exits 0, both saying "swiftlint is not installed"
Scenario: a missing swiftformat alone fails CI and only warns locally (#366 review)
  When swiftlint is on PATH but swiftformat is not
  Then the CI tier exits non-zero and the local tier exits 0, both saying "swiftformat is not installed"
Scenario: a missing base ref fails CI and only warns locally (#366 review)
  Given a repo with no origin/dev (a shallow checkout) and a committed Swift change
  When the runner runs with no file argument
  Then the CI tier exits non-zero naming fetch-depth and LINT_BASE, and the local tier exits 0 with the same warning
Scenario: an adopted child gets configs that exist (PR #366 review)
  Given a child repo with only ui/platforms/lint/swiftlint.yml (what adopt.sh --platforms ios writes), no baseline, no .swiftformat
  When the runner runs by its kit path in the CI tier
  Then swiftlint gets --config ui/platforms/lint/swiftlint.yml, and every --config and --baseline path given to the tools exists (the kit's own files fill the gaps)
Scenario: the baseline is committed empty and protected
  Then ui/ios/lint/swiftlint-baseline.json is the JSON array [] and matches a glob in scripts/protected_paths.txt (*baseline*)
Scenario: the Tokens file is the one place for raw colours and fixed fonts
  Given tests/fixtures/ios/Good/Tokens.swift holds Color(red:, UIColor(red:, Font.system(size: and Font.custom(
  Then the rule regexes match it, the token rules carry an excluded pattern that matches its path, and no other rule fires on it
  And CI job ui-ios-lint passes the whole Good folder in strict mode with real SwiftLint
Scenario: named snippets break their rule, good snippets break none
  Then Color(red:, UIColor(red:, .font(.system(size:, Font.custom(, import SnapKit and import UIKit each match their rule id
  And Color.red, Color("Brand"), .font(.body), Tokens.font, import SwiftUI, import Foundation and @testable import ShipQuickUI match no rule
Scenario: CI runs both tiers through the runner
  Then job ui-ios-lint fetches SwiftFormat 0.64.6 by SHA-256 like SwiftLint, runs `CI=1 bash ui/tool/ios_lint.sh` on Good and Bad, `CI= bash ui/tool/ios_lint.sh` on Bad, and the bad run names every rule id
```
Tests: `tests/test_ios_lint_tool.py` (s218). CI job: `ui-ios-lint` (macos-15).


## Story #223: the Android Button topic follows M3 exactly
```gherkin
Scenario: the Android Button topic shows only M3 parameters and the five M3 buttons
  Given the Button doc and contract in ui/components/Button
  When the android topic is built
  Then every prop row is a Compose Material 3 Button parameter (tests/fixtures/m3_button.json, from Google's page), onClick, enabled and content are among them, and Button, FilledTonalButton, ElevatedButton, OutlinedButton and TextButton are named, and no web variant word (primary, secondary, ghost, destructive) appears anywhere in the topic text (PR #367 review: the web Do line moved to platformUsage.web, Android got its own M3 line)
  Test: test_s223_the_android_button_topic_shows_only_m3_parameters_and_the_five_m3_buttons
Scenario: a web prop in core is caught as not M3
  Given a contract with `variant` in core
  When the android topic is built
  Then the M3 check names `variant`
  Test: test_s223_a_web_prop_in_core_is_caught_as_not_m3
Scenario: the web props stay in the web doc as webOnly
  Then the Button doc still lists label, variant, size, isDisabled and isLoading, and the contract has each under webOnly with a reason
  Test: test_s223_the_web_props_stay_in_the_web_doc_as_web_only
```
Tests: `tests/test_ui_topics.py::test_s223_the_android_button_topic_shows_only_m3_parameters_and_the_five_m3_buttons`, `test_s223_a_web_prop_in_core_is_caught_as_not_m3`, `test_s223_the_web_props_stay_in_the_web_doc_as_web_only`; `tests/test_ui_cli.py::test_s183_topics_are_generated_from_the_s2_docs_and_are_current` now asserts the web variant enum is absent from the Android topic.


## Story #175: the story check reaches children
```gherkin
Scenario: the story job exists in checks.yml and the gate needs it
  Then checks.yml has a `story` job that runs only on a pull request, asks for issues: read, runs check_story.py --pr-body-file with GH_TOKEN and the child's own GH_REPO, and the gate lists it and echoes its result
Scenario: the caller adopt.sh writes grants issues: read
  When adopt.sh runs on a fresh child, the written shipquick-call.yml has an `issues: read` line
Scenario: --check reports a caller without issues: read
  Given a correctly pinned child whose caller lost every `issues: read` line
  When adopt.sh --check runs
  Then it exits 1 and says "not adopted: shipquick-call.yml grants no issues: read"
Scenario: --check accepts a caller that grants issues: write (review of #370)
  Given a correctly pinned child whose caller says `issues: write` instead of `issues: read`
  When adopt.sh --check runs
  Then it exits 0 and says nothing about issues: read, since write lets the story job read issues
Scenario: --check accepts a caller with `permissions: read-all` (review of #370, round 2)
  Given a correctly pinned child whose caller's permissions block is the one line `permissions: read-all`
  When adopt.sh --check runs
  Then it exits 0 and says nothing about issues: read, since read-all grants issues: read too
Scenario: --check accepts an `issues: read` line with a trailing comment (review of #370, round 2)
  Given a correctly pinned child whose caller says `issues: read   # the story job reads the linked stories`
  When adopt.sh --check runs
  Then it exits 0 and says nothing about issues: read
```
Tests: `tests/test_checks_workflow.py::test_s175_checks_yml_has_a_story_job_that_runs_check_story_with_issues_read`, `test_s175_the_gate_needs_the_story_job_and_echoes_its_result`, `tests/test_adopt.py::test_s175_the_written_caller_grants_issues_read`, `test_s175_check_reports_a_caller_without_issues_read`, `test_s175_check_accepts_a_caller_that_grants_issues_write`, `test_s175_check_accepts_a_caller_with_permissions_read_all`, `test_s175_check_accepts_an_issues_read_line_with_a_trailing_comment`.


## Story #189 (S11): vibe tests, ten fixed screen prompts per platform
```gherkin
Scenario: the selftest scores the fixtures with zero model calls
  Given a fake claude on PATH that logs every call
  When `bench/vibe.py --selftest` runs
  Then it prints "selftest 3/3 platforms pass", exits 0, and the log is absent
  Test: test_selftest_scores_the_fixtures_and_makes_no_claude_call
Scenario: the good fixture is clean and the bad fixture is raw on every platform
  Then score_dir gives clean=1 for android, ios and web good fixtures and clean=0 with hits for the bad ones
  Test: test_good_fixture_is_clean_and_bad_fixture_is_raw_on_every_platform
Scenario: a cell that wrote no screen file scores zero
  Test: test_a_cell_with_no_screen_file_scores_zero
Scenario: the prompts are the same ten generic screens on three platforms
  Then each platform has exactly ten prompts with the fixed screen ids, and the task text is identical across platforms
  Test: test_prompts_are_the_same_ten_generic_screens_on_three_platforms
Scenario: the smoke runs exactly four calls and only the kit arm gets the agent block
  Given a fake claude that copies good fixture screens into its work folder
  When `--run --smoke` runs
  Then 4 calls are made on claude-haiku-5-5 with Bash disallowed, 2 carry --append-system-prompt with SELF-CHECK, and results.json scores kit 2/2 and no-kit 2/2
  Test: test_smoke_runs_exactly_four_calls_and_only_the_kit_arm_gets_the_agent_block
Scenario: a run folder inside a work tree is refused before any call
  Test: test_run_folder_inside_a_git_tree_is_refused_before_any_call
Scenario: a full run needs --full, so a typo never burns sixty calls
  Test: test_a_full_run_needs_the_full_flag_so_a_typo_never_burns_sixty_calls
Scenario: a web screen with JSX but no library import is raw (PR #371 review)
  Given a Screen.tsx that renders a plain div and imports nothing from @astryxdesign/core
  Then score_dir hits exactly no_library_import, and the bad fixture PlainScreen.tsx carries the same case for --selftest
  Test: test_a_web_screen_with_jsx_but_no_library_import_is_raw
Scenario: a web screen that imports a library subpath is clean (PR #371 review, round 2)
  Given a Screen.tsx that imports Button from "@astryxdesign/core/Button", the form the component docs teach
  Then it scores clean, while PlainScreen.tsx with no library import still hits no_library_import
  Test: test_a_web_screen_that_imports_a_library_subpath_is_clean
Scenario: an issue number after a colon in a web comment is not a hex colour (PR #371 review)
  Given the good web screen with a first line "// Story: #189 sign in"
  Then it scores clean, while a CSS file with "color: #fff;" still hits no_hex_colour
  Test: test_an_issue_number_after_a_colon_in_a_web_comment_is_not_a_hex_colour
```
Tests: `tests/test_vibe.py`.


## Story #296 (1/6): the InputModifiers catch-all holds only rows no control doc fits
```gherkin
Scenario: a catch-all row whose control has its own doc fails
  Given the catch-all docs split so far and, per catch-all, the row-name stems a control or task doc owns (gesture, focus, keypress, drag, drop, hover, widget, ...)
  When a row of a catch-all doc holds one of its stems
  Then the test fails naming the catch-all, the row and the doc that owns it
  Test: test_s296_a_catch_all_row_whose_control_has_its_own_doc_fails
Scenario: each owner doc exists, sets a family and holds a row of its stem
  Given every stem of the fixture
  Then its owner doc folder exists, the gate can count it (platforms.ios or platformApi.ios.family) and it holds a row with that stem
  Test: test_s296_each_owner_doc_exists_sets_a_family_and_holds_a_row_of_its_stem
```
Tests: `tests/test_ui_catch_all.py::test_s296_a_catch_all_row_whose_control_has_its_own_doc_fails`, `test_s296_each_owner_doc_exists_sets_a_family_and_holds_a_row_of_its_stem`.


## Story #92: CI runs again when a PR body is edited
```gherkin
Scenario: the ShipQuick CI trigger re-runs on a body edit
  Given the ci.yml pull_request trigger
  Then its types list carries edited, with opened, synchronize and reopened
Scenario: an adopted child caller re-runs on a body edit too
  When adopt.sh writes shipquick-call.yml for a child
  Then the pull_request trigger in the caller lists the same four types
```
Tests: `tests/test_s92_ci_on_body_edit.py::test_s92_ci_pull_request_trigger_lists_edited`, `tests/test_s92_ci_on_body_edit.py::test_s92_the_adopted_checks_caller_also_runs_on_body_edit`.

## Story #133 (S5w): design literals on added web lines
```gherkin
Scenario: a colour or font literal on an added web style line fails with the file and the line
  Given a diff that adds `color: #ff0033;` to a css file, `rgb(...)`/`rgba(...)` to a tsx inline style, `hsl(...)` to a vue, svelte or astro file, `font-family: 'Inter'` to css, `fontFamily: "Inter"` to tsx, or `bg-[#1e293b]` / `font-['Inter']` Tailwind classes
  When check_design_literals.py reads the diff
  Then it exits 1 and names `path:line` and the literal kind for every hit
  Test: test_a_hex_colour_in_added_css_fails_with_file_and_line, test_rgb_and_rgba_in_added_tsx_inline_style_fail, test_hsl_in_added_vue_svelte_and_astro_fails, test_a_font_family_literal_fails_in_css_and_in_tsx, test_a_tailwind_arbitrary_colour_or_font_fails
Scenario: token references, keywords and a token file in the allowlist pass
  Given `var(--color-primary)`, `font-family: inherit`, `theme.fonts.body` and a Tailwind token class, or a hex in a file that matches a glob in scripts/design_token_files.txt
  Then the check prints "no design literals on added lines" and exits 0
  Test: test_token_references_and_keywords_pass, test_a_token_file_in_the_allowlist_passes, test_the_allowlist_file_reads_globs_and_skips_comments_and_blanks
Scenario: only added lines of the named file types count, with the hunk's line numbers
  Given a removed line, a python, markdown or js file, a private field `this.#cafe`, an entity `&#dead;`, an id selector `#main-nav`, and two hunks
  Then none is a hit, and a hit in the second hunk carries that hunk's line number
  Test: test_a_removed_line_and_a_non_web_file_are_never_a_hit, test_a_private_field_an_html_entity_and_an_id_selector_with_letters_are_not_hex, test_line_numbers_follow_the_hunk_header_across_hunks
Scenario: a story reference in a comment is not a hex colour (PR #374 review)
  Given `// story #133` on a ts line, `/* story #374 */` on a css line, or a `#cafe = 1` class field
  Then none is a hit; a literal outside the comment still fails, and `//` inside a `url(https://...)` is not a comment
  Test: test_a_story_reference_in_a_comment_is_not_a_hex_colour
Scenario: the check is wired and the allowlist is protected
  Then scripts/design_token_files.txt is in scripts/protected_paths.txt, check_local.sh names design-tokens, ci.yml and checks.yml carry a design-tokens job (the script, then stylelint with `--report-needless-disables` only when css changed) and both gates wait for it; the CLI reads a diff file and exits 1 with the hits
  Test: test_the_kit_allowlist_is_protected_and_check_local_names_the_check, test_a_design_tokens_job_sits_in_ci_and_checks_and_both_gates_wait_for_it, test_the_cli_reads_a_diff_file_and_exits_1_with_the_hits
Scenario: stylelint runs with the project's own dependencies (PR #374 review)
  Given a child whose .stylelintrc.json extends `stylelint-config-standard`, or a `"stylelint"` key in package.json
  When the design-tokens job (ci.yml, checks.yml) or check_local.sh design-tokens runs stylelint
  Then it runs `npm ci --ignore-scripts` first when package-lock.json exists, uses `node_modules/.bin/stylelint` when present, and `npx --yes stylelint@16.26.1` only as the fallback
  Test: test_stylelint_installs_the_child_dependencies_and_prefers_the_local_binary
Scenario: a protocol-relative url in css does not hide a hex (PR #374 review round 2)
  Given `background: url(//cdn.example/a.png) #ff0000;` or the quoted `url('//...')` form on an added css line
  Then it is a hex hit: `//` is never a comment in css, only `/* */` is cut there; a ts line still loses its `//` comment
  Test: test_a_protocol_relative_url_in_css_does_not_hide_a_hex
Scenario: the font shorthand is a font-family literal (PR #374 review round 2)
  Given `font: 16px/1.5 'Inter', sans-serif;` or `font: 1rem Inter;` on a css line, or `style={{ font: '16px Inter' }}` on a tsx line
  Then each is a font-family hit; `font: 1rem var(--font-body)`, `font: inherit`, `font-size`/`font-weight` and the tsx `font: theme.fonts.body` pass
  Test: test_the_font_shorthand_is_a_font_family_literal
Scenario: stylelint runs once, per package root, and installs only when the binary is missing (PR #374 review round 2)
  Given a child whose web app sits in `web/` (web/package.json, web/.stylelintrc.json, a lockfile, Android beside it) and a changed `web/a.css`
  When ci.yml, checks.yml or check_local.sh design-tokens calls `scripts/run_stylelint_changed.sh <base> [repo]`
  Then it never prints `skip stylelint` for that file: it runs web's own `node_modules/.bin/stylelint` from `web/` on `a.css`, runs `npm ci` only when that binary is missing, names a folder with css but no config in its skip line, and the script is a protected path
  Test: test_stylelint_runs_from_the_package_root_of_a_web_subfolder, test_stylelint_installs_the_child_dependencies_and_prefers_the_local_binary, test_a_design_tokens_job_sits_in_ci_and_checks_and_both_gates_wait_for_it
Scenario: a style block or a url() string does not hide a literal (PR #374 review round 3)
  Given `.hero { background: url(//cdn.example/a.png) #ff0000; }` or `.t { font: 16px/1.5 'Inter', sans-serif; }` on a .vue, .svelte or .astro line, or `background: 'url(//cdn.example/a.png) #ff0000'` on a tsx line
  Then each is a hit: `//` starts a comment only at the line start or after a space; `const x = 1; // story #133`, `font: string;` and `font: 1rem var(--font-body), sans-serif;` pass
  Test: test_style_blocks_in_vue_svelte_astro_and_tsx_urls_do_not_hide_a_literal
Scenario: an rgb or hsl call on a token is not a literal (PR #374 review round 3)
  Given `color: rgb(var(--md-primary-rgb) / 0.12);` on a css line
  Then it passes, and `color: rgb(255, 0, 0);` is still an rgb/hsl hit
  Test: test_an_rgb_or_hsl_call_on_a_token_is_not_a_literal
Scenario: a non-ASCII file name does not hide a literal (PR #374 review round 4)
  Given a commit that adds `a { color: #ff0033; }` to `src/café.css`, so git writes a quoted header `+++ "b/src/caf\303\251.css"`
  When the check runs with --base, or reads a saved diff with that quoted header
  Then it reports `src/café.css:1`: git runs with `core.quotePath=false`, and a quoted header is unquoted before the `b/` strip
  Test: test_a_quoted_non_ascii_path_header_is_still_checked, test_the_cli_reports_a_hex_in_a_non_ascii_file_name_from_git
```
Tests: `tests/test_check_design_literals.py`.


## Story #219: snapshots and Prefire for ui/ios
```gherkin
Scenario: the package has a test target with the two snapshot packages pinned exactly
  Then ui/ios/Package.swift names swift-snapshot-testing and Prefire with `exact:` versions, a test target ShipQuickUITests with SnapshotTesting and PrefireTestsPlugin, all behind the SHIPQUICK_SNAPSHOTS guard, and the library a child resolves has no `.package(`; ui/ios/.prefire.yml names the target
  Test: test_s219_the_package_has_a_test_target_with_snapshot_testing_and_prefire_pinned_exactly
Scenario: one snapshot test per template over the whole matrix
  Then TemplateSnapshotTests.swift has a test<Name>() per template and names light, dark, extraSmall, accessibilityExtraExtraExtraLarge, iPhoneSe and ProMax, and says how record mode is switched on
  Test: test_s219_one_snapshot_test_per_template_over_the_whole_matrix
Scenario: every template has a #Preview for Prefire
  Test: test_s219_every_template_has_a_preview_for_prefire
Scenario: CI runs the snapshot tests on a pinned Xcode and simulator with a timeout
  Then ci.yml has a job ui-ios-snapshots behind ui-changes on macos-15 with timeout-minutes, Xcode 16.4, `xcodebuild test` on iPhone 16 iOS 18.5, the record env var, an upload-artifact step for __Snapshots__, a workflow_dispatch `record` input, and the gate waits for it
  Test: test_s219_ci_runs_the_snapshot_tests_on_a_pinned_xcode_and_simulator_with_a_timeout
Scenario: the reference images are a protected path
  Test: test_s219_the_reference_images_are_a_protected_path
Scenario: the doc tells how references are recorded and refreshed
  Then ui/ios/SNAPSHOTS.md names record, workflow_dispatch, gh run download, __Snapshots__, protected, Xcode 16.4 and iOS 18.5, and the README points to it
  Test: test_s219_the_doc_tells_how_references_are_recorded_and_refreshed
Scenario: the reference folder holds one PNG per template and matrix cell (#375 review)
  Then ui/ios/ShipQuickUITests/__Snapshots__/TemplateSnapshotTests/ holds exactly test<Template>.<light|dark>-<xs|ax5>-<se|promax>.png for every template, 40 in all
  Test: test_s219_the_reference_folder_holds_one_png_per_template_and_matrix_cell
Scenario: CI names the scheme and never parses xcodebuild output (#375 review)
  Then the job runs `xcodebuild test -scheme ShipQuickUI` and has no json.load
  Test: test_s219_ci_runs_the_snapshot_tests_on_a_pinned_xcode_and_simulator_with_a_timeout
Scenario: recorded reference images do not count toward pr-size (#375 review)
  Given 10 text files and 45 PNGs under ui/ios/ShipQuickUITests/__Snapshots__/, pr-size counts 10 and passes
  Given 50 PNGs outside __Snapshots__ and one .txt inside it, pr-size counts 51 and fails
  Given 51 PNGs under docs/__Snapshots__/ (not the protected folder), pr-size counts 51 and fails (round 4)
  Then both ci.yml pr-size awk lines anchor the exclusion to ^ui/ios/ShipQuickUITests/__Snapshots__/.*\.png$
  Tests: test_s219_reference_images_under_snapshots_do_not_count_toward_pr_size, test_s219_a_png_outside_snapshots_and_a_non_png_inside_still_count, test_s219_pngs_in_a_snapshots_folder_outside_the_protected_path_still_count, test_s219_cis_pr_size_job_leaves_out_the_same_reference_images (tests/test_ci_must_have.py)
Scenario: the snapshot job runs only when iOS paths change (#375 review, round 2)
  Given ui-changes has an `ios` output written by a grep over the changed names
  Then that grep matches ui/ios/** and design/** and does not match ui/android/** or tests/fixtures/**
  And the job ui-ios-snapshots waits on needs.ui-changes.outputs.ios, not on `ui`
  And it runs unless ios is 'false', so a fail-safe exit that writes only ui=true still runs it (round 3)
  And the story #217 fail-safe lines stay as they were
  Test: test_s219_the_snapshot_job_runs_only_when_ios_paths_change
Scenario: the doc states the real precision of the compare (#375 review, round 2)
  Then ui/ios/SNAPSHOTS.md names `perceptualPrecision <n>` with the same n as TemplateSnapshotTests.swift, points to that file, and never says "changed pixel"
  Test: test_s219_the_doc_states_the_real_precision_of_the_compare
```
Tests: `tests/test_ios_snapshots.py`, `tests/test_ci_must_have.py` (the four pr-size ones). The Swift tests themselves (`ui/ios/ShipQuickUITests/TemplateSnapshotTests.swift`, 5 tests, 40 images, plus Prefire's generated preview tests) run only in the CI job `ui-ios-snapshots`.


## Story #222: generated Swift contract structs for ui/components
```gherkin
Scenario: every prop kind maps to a Swift type
  Given a made-up contract with string, number, boolean, enum, fn, content, array and named props, one web-only prop and one sameMeaning
  When the generator renders it
  Then the file holds `<Name>Props` with typed fields, a nested String enum, `(() -> Void)?` for an optional callback, `@escaping` on a required one, a backticked `in`, the generic placeholder replaced and named in a comment, the content slot and the web-only prop in comments, and no Android prop
  Test: test_s222_every_prop_kind_maps_to_a_swift_type
Scenario: the folder names the struct when two contracts share an inner name
  Given two component folders whose contracts both carry the same inner `name`
  When the generator renders them
  Then each struct and its nested enums take the folder's name, and the inner name sits in a comment
  Test: test_s222_the_folder_names_the_struct_when_two_contracts_share_an_inner_name
Scenario: a record becomes a nested struct and an unknown kind fails by name
  Test: test_s222_a_record_type_becomes_a_nested_struct_and_an_unknown_kind_fails_by_name
Scenario: a renamed contract field fails --check and names the struct file
  Given the kit's contracts and structs copied to a temp folder, and `label` renamed to `title` in one contract
  When `--check` runs
  Then it exits 1 and prints that struct file; after a regenerate the new field is there and `--check` exits 0
  Test: test_s222_a_renamed_contract_field_fails_check_and_names_the_struct_file
Scenario: a removed contract leaves a stale struct that --check names and a regenerate removes
  Test: test_s222_a_removed_contract_leaves_a_stale_struct_that_check_names
Scenario: every committed struct is a fresh render of its contract (stack layer 2, the first 48 files)
  Given the committed Contracts folder
  Then it is not empty, no file is stale and no file has lost its contract
  Test: test_s222_every_committed_struct_is_current_with_its_contract
Scenario: the committed structs are current and every contract has one (stack layer 3, the other 48 files)
  Tests: test_s222_the_committed_structs_are_current_with_the_contracts, test_s222_every_contract_has_a_struct_file
Scenario: check_local.sh and CI run the check (stack layer 4)
  Test: test_s222_check_local_and_ci_run_the_check
```
Tests: `tests/test_emit_contracts.py`. The story landed as a four-layer stack (rule 23, max 50 files a PR); each layer carries the test it turns green.


## Story #81 (epic #80, S1): the roadmap tests and a golden fixture in JS
```gherkin
Scenario: the reference roadmap tests run on node:test
  Given the 33 tests of the reference Python roadmap suite
  When they are ported to roadmap/ported.test.js (28 tests; the 5 deploy tests are the kit's S4 story)
  Then 7 pass on the current render.js (board, columns, delivered, epic link, plain words, Now, India clock) and 21 are todo tests naming #82 (data) or #83 (page), and ROADMAP_STRICT=1 runs the 21 as real failures
Scenario: the golden fixture gives the same model in Python and JS
  Given roadmap/fixtures/golden-issues.json, a synthetic GitHub answer with 27 issues (parents both ways, 4 milestones, Needs lines, doing label times) and 5 pull requests
  And roadmap/fixtures/golden-expected.json captured from the reference Python by roadmap/fixtures/expected.py
  When the JS builds its model from the same answer
  Then epics, and every story's epic, column, raw, text, needsWords and pull request equal the golden now
  And milestone, prio, needs, blockedBy, started, cycleMin (#82), timeline, here, next, older, milestones with days left, map with crossings, chain (#83) are todo until those stories land
Scenario: the runner is wired
  Then scripts/check_local.sh has a `roadmap` check running `node --test roadmap/*.test.js`, the same line as ci.yml
Scenario: a node:test file counts as the red test
  Given a PR whose `## Red` names roadmap/golden.test.js and whose diff adds that file
  When check_tdd.py runs
  Then it prints "tdd OK: roadmap/golden.test.js"
  Test: tests/test_check_tdd.py::test_s81_a_node_test_file_in_the_red_section_passes
```
Tests: `roadmap/ported.test.js` (28, prefix `S1`), `roadmap/golden.test.js` (10, prefix `golden:` plus the runner check), `tests/test_check_tdd.py::test_s81_a_node_test_file_in_the_red_section_passes`.


## Story #296 (2/6): the TechnologyModifiers catch-all holds only rows no framework doc fits
```gherkin
Scenario: a TechnologyModifiers row whose framework has its own doc fails
  Given the fixture entry for TechnologyModifiers: the row-name stems a framework doc owns (in-app purchase, subscription, product, map, tip, apple pay, wallet, image playground, web view, gesture, photos picker)
  When a row of the TechnologyModifiers doc holds one of its stems
  Then the test fails naming the catch-all, the row and the doc that owns it (InAppPurchase, Map, Tips, Wallet, ImagePlayground, web-view, Gestures or PresentationModifiers)
  Test: test_s296_a_catch_all_row_whose_control_has_its_own_doc_fails
Scenario: each framework doc exists, sets a family and holds a row of its stem
  Given every stem of the TechnologyModifiers entry
  Then its owner doc folder exists, the gate can count it (platformApi.ios.family) and it holds a row with that stem
  Test: test_s296_each_owner_doc_exists_sets_a_family_and_holds_a_row_of_its_stem
```
Tests: the same two tests of `tests/test_ui_catch_all.py`, with the fixture extended by the `TechnologyModifiers` entry.
