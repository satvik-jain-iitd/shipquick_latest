# Prioritization

How we decide what to work on. Value first. No effort terms.

## The rule

Do not estimate hours, days, or story points. AI writes the code, so effort is flat.
Rank by value and risk only.

## Score each item

Answer four questions. Keep the answer short.

| Factor | Values | Meaning |
|---|---|---|
| Impact | H / M / L | How much value the user gets |
| Urgency | H / M / L | How soon it is needed |
| Dependencies | None / Soft / Hard | Does it unblock or block other work? |
| Risk | Low / Medium / High | How much unknown or blast radius |

## Order

1. **Spikes first.** A spike reduces risk. Do it before the story it unblocks.
2. **Unblockers first.** Items with no dependency that others wait on.
3. Then sort by Impact, then Urgency.
4. Then sort by Risk (lower risk first when value ties).

## Buckets (MoSCoW)

| Label | Meaning |
|---|---|
| `p:must` | The PI does not ship without it. |
| `p:should` | Important, but the PI can ship without it. |
| `p:could` | Nice to have. Only if time allows. |
| `p:wont` | Not now. Recorded, not planned. |

## Every item gets one line: why now

Add a one-line "why now" to each issue. If you cannot write it, the item is not ready.

## What we do not use

- No velocity. No story points. No hours.
- No "how long will this take". Only "what value, what risk".
