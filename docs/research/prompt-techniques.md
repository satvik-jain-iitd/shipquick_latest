# Prompt techniques and micro-task breakdowns: the catalog

Owner's rule (29 Oct 2026): "different kinds of prompt engineering techniques and different kinds of breakdown of the problem into micro tasks should be tried whenever we are deciding which model to use, before reaching any conclusion on which model is best." This file is the list to try from. Every row has an id, so an experiment row can say `technique: T12, breakdown: B04`.

How to read it (web-research rule): a paper is Tier A for "the paper reports this on the models it tested"; those models were large and ran on GPUs. The column "small local model fit" is our own call for a 1B to 4B model on a CPU box and starts at confidence 0.5; it moves only when a project measures it and writes the result in the status column. A vendor page is Tier A for what the vendor says; the vendor sells tokens, so a technique that spends more tokens is read with that motive in mind. No number here comes from memory: a number with no source says "not measured".

Sources used most: Schulhoff et al., "The Prompt Report: A Systematic Survey of Prompting Techniques" (arXiv 2406.06608, 2024, revised 2025; a PRISMA review, 58 text techniques; Tier A 0.9 for "this technique exists and is defined so"); Wei et al. 2022 (chain of thought, arXiv 2201.11903); Chen, Zaharia, Zou 2023 (FrugalGPT, arXiv 2305.05176); Hsieh et al. 2023 (Distilling step-by-step, arXiv 2305.02301, Findings of ACL 2023); Khattab et al. 2023 (DSPy, arXiv 2310.03714); Dhuliawala et al. 2023 (chain of verification, arXiv 2309.11495); Hu et al. 2021 (LoRA, arXiv 2106.09685); Ollama docs (structured outputs with `format`, `think`). Confirmed by search on 29 Oct 2026 except where a row says otherwise.

Columns: id | name | how it works | small local model fit (1B to 4B, CPU) | cost | the code check that goes with it | source, tier, confidence | status in our projects.

## Part A: prompt techniques

### A1. Zero-shot framing (no examples)
| id | name | how it works | small local model fit | cost | code check | source, tier, confidence | status |
|---|---|---|---|---|---|---|---|
| T01 | Direct ask | One plain instruction, the input, one output line | Good: the baseline for every micro call; short input, short output | 1 call | output shape (regex, list membership) | Prompt Report, A, 0.9 | tried: job-search micro composer (E-CO-8) |
| T02 | Role prompt | "You are a recruiter" before the task | Weak on small models; adds tokens, rarely changes a one-line output | +10 to 30 tokens | none | Prompt Report (role prompting), A, 0.8; small-model fit 0.5 | not tried |
| T03 | Style and length instruction | "One sentence, under 25 words, first person" | Good: the cheapest control; small models follow a count badly, so code enforces it | none | word and character count, first-person regex | Prompt Report, A, 0.8 | tried: E-CO-8 (length gate) |
| T04 | Rephrase and respond | The model first restates the question, then answers | Poor on a CPU: doubles output tokens | 2x output | none | Deng et al. 2023 "Rephrase and Respond" (not confirmed by search on 29 Oct), C until read, 0.5 | not tried |
| T05 | Emotion or urgency words | "This matters a lot" in the prompt | Contested; no reason to expect a gain on a one-line output | none | none | Prompt Report lists it (A, 0.8 that it exists); effect contested, 0.3 | not tried, low priority |
| T06 | System to attention (S2A) | A first call strips the irrelevant parts of the input, a second answers | Good shape for a small model: the first call is a filter; same as B02 | 2 calls | the kept text must be a substring of the input | Prompt Report, A, 0.8 | not tried |
| T07 | Negative instruction | "Do not add numbers. No pay." | Small models follow "do not" badly; keep it, but the code check does the real work | none | regex for the banned thing | vendor guides say prefer positive phrasing (A, 0.7) | tried: "No pay" line plus the refusal regex |

