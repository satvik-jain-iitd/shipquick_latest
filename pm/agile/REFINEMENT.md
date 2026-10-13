# Refinement

How to groom a story before it can be planned.

## When

Once per week, before sprint planning. 30 minutes is enough.

## Steps

1. Open the issue. Read the title and body.
2. Check **INVEST** (below). Fix what fails.
3. Set **Impact** and **Urgency** (see `PRIORITIZATION.md`).
4. Set a **T-shirt size** (below).
5. If the story is too big, split it.
6. If it is not clear, write the missing detail or mark it `blocked`.
7. Set the `p:` label.
8. Move the issue to the **Refined** column.

## INVEST check

| Letter | Question |
|---|---|
| I | Independent? Can it ship alone? |
| N | Negotiable? Is the how still open? |
| V | Valuable? Does the user get something? |
| E | Estimable? Is it clear enough to size? |
| S | Small? Can one person review it in one sitting? |
| T | Testable? Can we prove it works? |

## T-shirt size

Size means **change surface and risk**. It does not mean time.

| Size | Meaning |
|---|---|
| XS | One file, one change, no risk. |
| S | A few files, one clear change. |
| M | Several files, one feature, some tests. |
| L | Many files, a full feature, high review surface. |
| XL | Too big. Split it before planning. |

Rule: anything `L` or `XL` should be split unless it truly cannot.

## Split rules

Split a story by:
- Workflow step (login, then profile, then logout).
- Data type (one table at a time).
- Platform (web first, then mobile).
- Happy path first, then edge cases.

## Definition of Ready

A story is Ready when:
- The value is clear and one line long.
- It passes INVEST.
- It has Impact, Urgency, and a T-shirt size.
- It has clear acceptance criteria.
- It has no open `blocked` label.
