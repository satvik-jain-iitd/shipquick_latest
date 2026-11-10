# Commit Guidelines

Short sentences. One idea per sentence.

## Format

```
type(scope): description
```

## Types

| Type | Use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Docs only |
| `design` | Design system, tokens, components |
| `test` | Tests only |
| `chore` | Maintenance |
| `refactor` | Code change, same behavior |
| `style` | Formatting only |
| `perf` | Performance |
| `ci` | CI and pipelines |
| `build` | Build system |
| `release` | A release: changelog, notes, the dev to main PR |

## Rules

1. Subject max 72 chars.
2. English only.
3. Lowercase type and scope.
4. No period at end of subject.
5. Body explains why, not what.
6. Co-author line when required.
7. A branch that changes code carries a `## Red` section in a commit body that names the test file you saw fail, for example `- tests/test_widget.py::test_widget_rejects_empty`. The pre-push `tdd` check reads the commit log, because there is no PR body yet; CI reads the real PR body.

## Examples

Good:
```
feat(auth): add login rate limit
docs: update README quick start
fix(api): return 404 for missing user
```

Bad:
```
fixed stuff
WIP
Update README.md
feat: Added A Really Long Description That Goes Over Seventy Two Characters
```
