# ui/ios: accessibility (story #220)

## What the machine checks

Each template has one UI test in `A11yAudit/Tests/TemplateAccessibilityAuditTests.swift`.
The test opens the template in a small host app (`A11yAudit/Host/`).
Then it calls `performAccessibilityAudit()` (iOS 17 and later).

The audit checks the screen that is shown:

- Contrast of text against what is behind it.
- Dynamic Type: text grows with the user's size, and is not cut off.
- Hit regions: every control is big enough to tap (44 by 44 points).
- Labels: every control has a name VoiceOver can read.
- Element traits and parts that overlap.

It runs on CI in the job `ui-ios-snapshots`, after the snapshot tests.
XcodeGen makes the Xcode project from `A11yAudit/project.yml` on CI. The project is never committed.
A new template gets one `case` in the host app and one test.

## What a person checks (review-only)

No machine checks these. The reviewer looks at each one on every new or changed screen.

| Item | Tag | What to look at |
|---|---|---|
| Navigation pattern | `review-only` | The screen uses the HIG navigation for its job: a stack for drill-in, a sheet for a short task, a tab bar for top-level areas. Back always goes where the user expects. |
| Gestures | `review-only` | Every gesture has a visible control that does the same thing. No action needs a swipe, a long press, or two fingers alone. |
| VoiceOver order and meaning | `review-only` | Turn VoiceOver on. The reading order follows the screen. Each label makes sense on its own. |
| Reduce Motion | `review-only` | With Reduce Motion on, no animation slides or zooms the whole screen. |
| Colour alone | `review-only` | No state is shown by colour alone. An error also has words or an icon. |
| Keyboard and focus | `review-only` | The keyboard never hides the field or the main button. Return moves to the next field. |
| Language and length | `review-only` | Long words and right-to-left languages still fit. Button text says what happens. |
