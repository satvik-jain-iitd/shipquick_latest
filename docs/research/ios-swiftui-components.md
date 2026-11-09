# iOS: Apple's standard components, counted (story #135, S5)

Date: 2026-11-09. Read by the coder (shipquick-dev).

## Sources (all Tier A: Apple's and Google's own docs)

- Apple Human Interface Guidelines, Components: https://developer.apple.com/design/human-interface-guidelines/components
  (read as JSON from `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json`, the data the page renders).
- Each HIG component page: its "Platform considerations" line ("Not supported in iOS ...") and its "Developer references".
- SwiftUI docs, for exact type names and the iOS version: https://developer.apple.com/documentation/swiftui/controls-and-indicators,
  https://developer.apple.com/documentation/swiftui/text-input-and-output, https://developer.apple.com/documentation/swiftui/lists,
  https://developer.apple.com/documentation/swiftui/menus-and-commands, and each type's own page (linked in the table).
- Google's Compose components page, for the Android twin: https://developer.android.com/develop/ui/compose/components

Confidence that the table is right: 0.85. The source is the vendor itself. The weak spot is the twin column: it is our
judgement of "same job", not a fact from either vendor.

## How we counted

Apple's Components page has 64 component pages in 8 groups. We count a page when all three are true:

1. Apple does not say "Not supported in iOS" on that page.
2. It is a part of an app's own screens. So the group "System experiences" is left out (10 pages: App Shortcuts,
   Complications, Controls, Live Activities, Notifications, Snippets, Status bars, Top Shelf, Watch faces, Widgets).
   Those are system surfaces, built with WidgetKit, ActivityKit or App Intents, not screens in the app.
3. SwiftUI has a type or a view modifier for it on iOS. We take the name from the page's "Developer references".
   When the page names only UIKit, we use the SwiftUI part that Apple's SwiftUI docs list for the same job
   (rows 8 and 24). Every SwiftUI name was checked on its own page for an iOS version.

Left out, with the reason:
- Not supported in iOS (Apple says so): Column views, Lockups, Outline views, Tab views (a macOS tab view; iOS uses tab bars),
  Dock menus, Ornaments, The menu bar, Path controls, Token fields, Panels, Windows, Combo boxes, Digit entry views,
  Image wells, Rating indicators. (15)
