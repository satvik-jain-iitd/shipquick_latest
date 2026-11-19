/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/navigation-rail (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "NavigationRail",
  "displayName": "Navigation rail",
  "platforms": {
    "android": "androidx.compose.material3.NavigationRail",
    "ios": null,
    "web": null
  },
  "group": "Navigation",
  "category": "Navigation",
  "keywords": [
    "navigation rail",
    "rail",
    "side navigation",
    "tablet"
  ],
  "usage": {
    "description": "A navigation rail sits on the side of a large screen and gives access to the main places. Each NavigationRailItem is one place.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it on tablets and desktops for three to seven main places."
      },
      {
        "guidance": false,
        "description": "Use it on a phone in portrait. Use a navigation bar."
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
        "name": "Header",
        "required": false,
        "description": "A FAB or a logo at the top."
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
      "name": "header",
      "type": "@Composable ColumnScope.() -> Unit",
      "description": "Top of the rail, like a FAB."
    },
    {
      "name": "content",
      "type": "@Composable ColumnScope.() -> Unit",
      "description": "The NavigationRailItems.",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "NavigationRailItem",
          "note": "One destination in a NavigationRail: an icon, an optional label, and selected and onClick."
        }
      ],
      "supporting": [
        {
          "name": "NavigationRailDefaults",
          "use": "Default container colour and window insets for NavigationRail."
        },
        {
          "name": "NavigationRailItemDefaults",
          "use": "Default colours for NavigationRailItem. Make them with NavigationRailItemDefaults.colors()."
        },
        {
          "name": "NavigationRailItemColors",
          "use": "The icon, text and indicator colours of a NavigationRailItem, selected and not."
        }
      ]
    }
  }
};
