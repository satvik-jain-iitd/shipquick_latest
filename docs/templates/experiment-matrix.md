# Experiment matrix template (copy into docs/research/experiments.md before any run)

Rule: no model verdict without the matrix (`docs/research/prompt-techniques.md`, Part C).

```markdown
## E-XX-N: <task> on <model>, techniques x breakdowns (pre-registered <date>)
- Task and output kind: <one sentence, one label, one field, a list>
- Model (fixed for the matrix): <name:size>; speed estimate for the box = one third of the published number until measured
- Subset: <n> rows of <golden file>, chosen <how>
- Marks (unchanged for every cell): <accuracy mark>, <fallback or gate-failure mark>, <duplicate mark>, p95 <ms>
- Cells (ids from the catalog), one row each, filled after the run:

| cell | technique | breakdown | accuracy | fallback or failures | duplicates | p95 ms | calls per row | pass | read 30 outputs? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | T01 | B12 | | | | | | | |
| 2 | T03 | B03 | | | | | | | |

- Decision rule: the best cell by <mark order> becomes the default; a model step up only when the best cell fails the marks; then the two or three closest cells rerun on the bigger model.
- Result and decision: <filled after the run; the status column of the catalog updated by a PR to ShipQuick>
```
