/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "AppBarColumn",
  "displayName": "App bar column",
  "platforms": {
    "android": "androidx.compose.material3.AppBarColumn",
    "ios": null,
    "web": null
  },
  "group": "AppBar",
  "category": "Navigation",
  "keywords": [
    "app bar",
    "actions",
    "overflow",
    "column"
  ],
  "usage": {
    "description": "AppBarColumn lays out app bar actions in a column, for example in a vertical toolbar. Items that do not fit move into an overflow menu.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Put the most used actions first, so they stay in view."
      },
      {
        "guidance": false,
        "description": "Build your own overflow menu. AppBarColumn makes it."
      }
    ],
    "accessibility": [
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "the feel.touchTarget token",
        "description": "Each control in it is at least the feel.touchTarget token in design/tokens.json."
      }
    ]
  },
  "props": [
    {
      "name": "overflowIndicator",
      "type": "@Composable (AppBarMenuState) -> Unit",
      "description": "The button that opens the overflow menu.",
      "required": true
    },
    {
      "name": "maxItemCount",
      "type": "number",
      "description": "How many items show before the rest go into the overflow menu.",
      "default": "Int.MAX_VALUE"
    },
    {
      "name": "content",
      "type": "AppBarColumnScope.() -> Unit",
      "description": "The items: clickableItem, toggleableItem or customItem.",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "supporting": [
        {
          "name": "AppBarColumnScope",
          "use": "The scope inside AppBarColumn, where you add its items."
        }
      ]
    }
  }
};