### A2. In-context examples
| id | name | how it works | small local model fit | cost | code check | source, tier, confidence | status |
|---|---|---|---|---|---|---|---|
| T08 | One-shot | One worked example in the prompt | Risky: a small model copies the example value (job-search lesson, 29 Oct 2026: a literal id in the example became every answer). Use a fake example the code rejects | +50 to 150 tokens | reject any output equal to the example | Prompt Report, A, 0.9; our lesson, S, 0.9 | tried badly (E-CO-7); retry with a fake example |
| T09 | Few-shot (3 to 5) | Several examples, same shape | Good when the examples are the owner's own kept sentences; input grows past the 600 cap fast | +200 to 500 tokens | the example-copy check; the input cap | Prompt Report, A, 0.9 | not tried; needs kept sentences |
| T10 | Example selection by similarity | Pick the examples nearest to the input (embeddings) | Good: fewer, better examples keep the cap; we have nomic-embed-text | 1 embed call per input | same as T09 | Prompt Report (KNN example selection), A, 0.8 | not tried |
| T11 | Example order and balance | Order the examples, balance the labels | Matters for label tasks; costs nothing | none | none | Prompt Report cites order sensitivity, A, 0.8 | not tried |

### A3. Thought generation
| id | name | how it works | small local model fit | cost | code check | source, tier, confidence | status |
|---|---|---|---|---|---|---|---|
| T12 | Zero-shot chain of thought | "Think step by step" then answer | Poor on a CPU and on small models: Wei et al. report gains only around 100B parameters and no gain or harm below; the thinking tokens cost seconds per call | 3x to 10x output | strip the thinking, keep the last line | Wei et al. 2022, A, 0.9 (summaries read; check the paper for the exact threshold) | not tried on purpose |
| T13 | Few-shot chain of thought | Examples that show the steps | Same as T12, bigger input | input and output grow | same | Prompt Report, A, 0.9 | not tried |
| T14 | Step-back prompt | Ask a general question first, then the specific one | Two calls; the general step rarely helps a one-sentence task | 2 calls | none | Prompt Report, A, 0.8 | not tried |
| T15 | Analogical prompt | The model recalls a similar case first | Poor: more tokens, invented cases on a small model | 2x output | the grounded check | Prompt Report, A, 0.8 | not tried |
| T16 | Thinking models with think off | Reasoning models (qwen3.5) think by default; turn it off for micro calls | Required: with a 40 token cap the thinking ate the whole reply (E-CO-8 row 2) | none | empty-reply check | Ollama `think` parameter, A, 0.8; our lesson, S, 0.9 | tried: fixed in job-search PR #264 |

### A4. Decomposition
| id | name | how it works | small local model fit | cost | code check | source, tier, confidence | status |
|---|---|---|---|---|---|---|---|
| T17 | Least to most | Solve easier sub-questions first, feed them into the hard one | Good only when code does the splitting; the model gets one sub-question per call | n calls | each sub-answer checked alone | Zhou et al. 2022 (via the Prompt Report), A, 0.8 | not tried |
| T18 | Plan and solve | The model writes a plan, then follows it | Poor: planning tokens; a plan from a 1B model is weak | 2x output | none | Prompt Report, A, 0.8 | not tried |
| T19 | Decomposed prompting | A library of small prompts, each for one sub-task, called by a controller | Very good: this is micro-tasking with the controller in code | n small calls | per sub-task checks | Khot et al. 2022 (via the Prompt Report), A, 0.8 | tried: the engine's shape |
| T20 | Tree of thoughts | Several candidate steps, evaluate, branch | Poor on a CPU: many calls | 5x to 20x calls | none | Yao et al. 2023 (via the Prompt Report), A, 0.8 | not tried, out of budget |
| T21 | Skeleton of thought | An outline first, then each point filled in parallel | Good shape if the outline comes from code (the picked facts are the skeleton) | n parallel calls | per point checks | Ning et al. 2023 (not confirmed by search on 29 Oct), C until read, 0.5 | partly: the facts are the skeleton |
| T22 | Program of thoughts and PAL | The model writes code or a formula; a runtime computes | Good for numbers: the model never adds; code adds | 1 call plus a run | the run must succeed | Gao et al. 2022 (PAL, via the Prompt Report), A, 0.8 | not tried; our numbers come from facts only |

