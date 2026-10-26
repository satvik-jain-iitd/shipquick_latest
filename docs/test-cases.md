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
  Then each open story issue is closed with the comment "Done in PR #X (squash-merged to <base>)."
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
  When two branches each add a row at the end of docs/process-trace.md (or LEARNINGS.md, ideas.md)
  Then they merge with no conflict and both rows are kept (.gitattributes merge=union)
  And without that file the same merge conflicts (the control)
  And CHANGELOG.md is not on the list
  And the sprint lane template asks for the files each story touches, and for foundation work first
  And a release goes through release/vX.Y.Z with main merged in, a merge commit, and a back-merge of main into dev after the tag
  And the roster allows one reviewer and up to 3 coders, each in a worktree
```
Tests: `tests/test_parallel_lanes.py` (`test_s14_*`).

