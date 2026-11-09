/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "AppBarRow",
  "displayName": "App bar row",
  "platforms": {
    "android": "androidx.compose.material3.AppBarRow",
    "ios": null,
    "web": null
  },
  "group": "AppBar",
  "category": "Navigation",
  "keywords": [
    "app bar",
    "actions",
    "overflow",
    "toolbar"
  ],
  "usage": {
    "description": "AppBarRow lays out the actions of an app bar in a row. Items that do not fit move into an overflow menu.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Put the most used actions first, so they stay in view."
      },
      {
        "guidance": true,
        "description": "Set maxItemCount to the number of actions that fit."
      },
      {
        "guidance": false,
        "description": "Build your own overflow menu. AppBarRow makes it."
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
      "description": "The button that opens the overflow menu. Call show() on the state it gets.",
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
      "type": "AppBarRowScope.() -> Unit",
      "description": "The items: clickableItem, toggleableItem or customItem.",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "supporting": [
        {
          "name": "AppBarScope",
          "use": "The scope of AppBarRow and AppBarColumn content. Add items with clickableItem, toggleableItem or customItem."
        },
        {
          "name": "AppBarRowScope",
          "use": "The scope inside AppBarRow, where you add its items."
        },
        {
          "name": "AppBarMenuState",
          "use": "Says if the overflow menu of AppBarRow or AppBarColumn is open. Call show() and dismiss() from the overflowIndicator."
        }
      ]
    }
  }
};
