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
