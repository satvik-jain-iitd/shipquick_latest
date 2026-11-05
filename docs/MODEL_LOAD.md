# Model load: size every task to the model

Owner rules, 29 Oct 2026, from the job-search project. Every project that uses ShipQuick follows them. The owner's own words are kept in quotes.

> "try 1-2 billion parameter models first, as small a model as you can; fail in the smallest model first, then move to bigger model."
> "accuracy comes when we do small things with a deep focus."

## 1. One job per call
A local model gets one small job per call: a label, a yes or no, one field, or one sentence. Never a paragraph. Never a document with many fields. Code splits the input and code puts the output together. Code runs first (regex, lists, counts) and the model only does what code cannot.

## 2. Input cap per call
600 characters for a model of 1B to 2B parameters. 1,200 characters for 3B to 4B. Over the cap, code cuts the text into chunks at sentence ends, or code picks the chunk that matters (keyword overlap) before the call.

## 3. The size ladder, by eval
Each task has its own golden set and fixed marks. Run the smallest installed model first. Step up one size only when the marks fail. Before stepping up, try one prompt change and one more split, each measured. Record every run (model, p95, marks) in `docs/research/experiments.md`. A run that fails is kept, not deleted.

## 4. The run box's ceiling and the measured-factor rule
Every project has a run box (the machine the local model actually runs on) with its own ceiling: the largest model size that box can finish a run with, measured by a real test, not a guess. Never plan a model above that box's measured ceiling.
Published speeds (tokens a second) come from reference machines that rarely match the project's own box. So every speed estimate for the box starts as the published number times a measured factor (one third, until a real run replaces it), as the worst case. Only a real measured run on the box replaces that factor. Never a better assumption.

## 5. The target: speed with workable accuracy, then fine-tune
Speed first, with a workable accuracy floor the project sets for the task. Then more accuracy by fine-tuning on the project's own data, not by a bigger model.
A task that scores in the project's fine-tuning band on the smallest fast model is a fine-tuning candidate. Log the pairs from day one: the prompt, the model's output, the gate result, and the reviewer's edit. Find one real source (the vendor's doc or a person's own result) that fine-tuning a model of this size helps on this kind of task. Train on whichever free-compute host the project uses, never on the project's own laptop. Only the small output model comes back. Run the same eval before and after. Promote only when accuracy beats the next bigger model at lower latency.

## 6. Two lanes
`urgent` means someone is waiting: a live call, a panel, a chat. `background` means nobody waits: backfill, intake, cards, imports, evals.
Background work runs in the project's own night window (set per project, when nobody is waiting). It steps back while an urgent call holds the busy lock, and exits with "busy, try later". One local model stays loaded at a time: background uses the urgent model so the server never swaps models.

## 7. The free tier, occasional and budgeted
A big call (a whole paragraph, a long merge, a hard judgement) may go to the project's chosen free-tier model. Only from the urgent lane. Only for a big-task class the plan names. Never from a background job. Never with private text. The day budget is a fixed share of that tier's own free cap, with a cooldown gap between calls; a 429 cools the key off. The key is shared across projects, so the budget is per project and the counters live in a state file, never in the repo. A missing key means local, never an error to the user.

## 8. Every model call is listed
`docs/data/model-calls.md` holds one row per call site. `scripts/model_calls.sh` lists the call sites in the repo; `scripts/model_calls.sh --check docs/data/model-calls.md` fails when a call-site file is missing from the table. Run it in CI or before a push.

Table template:

```markdown
| # | Call | In (chars) | Out (tokens, shape) | Model | Lane | Eval |
|---|---|---|---|---|---|---|
| 1 | `app/engine.py` one sentence per fact | 400 | 40, one sentence | gemma3:1b | urgent | E-CO-8 |
```

For every speed number in the table write three values: published, the one third estimate, and measured on the box (blank until a run).

## 9. Workflow tools
A model step in a workflow carries a `**Model:**` line in its sticky note or card (model, input cap, output cap, lane). A project that runs n8n keeps the same rules in its own n8n rulebook, section B14.

## 10. Before choosing a model: the technique and breakdown matrix
Owner, 29 Oct 2026: "different kinds of prompt engineering techniques and different kinds of breakdown into micro tasks should be tried whenever we are deciding which model to use, before reaching any conclusion on which model is best."
Never conclude "model X is best" from one prompt and one breakdown. Fix the smallest readable model, fix the eval, pick 5 to 8 cells from the catalog by output kind, pre-register them, run them all, read 30 real outputs of the winner, and only then step the model up. The catalog with ids, the fit notes for small CPU models, the sources with tiers, and the full procedure: `docs/research/prompt-techniques.md` (Part C). The pre-registration template: `docs/templates/experiment-matrix.md`. The result goes back into the catalog's status column with a PR to ShipQuick.

## Worked example (job-search, 29 Oct 2026)
The numbers below are one project's own setup, not the rule. They show what sections 4, 6, 7 and 9 look like filled in.
- Run box and ceiling (section 4): the Oracle CPU box. No model above 4B parameters finishes a run on it; 4B is the most it can do and it is very slow; 1B or less works best. Measured factor: about one third of published GPU speed (50 tokens/s on a GPU measured as 14 to 18 on this box).
- Night window (section 6): background work runs 01:00 to 07:00 IST; `urgent` means a Telegram word, panel call or chat.
- Free tier and budget (section 7): the OpenRouter free tier, a day budget of 100 of the account's 1,000 free calls, 10 second gap between calls.
- Fine-tuning host (section 5): Colab or Kaggle, never the Mac. Accuracy floor: about 70 percent before fine-tuning.
- Workflow tool (section 9): n8n, rulebook section B14.
