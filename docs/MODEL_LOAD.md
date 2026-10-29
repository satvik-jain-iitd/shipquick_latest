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

## 4. The Oracle CPU ceiling and the one third rule
From the owner's own tests: on the Oracle CPU box no model above 4B parameters can finish a run. 4B is the most it can do and it is very slow. Models of 1B or less work best. Never plan a model above 4B for the box.
Published speeds (tokens a second) come from GPU machines. On this CPU the owner measured about one third (50 on a GPU became 14 to 18). So every speed estimate for the box starts at one third of the published number, as the worst case. Only a real measured run on the box replaces it. Never a better assumption.

## 5. The target: speed with 70 percent accuracy, then fine-tune
Speed first, with about 70 percent accuracy. Then more accuracy by fine-tuning on the owner's own data, not by a bigger model.
A task that scores between 0.5 and 0.8 on the smallest fast model is a fine-tuning candidate. Log the pairs from day one: the prompt, the model's output, the gate result, and the owner's edit. Find one real source (the vendor's doc or a person's own result) that fine-tuning a model of this size helps on this kind of task. Train on Colab or Kaggle, never on the Mac. Only the small output model comes back. Run the same eval before and after. Promote only when accuracy beats the next bigger model at lower latency.

## 6. Two lanes
`urgent` means the owner is waiting: a Telegram word, a panel call, a chat. `background` means nobody waits: backfill, intake, cards, imports, evals.
Background work runs in the night window (01:00 to 07:00 IST). It steps back while an urgent call holds the busy lock, and exits with "busy, try later". One local model stays loaded at a time: background uses the urgent model so the server never swaps models.

## 7. The free tier, occasional and budgeted
A big call (a whole paragraph, a long merge, a hard judgement) may go to the OpenRouter free tier. Only from the urgent lane. Only for a big-task class the plan names. Never from a background job. Never with private text. The day budget is 10 percent of the account's free cap (100 of 1,000 today), with a 10 second gap between calls; a 429 cools the key off. The key is shared across projects, so the budget is per project and the counters live in a state file, never in the repo. A missing key means local, never an error to the user.

## 8. Every model call is listed
`docs/data/model-calls.md` holds one row per call site. `scripts/model_calls.sh` lists the call sites in the repo; `scripts/model_calls.sh --check docs/data/model-calls.md` fails when a call-site file is missing from the table. Run it in CI or before a push.

Table template:

```markdown
| # | Call | In (chars) | Out (tokens, shape) | Model | Lane | Eval |
|---|---|---|---|---|---|---|
| 1 | `app/engine.py` one sentence per fact | 400 | 40, one sentence | gemma3:1b | urgent | E-CO-8 |
```

For every speed number in the table write three values: published, the one third estimate, and measured on the box (blank until a run).

## 9. n8n
A model step in a workflow carries a `**Model:**` line in its sticky note (model, input cap, output cap, lane). The same rules sit in the n8n rulebook, section B14.

## 10. Before choosing a model: the technique and breakdown matrix
Owner, 29 Oct 2026: "different kinds of prompt engineering techniques and different kinds of breakdown into micro tasks should be tried whenever we are deciding which model to use, before reaching any conclusion on which model is best."
Never conclude "model X is best" from one prompt and one breakdown. Fix the smallest readable model, fix the eval, pick 5 to 8 cells from the catalog by output kind, pre-register them, run them all, read 30 real outputs of the winner, and only then step the model up. The catalog with ids, the fit notes for small CPU models, the sources with tiers, and the full procedure: `docs/research/prompt-techniques.md` (Part C). The pre-registration template: `docs/templates/experiment-matrix.md`. The result goes back into the catalog's status column with a PR to ShipQuick.