### A5. Ensembling
| id | name | how it works | small local model fit | cost | code check | source, tier, confidence | status |
|---|---|---|---|---|---|---|---|
| T23 | Self-consistency (vote) | Sample n answers, take the majority | Good for labels and yes or no with a 1B model (n tiny calls are cheap); not for sentences | n calls | majority rule in code | Wang et al. 2022 (via the Prompt Report), A, 0.9 | not tried |
| T24 | Prompt paraphrase ensemble | The same ask worded n ways, vote | Good for labels; catches wording luck | n calls | majority rule | Prompt Report, A, 0.8 | not tried |
| T25 | Mixture of experts prompts | Different role or style prompts, then vote or merge | Weak on small models (T02) | n calls | majority rule | Prompt Report, A, 0.7 | not tried |
| T26 | Universal self-consistency | A model picks the best of n answers | The picker is itself a model call; use a code rule (gates, length) instead | n plus 1 calls | the gates | Prompt Report, A, 0.7 | not tried |

### A6. Self-criticism
| id | name | how it works | small local model fit | cost | code check | source, tier, confidence | status |
|---|---|---|---|---|---|---|---|
| T27 | Self-refine | Draft, critique, rewrite | Poor on a small model: the critique is as weak as the draft; use code gates and one retry instead | 3 calls | the gates | Madaan et al. 2023 (via the Prompt Report), A, 0.8 | tried as "one retry on a gate" |
| T28 | Chain of verification | Draft, write check questions, answer them, revise | Good shape when the check questions come from code (does the sentence hold a number not in the fact?) | 2 to 4 calls | our gates are the checks | Dhuliawala et al. 2023, arXiv 2309.11495, A, 0.8 | tried as code gates, not as model questions |
| T29 | Self-calibration | Ask the model how sure it is | Small models are badly calibrated; prefer a decision API or code | 1 call | none | Prompt Report, A, 0.7 | not tried |
| T30 | Reflexion | Keep a memory of past mistakes, feed it in | Costs input tokens; our lessons file is the human version | input grows | none | Shinn et al. 2023 (via the Prompt Report), A, 0.8 | not tried |

### A7. Constraint and format control
| id | name | how it works | small local model fit | cost | code check | source, tier, confidence | status |
|---|---|---|---|---|---|---|---|
| T31 | Choice list | "Reply with one word from: a, b, c" | Very good: the best shape for a small model; code maps the word back | none | membership | vendor guides, A, 0.8; our runs, S, 0.8 | tried: memory observe type, book kind and class |
| T32 | Yes or no | One token answer | Very good; the cheapest filter | none | startswith yes | vendor guides, A, 0.8 | tried: book filter |
| T33 | JSON mode | `format: json` makes the reply valid JSON | Costly on a CPU: a document with many fields is a big output; fine for one field | output grows | schema check | Ollama structured outputs, A, 0.8 | tried: the one-call composer (retired for micro) |
| T34 | JSON schema or grammar constrained decoding | The decoder can only emit tokens the schema allows | Good for one small object; the server does the work | none | schema check | Ollama structured outputs (schema in `format`), A, 0.8 | not tried |
| T35 | Stop sequences and token caps | Stop at a newline; cap the tokens | Required on a CPU: the cap is the speed knob (job-search: 400 to 220 to 40) | none | empty-reply check | Ollama `num_predict`, A, 0.9; our runs, S, 0.9 | tried |
| T36 | Escape word | "or reply NONE" | Good: lets a small model say nothing instead of inventing | none | NONE check | our company card, S, 0.7 | tried |
| T37 | Short ids and aliases | Show f1, f2 instead of long ids | Required: small models mangle long ids (E-CO-7) | none | alias map back | our lesson, S, 0.9 | tried |
| T38 | Temperature 0 | Deterministic decoding | Required for evals and gates | none | none | vendor docs, A, 0.9 | tried |

