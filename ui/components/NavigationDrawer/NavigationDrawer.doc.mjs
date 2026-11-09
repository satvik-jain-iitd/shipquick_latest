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
  "group": "Navigation",
  "category": "Navigation",
  "keywords": [
    "drawer",
    "side menu",
    "hamburger",
    "navigation"
  ],
  "usage": {
    "description": "A navigation drawer is a menu that slides in from the side. The user swipes or taps a menu icon. Use it for many sections, account links, or features in a complex app.",
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
    ],
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
    }
  ]
};
