/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/drawer (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "NavigationDrawer",
  "displayName": "Navigation drawer",
  "platforms": {
    "android": "androidx.compose.material3.ModalNavigationDrawer",
    "ios": "SwiftUI.ListStyle.sidebar",
    "web": null
  },
  "platformUsage": {
    "android": {
      "description": "It is a menu that slides in from the side. The user swipes or taps a menu icon.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Put a ModalDrawerSheet with NavigationDrawerItems in drawerContent."
        },
        {
          "guidance": true,
          "description": "Open and close it with DrawerState."
        },
        {
          "guidance": false,
          "description": "Hide the app's two or three main places in a drawer. Use a navigation bar."
        }
      ],
      "accessibility": [
        {
          "name": "Focus",
          "category": "Keyboard",
          "criterion": "2.4.3 Focus Order",
          "requirement": "focus moves in and back",
          "description": "Focus moves into the surface when it opens and back to what opened it when it closes. Back closes it."
        },
        {
          "name": "State is read out",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "role and state",
          "description": "Screen readers say the role and the state (on, off, selected). Put the click on the whole row with its label, and pass a null click to the control (Google's api-defaults page)."
        }
      ]
    },
    "ios": {
      "description": "On iOS the twin is a sidebar: a List with .listStyle(.sidebar), as the first column of a NavigationSplitView. Apple: \"The list style that describes the behavior and appearance of a sidebar list.\" On iPhone the split view folds into one stack.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Put the sidebar List in NavigationSplitView(sidebar:detail:)."
        },
        {
          "guidance": true,
          "description": "Group a deep list with sections or disclosure groups (Apple HIG, Sidebars)."
        },
        {
          "guidance": false,
          "description": "Hide the app's two or three main places in a sidebar on iPhone. Use a tab bar."
        }
      ],
      "accessibility": [
        {
          "name": "VoiceOver",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "a spoken name and state",
          "description": "VoiceOver says the selected row. Bind selection so the list knows which one it is."
        }
      ]
    }
  },
  "group": "Navigation",
  "category": "Navigation",
  "keywords": [
    "drawer",
    "side menu",
    "hamburger",
    "navigation"
  ],
  "usage": {
    "description": "A navigation drawer lists many sections, account links, or features in a complex app.",
    "bestPractices": [],
    "accessibility": [],
    "anatomy": [
      {
        "name": "Scrim",
        "required": true,
        "description": "Dims the screen."
      },
      {
        "name": "Sheet",
        "required": true,
        "description": "The drawer surface."
      },
      {
        "name": "Item",
        "required": true,
        "description": "One place."
      }
    ]
  },
  "props": [
    {
      "name": "drawerContent",
      "type": "@Composable () -> Unit",
      "description": "The drawer, usually ModalDrawerSheet.",
      "required": true
    },
    {
      "name": "drawerState",
      "type": "DrawerState",
      "description": "Open or closed. Create it with rememberDrawerState(DrawerValue.Closed).",
      "default": "rememberDrawerState(DrawerValue.Closed)"
    },
    {
      "name": "gesturesEnabled",
      "type": "boolean",
      "description": "When false, a swipe does not open or close it.",
      "default": "true"
    },
    {
      "name": "content",
      "type": "@Composable () -> Unit",
      "description": "The screen behind the drawer.",
      "required": true
    },
    {
      "name": "sidebar",
      "type": "() -> some View",
      "description": "NavigationSplitView: the sidebar List.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "detail",
      "type": "() -> some View",
      "description": "NavigationSplitView: what the picked row opens.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "selection",
      "type": "Binding<SelectionValue?>",
      "description": "List: the picked row.",
      "platform": "ios"
    }
  ],
  "platformApi": {
    "android": {
      "family": "NavigationDrawer",
      "variants": [
        {
          "name": "ModalDrawerSheet",
          "note": "The sheet that holds the items of a ModalNavigationDrawer."
        },
        {
          "name": "NavigationDrawerItem",
          "note": "One destination in a drawer sheet: a label, an optional icon and badge, and selected and onClick."
        },
        {
          "name": "DismissibleNavigationDrawer",
          "note": "A drawer that pushes the content aside when open, and that the user can close. Use it when the content should stay in view."
        },
        {
          "name": "DismissibleDrawerSheet",
          "note": "The sheet that holds the items of a DismissibleNavigationDrawer."
        },
        {
          "name": "PermanentNavigationDrawer",
          "note": "A drawer that is always open, beside the content. Use it on large screens only."
        },
        {
          "name": "PermanentDrawerSheet",
          "note": "The sheet that holds the items of a PermanentNavigationDrawer."
        }
      ],
      "supporting": [
        {
          "name": "DrawerState",
          "use": "Says if the drawer is open or closed. Call open() and close() from a coroutine."
        },
        {
          "name": "rememberDrawerState",
          "use": "Creates and keeps a DrawerState, with DrawerValue.Closed or Open as the first value."
        },
        {
          "name": "DrawerValue",
          "use": "The two states of a drawer: Closed and Open."
        },
        {
          "name": "DrawerDefaults",
          "use": "Default container colours, elevations, shape, maximum width and window insets for drawer sheets, and the scrim colour."
        },
        {
          "name": "NavigationDrawerItemDefaults",
          "use": "Default colours and padding for NavigationDrawerItem."
        },
        {
          "name": "NavigationDrawerItemColors",
          "use": "The container, icon, text and badge colours of a NavigationDrawerItem, selected and not."
        }
      ]
    }
  }
};