### A8. Retrieval and grounding
| id | name | how it works | small local model fit | cost | code check | source, tier, confidence | status |
|---|---|---|---|---|---|---|---|
| T39 | Facts in the prompt | Only the picked facts are shown; nothing else may be claimed | Required: the fence | input per fact | ids offered, numbers from facts | our engine, S, 0.9 | tried |
| T40 | Quote then answer | The model copies the supporting words first, then answers | Very good: the copy is checked by code, invented text fails | 2 calls or 2 fields | substring check | our company card and book intake, S, 0.8; "cite the span" pattern in vendor guides, A, 0.7 | tried |
| T41 | Retrieval with a window | Vector search picks the k nearest memories inside a date window | Good: code picks, the model never searches | 1 embed call | k and window in params | our memory layer, S, 0.8 | tried |
| T42 | Prompt programs with optimisation (DSPy) | Prompts as programs; an optimiser picks examples and wording against a metric | Good idea for later: our eval is the metric; the optimiser needs many runs, so it belongs on the free tier or at night | many runs | the eval | Khattab et al. 2023, arXiv 2310.03714, A, 0.8 | not tried |

## Part B: micro-task breakdown patterns
| id | name | how it works | small local model fit | cost | code check | source, tier, confidence | status |
|---|---|---|---|---|---|---|---|
| B01 | Code first, then model | Regex, lists and counts do everything they can; the model gets only the rest | Required: the first rung of the doctrine | none | all of it | doctrine section 15, S, 0.9 | tried everywhere |
| B02 | Filter then extract | A yes or no gate before any writing call | Very good: most inputs stop at one tiny call | 1 call plus n for the yes cases | yes or no parse | our book intake, S, 0.8 | tried |
| B03 | Choose then write | Call 1 picks the key phrase from the input (a copy), call 2 words a sentence around it | Promising: the copy is checked, the sentence is grounded by construction | 2 calls | the phrase must be in the input; the sentence must hold the phrase | our plan, S, 0.5 (not measured; an E-CO-13 cell) | planned |
| B04 | Slot fill by code | The model fills one verb and one object; code writes the sentence from a template | Promising for 1B: the smallest possible output | 1 to 2 calls, 5 tokens each | slot membership and length | our plan, S, 0.5 (not measured; an E-CO-13 cell) | planned |
| B05 | Template fill | "I <did what> at <where>, which <result>" given to the model | Promising; the shape stops wandering | 1 call | the template words must remain | our plan, S, 0.5 (not measured; an E-CO-13 cell) | planned |
| B06 | Map over chunks, reduce in code | Cut the input into chunks under the cap, one call each, code joins | Required for anything over 600 characters | n calls | per chunk checks; join in order | our observe and card, S, 0.8 | tried |
| B07 | Extract then verify | A second tiny call or a regex checks the first call's output | Good: the verifier is a yes or no call, cheap | 2 calls | the verifier is code where possible | chain of verification (T28) made micro, A, 0.7 | partly: code gates |
| B08 | Quote then claim | The claim is kept only if its quote is in the source | Very good: invented claims cannot pass | 1 to 2 calls | substring | our card and books, S, 0.9 | tried |
| B09 | Classify then route | A label call picks which prompt runs next | Good: each branch prompt stays small | 1 plus 1 calls | label membership | our answer classes are code, S, 0.6; the model version is untried | partly |
| B10 | Pairwise compare and tournament | Ask "which of these two is better" instead of a score | Good for ranking with a small model: a choice, not a number | n log n calls | majority rule | pairwise judging in vendor eval guides, A, 0.7 | not tried |
| B11 | Vote over n tiny calls | The same label call n times (or n paraphrases), majority wins | Good for labels and yes or no; cheap with a 1B model | n calls | majority | self-consistency (T23) made micro, A, 0.8 | not tried |
| B12 | Checker gate, one retry, deterministic fallback | Code checks the output; one retry with the reason; then code's own fallback | Required: no silent failure, bounded calls | up to 2 calls | the gates | our composer, S, 0.9 | tried |
| B13 | Cascade small to big | Try the small model; only a failed gate goes to the next size, then the free tier | Required: the budget rule; FrugalGPT reports cost cuts up to 98 percent on their tasks with a cascade | 1 call most of the time | the gates decide the step | Chen, Zaharia, Zou 2023, arXiv 2305.05176, A, 0.8 | tried: the ladder |
| B14 | Draft then polish | Local micro sentences, one occasional big join on the free tier | Good for long answers only; under the day budget | 1 big call per long answer | gates after the polish | our PR 27, S, 0.7 | built, off by default |
| B15 | Question decomposition | A compound question becomes one-fact questions in code (or one tiny call), each answered alone | Good: each micro call sees one question | n calls | per question checks | least to most (T17) made micro, A, 0.7 | not tried |
| B16 | Progressive summarisation | Chunk summaries, then a summary of summaries, each under the cap | Good for long notes and books | n plus 1 calls | numbers must come from the chunks | map-reduce summarisation, vendor guides, A, 0.7 | not tried |
| B17 | Parallel independent calls | Run the independent micro calls at once | Measure first: RAM and the one CPU queue (E-CO-9) | same calls, less wall time | RAM floor | our plan, S, 0.5 (not measured; E-CO-9) | planned |
| B18 | Label capture for fine-tuning | Every owner edit and every gate verdict becomes a training pair; the small model is fine-tuned on them later | The owner's end goal: Hsieh et al. report a 770M model beating a 540B few-shot model on their benchmarks after training on rationales; LoRA makes the training cheap | training on Colab or Kaggle | the same eval before and after | Hsieh et al. 2023, arXiv 2305.02301, A, 0.8; Hu et al. 2021 LoRA, arXiv 2106.09685, A, 0.9 | logging built (job-search answer_runs.micro) |
| B19 | Decision API instead of a generator | A calibrated decision model (choice, score, boolean) answers in one pass | Good for labels when the local model is unsure; cheap and fast | 1 call, paid cents | the choice list | doctrine section 15 (Jev, Laya), S, 0.7 | not tried in job-search |

