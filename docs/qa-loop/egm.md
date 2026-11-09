# Elephant-Goldfish model (EGM) in the QA loop

## Sources read (9 Nov 2026)
| Source | Link | Tier | What we take |
|---|---|---|---|
| EGM repo, README | https://github.com/google/elephant-goldfish-model | A (the authors) | Roles: elephant drafts with full context, goldfish reviews with fresh context, owner decides |
| EGM blog post | https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html | A | Why fresh eyes find unstated assumptions |
| Reviewer personas | https://github.com/google/elephant-goldfish-model/tree/main/agents | A | Read-only, stateless, no chitchat; severity Blocker, Major, Nit; a failed reviewer is "not run" |
| Review loop skill | https://github.com/google/elephant-goldfish-model/blob/main/skills/egm-review-loop/SKILL.md | A | Custom reviewer persona files and custom standards by path |
| Dave Rensin essay (Google), Apr 2026, updated 21 Oct 2026 | https://drensin.medium.com/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874 | P (first-hand, a Google engineering leader; sells nothing, the plugin is free) | The method itself: feed the elephant, test it against the goldfish |
Repo facts at read time: Apache-2.0, pushed 8 Nov 2026, about 15k stars, plugin for Claude Code.
"Google recommends" means: the EGM authors say so. Confidence it helps us: 0.7 until our own test (below).

## Decision: adopt the engine, add our pieces (hybrid)
1. Plans, specs, ADRs, stories: use EGM directly (`/egm:egm-brainstorm`, `egm-draft`, `egm-review`,
   `egm-resolve`, `egm-drift-report`). Do not copy or rewrite it.
2. Design audit and QA: EGM has no screens, no test runs, no canvas, no GitHub bug flow. The QA loop does
   those, using EGM's roles and rules. Our design reviewers are written in EGM's persona format
   (`docs/qa-loop/goldfish_*.md`), so they can run inside `/egm:egm-review-loop` with custom paths once the plugin is
   installed and a test passes. Until then the QA loop runs them as plain fresh subagents with the same text.
3. Conflict to settle with the owner: EGM reviews spawn many reviewers in parallel; the project may cap
   subagents (for example at 2). Run EGM reviews within that cap unless the owner says otherwise.

## Test before trusting (global rule 10)
Hypothesis: EGM review of a plan finds at least one real gap our own review missed.
Design: run `/egm:egm-review` on one real plan, compare with our review. Decision rule: one real gap or more
in 2 of 3 plans means EGM review becomes a required gate for plans. Record in `docs/research/experiments.md`.

## Mapping for design
| Role | Sees | Asks |
|---|---|---|
| Elephant | `journey.md`, all boards in order, approvals, brand, past bugs | Does this screen fit? What came before and after? Is the promise kept? Is it consistent? Is any step extra? |
| Goldfish (cold user) | One screen image only | What is this? What do I do? How do I feel? What worries me? What would I tap? |
| Goldfish (critic) | One screen image plus the design standard | Which lens fails, where, why, how to fix |
| Goldfish (step reader) | Only the written test steps | Which step can I not follow without guessing? |
| Owner | Synthesis | Trade-offs, yes or no |
A finding where the elephant says "clear from context" and the cold goldfish is lost = "leans on memory".

## The essay's protocol, step by step, and where it lives in this loop
Rensin's rule: "Feed the Elephant; test it against the Goldfish." Design is the new code: when the code is written
by AI, every judgment must "shift left" into a document a human can read. For us the design canvas and the screen
files are that document. Confidence the method helps us: 0.7 (one expert's first-hand account, 100,000 Googlers used
his tool; no controlled study). Our own test is below.

| Essay step | What it says | In this loop |
|---|---|---|
| Victory loves preparation | Let the AI interrogate you and challenge your assumptions before it produces anything | Before a run, the elephant writes `journey.md` and asks the owner only what the boards cannot answer |
| Trust but verify | Write the grading rubric before the work, then let a fresh session work against topic plus rubric | Expected results and pass marks are written in the screen file before any case runs; the design standard (`design-lenses.md`) is the rubric the goldfish gets |
| A word about judgment | Never outsource judgment to the model | The owner confirms bugs and approves board changes; the audit only proposes |
| Save three artifacts, not the chat | Description, criteria, output; the rest is token noise | Screen file (description and cases), lenses (criteria), runs and report (output) |
| Step 1 Context loading | Ask the AI to describe what it learned; correct it at once | Each session starts by stating the journey back from `journey.md`; fix it before testing |
| Step 2 No-code rule | Discuss first, build later | No board change and no story before the design review and the cases are written |
| Step 3 Sycophant challenge | "You are not being helpful. Your best use is to challenge my thinking." "Why do you think that?" | Every goldfish prompt says each real flaw found makes it more useful; the elephant asks "why do you think that?" of every finding before it goes in the report |
| Step 4 AI drafts first | Ask the model to propose first; reacting to your own draft hides blind spots | The elephant writes the cases and the design review before reading old notes or the owner's guesses |
| Phase 2 The doc | Problem, plan, alternatives (rejected ideas as guardrails), every file to change | A bug story: before, after, why, steps, files. The canvas "Rejected" section is the alternatives list; a finding that repeats a rejected idea is dropped |
| Step 5 Comprehension test | A fresh session explains the doc back; if it cannot, the doc lacks context; loop | Cold-user goldfish per screen (can a stranger say what the screen is for?); step-reader goldfish on the owner's test steps |
| Step 6 Critic review | A fresh expert lists what was missed; about 30 percent of ideas are valuable; repeat until only nits | Critic goldfish with the design standard; a screen is done when a new critic pass returns only nits |
| Step 7 Implementation readiness | A fresh engineer: do I have everything to build this on the first pass? | Before a story goes to the developer, a goldfish gets only the issue text and the board image and lists its questions; answer them in the issue first |
| Step 9 Mean review | "Tear it to shreds"; repeat until trivial | Every PR review: a goldfish with only the diff, the board and the issue, asked to find every way it fails the board |
| Peanuts and hay | Small README summaries feed context cheaply | `journey.md`, the QA home `README.md` and screen files are the elephant's food, not raw code |
| Managing agents | Give outcome and guardrails, the scope of authority and when to stop; ramp slowly (3 to 5 agents) | Briefs name the outcome, the files they may touch and when to stop; within the project's subagent cap |
