# Android library: Google's Compose Material 3 components, counted (story #134, S4)

Source (Tier A, Google's own page): https://developer.android.com/develop/ui/compose/components
Read on: 2026-11-09. The page says "Last updated 2025-07-11 UTC".
API names: the Material 3 Compose reference, https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary

Count: 30

The page has 30 component cards in six groups: Actions, Communication, Containment, Navigation, Selection, Text inputs.
That matches the reviewer's "30". Under the last group the page also has two link cards with no group name:
"Lists and grids" and "Resources". They are not components, and "Lists and grids" opens the same page as "Lists".
So they are not counted.

How to read the table:
- "Doc folder" is the S2 doc and contract. Every row has one.
- "Compose API" is the one composable the doc names in `platforms.android`. Its topic is `android-<folder name>`.
- "Also on the page" lists the other composables Google shows on the same card. An app uses them directly too.
- One card's link differs from its page. "Floating action button" links to the Buttons page.
  Google has its own FAB page, so the table uses that one.
- "Lists" is a layout guide. `LazyColumn` and `LazyRow` are layout containers (rule 38 allows them). Each row is the M3 `ListItem`.

| # | Component (Google's name) | Doc folder | Compose API | Also on the page | Google doc page |
|---|---|---|---|---|---|
| 1 | Buttons | `ui/components/Button/` | `androidx.compose.material3.Button` | Button, FilledTonalButton, ElevatedButton, OutlinedButton, TextButton | https://developer.android.com/develop/ui/compose/components/button |
| 2 | Floating action button | `ui/components/FloatingActionButton/` | `androidx.compose.material3.FloatingActionButton` | FloatingActionButton, SmallFloatingActionButton, LargeFloatingActionButton, ExtendedFloatingActionButton | https://developer.android.com/develop/ui/compose/components/fab |
| 3 | Icon button | `ui/components/IconButton/` | `androidx.compose.material3.IconButton` | IconButton, FilledIconButton, FilledTonalIconButton, OutlinedIconButton | https://developer.android.com/develop/ui/compose/components/icon-button |
| 4 | Segmented button | `ui/components/SegmentedButton/` | `androidx.compose.material3.SegmentedButton` | SingleChoiceSegmentedButtonRow, MultiChoiceSegmentedButtonRow, SegmentedButton | https://developer.android.com/develop/ui/compose/components/segmented-button |
| 5 | Badges | `ui/components/Badge/` | `androidx.compose.material3.BadgedBox` | BadgedBox, Badge | https://developer.android.com/develop/ui/compose/components/badges |
| 6 | Progress indicators | `ui/components/ProgressIndicator/` | `androidx.compose.material3.LinearProgressIndicator` | LinearProgressIndicator, CircularProgressIndicator | https://developer.android.com/develop/ui/compose/components/progress |
| 7 | Snackbar | `ui/components/SnackbarHost/` | `androidx.compose.material3.SnackbarHost` | SnackbarHost, SnackbarHostState.showSnackbar, Snackbar | https://developer.android.com/develop/ui/compose/components/snackbar |
| 8 | Tooltips | `ui/components/Tooltip/` | `androidx.compose.material3.TooltipBox` | TooltipBox, PlainTooltip, RichTooltip, rememberTooltipState | https://developer.android.com/develop/ui/compose/components/tooltip |
| 9 | Bottom sheets | `ui/components/BottomSheet/` | `androidx.compose.material3.ModalBottomSheet` | ModalBottomSheet, rememberModalBottomSheetState, SheetState | https://developer.android.com/develop/ui/compose/components/bottom-sheets |
| 10 | Cards | `ui/components/Card/` | `androidx.compose.material3.Card` | Card, ElevatedCard, OutlinedCard | https://developer.android.com/develop/ui/compose/components/card |
| 11 | Carousel | `ui/components/Carousel/` | `androidx.compose.material3.carousel.HorizontalMultiBrowseCarousel` | HorizontalMultiBrowseCarousel, HorizontalUncontainedCarousel, rememberCarouselState | https://developer.android.com/develop/ui/compose/components/carousel |
| 12 | Dialogs | `ui/components/Dialog/` | `androidx.compose.material3.AlertDialog` | AlertDialog, Dialog | https://developer.android.com/develop/ui/compose/components/dialog |
| 13 | Dividers | `ui/components/Divider/` | `androidx.compose.material3.HorizontalDivider` | HorizontalDivider, VerticalDivider | https://developer.android.com/develop/ui/compose/components/divider |
| 14 | Lists | `ui/components/List/` | `androidx.compose.material3.ListItem` | LazyColumn, LazyRow (androidx.compose.foundation.lazy) with ListItem | https://developer.android.com/develop/ui/compose/lists |
| 15 | Scaffold | `ui/components/Scaffold/` | `androidx.compose.material3.Scaffold` | Scaffold | https://developer.android.com/develop/ui/compose/components/scaffold |
| 16 | App bars | `ui/components/AppBar/` | `androidx.compose.material3.TopAppBar` | TopAppBar, CenterAlignedTopAppBar, MediumTopAppBar, LargeTopAppBar, BottomAppBar | https://developer.android.com/develop/ui/compose/components/app-bars |
| 17 | Navigation bar | `ui/components/NavigationBar/` | `androidx.compose.material3.NavigationBar` | NavigationBar, NavigationBarItem | https://developer.android.com/develop/ui/compose/components/navigation-bar |
| 18 | Navigation drawer | `ui/components/NavigationDrawer/` | `androidx.compose.material3.ModalNavigationDrawer` | ModalNavigationDrawer, ModalDrawerSheet, NavigationDrawerItem, DrawerState | https://developer.android.com/develop/ui/compose/components/drawer |
| 19 | Navigation rail | `ui/components/NavigationRail/` | `androidx.compose.material3.NavigationRail` | NavigationRail, NavigationRailItem | https://developer.android.com/develop/ui/compose/components/navigation-rail |
| 20 | Tabs | `ui/components/Tabs/` | `androidx.compose.material3.PrimaryTabRow` | PrimaryTabRow, SecondaryTabRow, Tab | https://developer.android.com/develop/ui/compose/components/tabs |
| 21 | Checkbox | `ui/components/Checkbox/` | `androidx.compose.material3.Checkbox` | Checkbox, TriStateCheckbox | https://developer.android.com/develop/ui/compose/components/checkbox |
| 22 | Chips | `ui/components/Chip/` | `androidx.compose.material3.FilterChip` | AssistChip, FilterChip, InputChip, SuggestionChip | https://developer.android.com/develop/ui/compose/components/chip |
| 23 | Date picker | `ui/components/DatePicker/` | `androidx.compose.material3.DatePicker` | DatePicker, DatePickerDialog, DateRangePicker, rememberDatePickerState | https://developer.android.com/develop/ui/compose/components/datepickers |
| 24 | Menus | `ui/components/Menu/` | `androidx.compose.material3.DropdownMenu` | DropdownMenu, DropdownMenuItem | https://developer.android.com/develop/ui/compose/components/menu |
| 25 | Radio button | `ui/components/RadioButton/` | `androidx.compose.material3.RadioButton` | RadioButton | https://developer.android.com/develop/ui/compose/components/radio-button |
| 26 | Sliders | `ui/components/Slider/` | `androidx.compose.material3.Slider` | Slider, RangeSlider | https://developer.android.com/develop/ui/compose/components/slider |
| 27 | Switch | `ui/components/Switch/` | `androidx.compose.material3.Switch` | Switch | https://developer.android.com/develop/ui/compose/components/switch |
| 28 | Time pickers | `ui/components/TimePicker/` | `androidx.compose.material3.TimePicker` | TimePicker, TimeInput, rememberTimePickerState | https://developer.android.com/develop/ui/compose/components/time-pickers |
| 29 | Search | `ui/components/SearchBar/` | `androidx.compose.material3.SearchBar` | SearchBar, SearchBarDefaults.InputField (experimental) | https://developer.android.com/develop/ui/compose/components/search-bar |
| 30 | Text fields | `ui/components/TextField/` | `androidx.compose.material3.TextField` | TextField, OutlinedTextField, SecureTextField | https://developer.android.com/develop/ui/compose/text/user-input |

Where the facts come from:
- Each doc uses only Google: the guide page in the table, the M3 reference for the parameters, and Google's
  accessibility page (https://developer.android.com/develop/ui/compose/accessibility/api-defaults).
  That page sets a 48dp touch target, and a null click on a control when its row takes the tap.
- WCAG 2.2 gives the criterion names.
- Props are the Compose parameters an app sets. Colours, shapes and padding come from the tokens, so they are left out.
- The props sit under `platforms.android` in each contract, with `core` empty. The iOS lane (S5, #135) moves the
  shared ones to `core` when it adds the SwiftUI names. `platforms.ios` is null until then.
- `platforms.web` names an `@astryxdesign/core` part only when core 0.7.11 has a part of the same kind
  (a folder in its `packages/core/src`). Otherwise it is null.

Confidence that the count is right: 0.95. Google's page markup was read and every card was checked (Tier A).
