/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/app-bars (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "AppBar",
  "displayName": "App bar",
  "platforms": {
    "android": "androidx.compose.material3.TopAppBar",
    "ios": "SwiftUI.View.toolbar(content:)",
    "web": null
  },
  "platformUsage": {
    "android": {
      "description": "Pass app bars to Scaffold.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Pass the bar to Scaffold's topBar or bottomBar."
        },
        {
          "guidance": true,
          "description": "Use a scrollBehavior to shrink the bar as the content scrolls."
        }
      ],
      "accessibility": [
        {
          "name": "Icon name",
          "category": "Semantics",
          "criterion": "1.1.1 Non-text Content",
          "requirement": "contentDescription",
          "description": "An icon with no words next to it needs a contentDescription that names the action, like \"Add to favorites\"."
        },
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "48dp",
          "description": "Google: anything a user can tap is at least 48dp. Material sets this on each action only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
        }
      ]
    },
    "ios": {
      "description": "On iOS the bar is the navigation bar at the top, or a toolbar at the bottom. Add items with toolbar(content:) and ToolbarItem. Apple: \"Populates the toolbar or navigation bar with the specified items.\" Set the title with navigationTitle(_:).",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Put each item in a ToolbarItem with a placement, like .topBarTrailing, .bottomBar or .confirmationAction."
        },
        {
          "guidance": true,
          "description": "Set the screen name with navigationTitle(_:) on the view inside the navigation container."
        },
        {
          "guidance": false,
          "description": "Build your own top bar out of stacks and buttons."
        }
      ],
      "accessibility": [
        {
          "name": "VoiceOver",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "a spoken name and state",
          "description": "An icon with no words needs an accessibilityLabel that names the action, like \"Add to favorites\"."
        },
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "44 by 44 pt",
          "description": "Apple: a control needs a hit region of at least 44 by 44 pt (HIG, Buttons). The feel.touchTarget.ios token is 44pt."
        }
      ]
    }
  },
  "group": "App bar",
  "category": "Navigation",
  "keywords": [
    "app bar",
    "toolbar",
    "header",
    "top bar",
    "bottom bar"
  ],
  "usage": {
    "description": "An app bar gives access to key tasks and navigation. A top app bar has the title, main actions and navigation. A bottom app bar has core navigation or actions.",
    "bestPractices": [
      {
        "guidance": false,
        "description": "Put more than a few actions in the bar. Move the rest to a menu."
      }
    ],
    "accessibility": [],
    "anatomy": [
      {
        "name": "Navigation icon",
        "required": false,
        "description": "Back or menu."
      },
      {
        "name": "Title",
        "required": true,
        "description": "The screen name."
      },
      {
        "name": "Actions",
        "required": false,
        "description": "Icon buttons at the end."
      }
    ]
  },
  "props": [
    {
      "name": "title",
      "type": "@Composable () -> Unit",
      "description": "The screen name.",
      "required": true
    },
    {
      "name": "navigationIcon",
      "type": "@Composable () -> Unit",
      "description": "Back or menu, at the start."
    },
    {
      "name": "actions",
      "type": "@Composable RowScope.() -> Unit",
      "description": "Icon buttons at the end."
    },
    {
      "name": "scrollBehavior",
      "type": "TopAppBarScrollBehavior",
      "description": "How the bar reacts when the content scrolls.",
      "default": "null"
    },
    {
      "name": "content",
      "type": "() -> some ToolbarContent",
      "description": "The ToolbarItems.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "placement",
      "type": "ToolbarItemPlacement",
      "description": "ToolbarItem: where the item sits, like .topBarTrailing or .bottomBar.",
      "platform": "ios",
      "default": ".automatic"
    },
    {
      "name": "navigationTitle",
      "type": "LocalizedStringKey",
      "description": "The screen name, set on the view inside the navigation container.",
      "platform": "ios"
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "presentedWindowToolbarStyle", "note": "`.presentedWindowToolbarStyle(_:)`, not on iOS. Apple: \"Sets the style for the toolbar in windows created by interacting with this view.\"", "status": "unavailable-ios", "replacement": "toolbar"}
      ]
    },
    "android": {
      "family": "AppBar",
      "variants": [
        {
          "name": "CenterAlignedTopAppBar",
          "note": "A top app bar with the title in the middle. Use it on a main screen with one short title."
        },
        {
          "name": "MediumTopAppBar",
          "note": "A taller top app bar with the title on its own line. It can shrink to a small bar as the content scrolls."
        },
        {
          "name": "LargeTopAppBar",
          "note": "The tallest top app bar, with a big title. It can shrink to a small bar as the content scrolls."
        },
        {
          "name": "BottomAppBar",
          "note": "A bar at the bottom of the screen with up to four actions and an optional FAB."
        },
        {
          "name": "AppBarRow",
          "note": "A row for app bar actions. Items that do not fit move into an overflow menu. Set maxItemCount and an overflowIndicator."
        },
        {
          "name": "AppBarColumn",
          "note": "A column for app bar actions. Items that do not fit move into an overflow menu. Set maxItemCount and an overflowIndicator."
        }
      ],
      "supporting": [
        {
          "name": "TopAppBarDefaults",
          "use": "Default colours, heights and window insets for top app bars, and the scroll behaviours pinnedScrollBehavior, enterAlwaysScrollBehavior and exitUntilCollapsedScrollBehavior."
        },
        {
          "name": "TopAppBarColors",
          "use": "The colours of a top app bar, before and after the content scrolls under it. Make one with TopAppBarDefaults."
        },
        {
          "name": "TopAppBarScrollBehavior",
          "use": "Links a top app bar to a scrolling list, so the bar hides, shrinks or changes colour. Pass it to the bar and its nestedScrollConnection to the list."
        },
        {
          "name": "TopAppBarState",
          "use": "The height offset and scroll state a top app bar scroll behaviour reads and writes."
        },
        {
          "name": "rememberTopAppBarState",
          "use": "Creates and keeps a TopAppBarState across recompositions."
        },
        {
          "name": "BottomAppBarDefaults",
          "use": "Default colours, height, padding and window insets for the bottom app bar, and exitAlwaysScrollBehavior."
        },
        {
          "name": "BottomAppBarScrollBehavior",
          "use": "Links a bottom app bar to a scrolling list, so the bar hides while the user scrolls."
        },
        {
          "name": "BottomAppBarState",
          "use": "The height offset and scroll state a bottom app bar scroll behaviour reads and writes."
        },
        {
          "name": "rememberBottomAppBarState",
          "use": "Creates and keeps a BottomAppBarState across recompositions."
        },
        {
          "name": "AppBarScope",
          "use": "The scope of AppBarRow and AppBarColumn content. Add items with clickableItem, toggleableItem or customItem."
        },
        {
          "name": "AppBarRowScope",
          "use": "The scope inside AppBarRow, where you add its items."
        },
        {
          "name": "AppBarColumnScope",
          "use": "The scope inside AppBarColumn, where you add its items."
        },
        {
          "name": "AppBarMenuState",
          "use": "Says if the overflow menu of AppBarRow or AppBarColumn is open. Call show() and dismiss() from the overflowIndicator."
        }
      ]
    }
  }
};