## Part C: the decision procedure (no model verdict without the matrix)
1. Fix the model: the smallest installed local model that gives readable output on the task (one quick look at 10 outputs).
2. Fix the task's eval: a golden subset of about 20 rows and the project's marks, unchanged for the whole matrix.
3. Pick the cells by output kind, 5 to 8 cells, not 40:
   - a label or a yes or no: T31, T32, T23 or B11, T24, T09 with a fake example, B19;
   - one field or a copied span: T40, B08, T36, T34, T10;
   - one sentence: T01, T03, B03, B04, B05, T09 (own kept sentences), B12 always on;
   - a list or a long text: B06, B16, B02 before anything, B14 only on the free tier.
4. Pre-register the matrix in `docs/research/experiments.md` with the template in `docs/templates/experiment-matrix.md`: one row per cell with its ids, before any run.
5. Run every cell on the same subset; one row per cell with the marks (accuracy, fallback or gate failures, duplicates, p95). Read 30 real outputs per winning cell, not only the numbers.
6. The best cell becomes the default. Only when the best cell still fails the marks, step the model up one size and rerun the two or three closest cells. Never conclude "model X is best" from one prompt and one breakdown.
7. Write the result back into the status column of this file (a raise-and-forget PR to ShipQuick), so the next project starts from what was measured.
