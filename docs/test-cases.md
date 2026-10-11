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