/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/navigation-bar (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "NavigationBar",
  "displayName": "Navigation bar",
  "platforms": {
    "android": "androidx.compose.material3.NavigationBar",
    "ios": "SwiftUI.TabView",
    "web": null
  },
  "group": "Navigation",
  "category": "Navigation",
  "keywords": [
    "navigation bar",
    "bottom navigation",
    "tabs",
    "tab bar"
  ],
  "usage": {
    "description": "A navigation bar at the bottom lets the user switch between the app's main places. Each NavigationBarItem is one place.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it for three to five places of equal weight."
      },
      {
        "guidance": true,
        "description": "Use it on compact windows. Use a navigation rail on large ones."
      },
      {
        "guidance": false,
        "description": "Use it for fewer than three or more than five places."
      }
    ],
    "accessibility": [
      {
        "name": "State is read out",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "role and state",
        "description": "Screen readers say the role and the state (on, off, selected). Put the click on the whole row with its label, and pass a null click to the control (Google's api-defaults page)."
      },
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "48dp",
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on each item only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      }
    ],
    "anatomy": [
      {
        "name": "Container",
        "required": true,
        "description": "The bar."
      },
      {
        "name": "Item",
        "required": true,
        "description": "One place: icon, label, selected mark."
      }
    ]
  },
  "props": [
    {
      "name": "content",
      "type": "@Composable RowScope.() -> Unit",
      "description": "The NavigationBarItems.",
      "required": true
    },
    {
      "name": "selected",
      "type": "boolean",
      "description": "NavigationBarItem: true for the place on screen now.",
      "required": true
    },
    {
      "name": "onClick",
      "type": "() => void",
      "description": "NavigationBarItem: runs when the user taps the place. Go there here.",
      "required": true
    },
    {
      "name": "icon",
      "type": "@Composable () -> Unit",
      "description": "NavigationBarItem: the icon for the place.",
      "required": true
    },
    {
      "name": "label",
      "type": "@Composable () -> Unit",
      "description": "NavigationBarItem: the words under the icon."
    }
  ]
};
