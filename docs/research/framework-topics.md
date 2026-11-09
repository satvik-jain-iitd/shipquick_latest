# Framework topics: the parts outside the two UI libraries (story #231)

The line below is written by `python3 scripts/ui_api_lists.py --fetch-frameworks`. Do not edit it by hand.
It pins the saved public names of each framework package. The coverage gate checks every framework-doc name against them (story #288).

Saved names: `docs/research/sources/framework-names.json` sha256 `7d687a60f1a23cc1b8da43b53c4bab825cadd528788fc374f67ecce0ca45cae3`

Date: 2026-11-09. Kept by hand. Each link was opened on that date and answered 200.

These are not in the Compose Material 3 API or in SwiftUI's View list. They come from another framework.
Each one gets one doc later, and that doc points to the official framework. This first PR only lists them.

Source tier: A for every row. Each link is the vendor's own documentation.

## iOS

| # | Topic | Framework | Official source |
|---|---|---|---|
| 1 | Swift Charts | Charts | https://developer.apple.com/documentation/charts |
| 2 | Web view | WebKit, `WKWebView` | https://developer.apple.com/documentation/webkit/wkwebview |
| 3 | Collection view | UIKit, `UICollectionView` | https://developer.apple.com/documentation/uikit/uicollectionview |
| 4 | Edit menus | UIKit, `UIEditMenuInteraction` | https://developer.apple.com/documentation/uikit/uieditmenuinteraction |
| 5 | Quick actions | UIKit, Home Screen quick actions | https://developer.apple.com/documentation/uikit/add-home-screen-quick-actions |
| 6 | Activity rings | HealthKitUI, `HKActivityRingView` | https://developer.apple.com/documentation/healthkitui/hkactivityringview |
| 7 | Widgets | WidgetKit | https://developer.apple.com/documentation/widgetkit |
| 8 | Live Activities | ActivityKit | https://developer.apple.com/documentation/activitykit |
| 9 | Notifications | UserNotifications | https://developer.apple.com/documentation/usernotifications |
| 10 | App Intents and App Shortcuts | App Intents | https://developer.apple.com/documentation/appintents and https://developer.apple.com/documentation/appintents/app-shortcuts |
| 11 | Controls | WidgetKit controls | https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system |

## Android

| # | Topic | Framework | Official source |
|---|---|---|---|
| 1 | Pull to refresh | Compose Material 3, `PullToRefreshBox` (also a row of `android-m3-api.md`) | https://developer.android.com/develop/ui/compose/components/pull-to-refresh |
| 2 | Widgets | Jetpack Glance | https://developer.android.com/develop/ui/compose/glance |
| 3 | Notifications | Android notifications | https://developer.android.com/develop/ui/views/notifications |
