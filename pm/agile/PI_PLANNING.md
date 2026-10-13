# PI Planning

How to plan a PI, which is one D increment.

## What a PI is

A PI is a D increment. It is a big goal that takes about 3 to 4 sprints.
Each PI is tracked as an epic issue and a file `docs/pis/D<n>.md`.

## Steps

1. Read `docs/ROADMAP.md`. Pick the next D increment.
2. Write the PI goal: two or three sentences. What will exist that does not exist now?
3. Break the goal into epics. Each epic is a group of stories.
4. For each epic, list the stories at a high level. They do not need full detail yet.
5. Mark dependencies between stories. Find the unblockers.
6. Order the epics by value (see `PRIORITIZATION.md`).
7. Map the stories to sprints across the PI.
8. Copy `templates/pi-plan.md` into `docs/pis/D<n>.md`. Fill it in.
9. Create the epic issues. Link each story to its epic.

## Output

- One file: `docs/pis/D<n>.md`.
- One epic issue per epic.
- One milestone per sprint in the PI.

## Keep it light

Do not over-plan. A PI is a direction, not a contract.
Stories get detail during refinement, sprint by sprint.