- No SwiftUI part named by Apple for it on iOS: Charts (the Swift Charts framework, not SwiftUI), Web views (WebKit `WKWebView`),
  Collections (UIKit `UICollectionView`; SwiftUI grids are layout containers, which rule 38 already allows),
  Edit menus (UIKit `UIEditMenuInteraction`), Home Screen quick actions (UIKit, outside the app's screens),
  Activity rings (HealthKitUI). (6)
- 64 pages - 10 system - 15 not on iOS - 6 no SwiftUI part = 33.

Count: 33

Of these, 25 rows are a SwiftUI view type or style and 8 are a view modifier (context menu, toolbar, search,
action sheet, alert, popover, sheet, keyboard type). SwiftUI ships those 8 only as modifiers.

SwiftUI also has controls that have no HIG page of their own, so they are not in the count:
`Link`, `EditButton`, `PasteButton`, `RenameButton`, `TextFieldLink`, `HelpLink`, `MultiDatePicker`, `ContentUnavailableView`,
`TextEditor`, `Form`, `NavigationStack`, `NavigationLink`. A later story can add a doc for any of them when a screen needs it.

## The counted list

Checked: 2026-11-09. That one date covers every row below.
"iOS since" is the earliest iOS of the symbol and every overload with the same name. Apple gives each overload its
own page; the page without a suffix is often the newest overload, not the first. Row 15 was wrong for that reason
(the unsuffixed page is the iOS 16 `LocalizedStringResource` overload; the `Text` prompt overload is iOS 15.0), so
every row was checked again the same way on 2026-11-09. No other row changed.

"Same as M3 component" names the component on Google's Compose page that does the same job.
`none (iOS-only)` means Google's page has nothing for that job. Each iOS-only row has its own doc in `ui/components/`
(the "Our doc" column). A shared row gets `platforms.ios` added to the Android doc in a later PR, after story S4 merges.

| # | HIG component | SwiftUI type | iOS since | Doc URL | Same as M3 component | Our doc |
|---|---|---|---|---|---|---|
| 1 | Image views | `SwiftUI.Image` | 13.0 | https://developer.apple.com/documentation/swiftui/image | none (iOS-only) | `Image` |
| 2 | Text views | `SwiftUI.Text` | 13.0 | https://developer.apple.com/documentation/swiftui/text | none (iOS-only) | `Text` |
| 3 | Boxes | `SwiftUI.GroupBox` | 14.0 | https://developer.apple.com/documentation/swiftui/groupbox | Cards | - |
| 4 | Disclosure controls | `SwiftUI.DisclosureGroup` | 14.0 | https://developer.apple.com/documentation/swiftui/disclosuregroup | none (iOS-only) | `DisclosureGroup` |
| 5 | Labels | `SwiftUI.Label` | 14.0 | https://developer.apple.com/documentation/swiftui/label | none (iOS-only) | `Label` |
| 6 | Lists and tables | `SwiftUI.List` | 13.0 | https://developer.apple.com/documentation/swiftui/list | Lists | - |
| 7 | Split views | `SwiftUI.NavigationSplitView` | 16.0 | https://developer.apple.com/documentation/swiftui/navigationsplitview | none (iOS-only) | `NavigationSplitView` |
| 8 | Activity views | `SwiftUI.ShareLink` | 16.0 | https://developer.apple.com/documentation/swiftui/sharelink | none (iOS-only) | `ShareLink` |
| 9 | Buttons | `SwiftUI.Button` | 13.0 | https://developer.apple.com/documentation/swiftui/button | Buttons | - |
| 10 | Context menus | `SwiftUI.View.contextMenu(menuItems:)` | 13.0 | https://developer.apple.com/documentation/swiftui/view/contextmenu(menuitems:) | Menus | - |
| 11 | Menus | `SwiftUI.Menu` | 14.0 | https://developer.apple.com/documentation/swiftui/menu | Menus | - |
| 12 | Pop-up buttons | `SwiftUI.MenuPickerStyle` | 14.0 | https://developer.apple.com/documentation/swiftui/menupickerstyle | Menus | - |
| 13 | Pull-down buttons | `SwiftUI.Menu` | 14.0 | https://developer.apple.com/documentation/swiftui/menu | Menus | - |
| 14 | Toolbars | `SwiftUI.View.toolbar(content:)` | 14.0 | https://developer.apple.com/documentation/swiftui/view/toolbar(content:) | App bars | - |
| 15 | Search fields | `SwiftUI.View.searchable(text:placement:prompt:)` | 15.0 | https://developer.apple.com/documentation/swiftui/view/searchable(text:placement:prompt:)-18a8f | Search | - |
| 16 | Sidebars | `SwiftUI.ListStyle.sidebar` | 14.0 | https://developer.apple.com/documentation/swiftui/liststyle/sidebar | Navigation drawer | - |
| 17 | Tab bars | `SwiftUI.TabView` | 13.0 | https://developer.apple.com/documentation/swiftui/tabview | Navigation bar | - |
| 18 | Action sheets | `SwiftUI.View.confirmationDialog(_:isPresented:titleVisibility:actions:)` | 15.0 | https://developer.apple.com/documentation/swiftui/view/confirmationdialog(_:ispresented:titlevisibility:actions:)-46zbb | Bottom sheets | - |
| 19 | Alerts | `SwiftUI.View.alert(_:isPresented:actions:)` | 15.0 | https://developer.apple.com/documentation/swiftui/view/alert(_:ispresented:actions:)-1bkka | Dialogs | - |
| 20 | Page controls | `SwiftUI.PageTabViewStyle` | 14.0 | https://developer.apple.com/documentation/swiftui/pagetabviewstyle | none (iOS-only) | `PageControl` |
| 21 | Popovers | `SwiftUI.View.popover(isPresented:attachmentAnchor:arrowEdge:content:)` | 13.0 | https://developer.apple.com/documentation/swiftui/view/popover(ispresented:attachmentanchor:arrowedge:content:) | none (iOS-only) | `Popover` |
| 22 | Scroll views | `SwiftUI.ScrollView` | 13.0 | https://developer.apple.com/documentation/swiftui/scrollview | none (iOS-only) | `ScrollView` |
| 23 | Sheets | `SwiftUI.View.sheet(isPresented:onDismiss:content:)` | 13.0 | https://developer.apple.com/documentation/swiftui/view/sheet(ispresented:ondismiss:content:) | Bottom sheets | - |
| 24 | Color wells | `SwiftUI.ColorPicker` | 14.0 | https://developer.apple.com/documentation/swiftui/colorpicker | none (iOS-only) | `ColorPicker` |
| 25 | Pickers | `SwiftUI.DatePicker` | 13.0 | https://developer.apple.com/documentation/swiftui/datepicker | Date picker | - |
| 26 | Segmented controls | `SwiftUI.SegmentedPickerStyle` | 13.0 | https://developer.apple.com/documentation/swiftui/pickerstyle/segmented | Segmented button | - |
| 27 | Sliders | `SwiftUI.Slider` | 13.0 | https://developer.apple.com/documentation/swiftui/slider | Sliders | - |
| 28 | Steppers | `SwiftUI.Stepper` | 13.0 | https://developer.apple.com/documentation/swiftui/stepper | none (iOS-only) | `Stepper` |
| 29 | Text fields | `SwiftUI.TextField` | 13.0 | https://developer.apple.com/documentation/swiftui/textfield | Text fields | - |
| 30 | Toggles | `SwiftUI.Toggle` | 13.0 | https://developer.apple.com/documentation/swiftui/toggle | Switch | - |
| 31 | Virtual keyboards | `SwiftUI.View.keyboardType(_:)` | 13.0 | https://developer.apple.com/documentation/swiftui/view/keyboardtype(_:) | Text fields | - |
| 32 | Gauges | `SwiftUI.Gauge` | 16.0 | https://developer.apple.com/documentation/swiftui/gauge | none (iOS-only) | `Gauge` |
| 33 | Progress indicators | `SwiftUI.ProgressView` | 14.0 | https://developer.apple.com/documentation/swiftui/progressview | Progress indicators | - |

Totals: 12 iOS-only, 21 shared with an M3 component.

## Notes on the mapping

- Row 9: the existing doc `ui/components/Button/Button.doc.mjs` already says `"ios": "SwiftUI.Button"`. Apple's page
  (struct `Button`, "A control that initiates an action", iOS 13.0) confirms it. No change needed.
- Rows 12 and 13: Apple's HIG names `MenuPickerStyle` for both. A pull-down button runs actions, so we use `Menu`
  ("A control for presenting a menu of actions"); a pop-up button picks one value, so it is a `Picker` with the menu style.
- Row 25: the HIG Pickers page names `Picker` and `DatePicker`. We map the date picker, the part Google also has.
  A plain `Picker` (one choice from a set) maps to Menus or Radio button, by its style.
- Row 26: `.segmented` is the static member; its type is `SegmentedPickerStyle`.
- Row 29: `SecureField` (a password field) is the same job as an M3 text field with a password visual transformation.
- Row 30: an M3 Checkbox also does a toggle's job; the twin is Switch, as both look like a switch.
- Row 31: Compose sets the keyboard through a text field's `keyboardOptions`, so the twin is Text fields, not a new doc.
- Rows 1 and 2: Compose has `Image` (foundation) and `Text` (material3), but Google's components page does not list them,
  so they count as iOS-only here. If the Android lane adds docs for them, the two docs become one with both platforms.
- Row 22: Compose scrolls with a modifier (`verticalScroll`), not a component on Google's page, so ScrollView is iOS-only.
