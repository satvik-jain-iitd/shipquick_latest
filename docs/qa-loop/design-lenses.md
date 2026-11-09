# Design audit standard: the lenses

Use the lens id in every finding. A project adds its own lenses in its QA home, never here. Measure when you can. Praise what works with the same care.
Each finding also gets: impact (high, medium, low), effort (S, M, L), roadmap bucket (now, next, later).
Bucket rule: high impact and S effort is "now"; high impact and M or L is "next"; the rest is "later".

## Elephant lenses (the whole journey)
| Id | Lens | Ask | Source |
|---|---|---|---|
| J1 | Journey fit | Where does the user come from, where do they go? Is this the fewest steps? Any dead end? | NN/g journey mapping (A/K) |
| J2 | Promise kept | Does every screen keep the product's promise (the one line in the QA home README; worked example: GoServe, hot meals in 20 minutes)? | Product brief |
| J3 | Consistency | Same thing, same look, same words, same place across screens (Jakob's law, Nielsen #4) | Laws of UX, lawsofux.com (C, citing K) |
| J4 | Peak and end | Is the best moment strong and the last screen warm? (peak-end rule) | Kahneman (K) |
| J5 | Cold arrival | Does the screen work when opened from an alert, a link, or after a week away? | EGM goldfish idea (A) |
| J6 | Progress truth | Do step counters, titles and back paths tell the truth? | Nielsen #1 visibility (A/K) |
| J7 | Thumb path | On a step flow: is the main (filled) button last, bottom-anchored, at the same y on every step, the alternative above it, the hero centred on one shared line (measure, fail over 2 px)? On a typing step, does the button ride above the keyboard? | Hoober thumb zone 2013 (K/B), Apple HIG and Material reach (A), the GoServe owner's call, 9 Nov 2026 (worked example) |
| J8 | Kind no | When the answer is no (not served, sold out, offline), does the screen thank, tell the truth, keep a way out, and give a reason to come back? | the GoServe owner's call, 9 Nov 2026 (worked example) |

## Goldfish lenses (one screen)
| Id | Lens | Ask | Source |
|---|---|---|---|
| G1 | 5-second test | Can a stranger say what the screen is for and what to do? | NN/g 5-second test (A/K) |
| G2 | Feeling | Calm, trust, appetite; no worry about money or data | Don Norman, Emotional Design (K) |
| G3 | One clear action | One primary action, visually strongest; no rival buttons (Hick's law) | Laws of UX (C, citing K) |

## Craft lenses (the best designer's eye)
| Id | Lens | Ask | Source |
|---|---|---|---|
| C1 | Hierarchy | Size, weight, colour and space show order of importance; the eye path is clear | Refactoring UI (K) |
| C2 | Spacing rhythm | One spacing scale (for example 4 or 8 px steps); equal gaps for equal relations (Gestalt proximity) | Material 3 layout (A) |
| C3 | Alignment and grid | Edges line up; optical centring; nothing floats | Gestalt (K) |
| C4 | Type | Few sizes, clear roles, line length, no orphan words in titles | Butterick, Practical Typography (K) |
| C5 | Less but better | Can anything be removed? Every element earns its place | Dieter Rams, 10 principles (K); skill `claude-mem:design-is` |
| C6 | Honest and inevitable | Nothing decorative pretends to be functional; the design feels like the only answer | Rams, Apple design talks (P/K) |
| C7 | Imagery | Photos real, appetising, correct crop, no AI marks, consistent style | Brand rules |

## Usability lenses (Nielsen's 10 heuristics, https://www.nngroup.com/articles/ten-usability-heuristics/, A)
U1 visibility of status, U2 match with the real world (user's words), U3 user control and freedom (undo, back),
U4 consistency and standards, U5 error prevention, U6 recognition over recall, U7 flexibility, U8 minimal design,
U9 help users recover from errors (plain words, a way out), U10 help and documentation.

## Platform and access lenses
| Id | Lens | Check | Source |
|---|---|---|---|
| P1 | Touch targets | 44 x 44 pt (Apple) / 48 x 48 dp (Material); WCAG 2.2 AA minimum 24 x 24 px | Apple HIG, Material 3, WCAG 2.5.8 (A) |
| P2 | Contrast | Text 4.5:1, large text and icons 3:1 | WCAG 1.4.3, 1.4.11 (A) |
| P3 | Safe areas | Nothing under the notch, home bar or keyboard | Apple HIG (A) |
| P4 | Thumb reach | Main action in the lower part of a tall phone (Fitts's law) | Hoober, thumb zone (P/K) |
| P5 | Text size | Works with the largest system text size | WCAG 1.4.4 (A) |
| P6 | Brand guidelines | Third-party buttons follow their owner's rules (Google sign-in, maps credit) | Google Identity branding (A) |

## Content lenses
| Id | Lens | Check | Source |
|---|---|---|---|
| W1 | Plain words | Grade 5 to 7, short, the user's words, in the language the user speaks | Owner rule; plainlanguage.gov (A) |
| W2 | Honest errors | Every error is true for this user and shows the way out | Nielsen #9 (A/K) |
| W3 | Money clarity | Prices, fees, totals and payment state never in doubt | Baymard checkout research (B) |

## Benchmark lens
| Id | Lens | Check | Source |
|---|---|---|---|
| B1 | Category patterns | What users already know from the category leaders the QA home README names. Learn the pattern, never copy the look | Jakob's law (C, citing K) |
