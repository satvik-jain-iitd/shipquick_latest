/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "SwipeToDismissBox",
  "displayName": "Swipe to dismiss",
  "platforms": {
    "android": "androidx.compose.material3.SwipeToDismissBox",
    "ios": null,
    "web": null
  },
  "group": "List",
  "category": "Table & List",
  "keywords": [
    "swipe",
    "dismiss",
    "delete",
    "list item"
  ],
  "usage": {
    "description": "SwipeToDismissBox lets the user swipe an item to the side to act on it, like delete. The background content shows behind the item while it moves.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Offer the same action in a menu too, for people who cannot swipe."
      },
      {
        "guidance": false,
        "description": "Make swipe the only way to delete."
      }
    ],
    "accessibility": [
      {
        "name": "Other way",
        "category": "Keyboard",
        "criterion": "2.5.1 Pointer Gestures",
        "requirement": "a single-tap alternative",
        "description": "The action is also in a menu or a button."
      }
    ]
  },
  "props": [
    {
      "name": "state",
      "type": "SwipeToDismissBoxState",
      "description": "Where the item rests. Make it with rememberSwipeToDismissBoxState().",
      "required": true
    },
    {
      "name": "backgroundContent",
      "type": "@Composable RowScope.() -> Unit",
      "description": "What shows behind the item, like a delete icon.",
      "required": true
    },
    {
      "name": "enableDismissFromStartToEnd",
      "type": "boolean",
      "description": "Allows a swipe from the start edge.",
      "default": "true"
    },
    {
      "name": "enableDismissFromEndToStart",
      "type": "boolean",
      "description": "Allows a swipe from the end edge.",
      "default": "true"
    },
    {
      "name": "content",
      "type": "@Composable RowScope.() -> Unit",
      "description": "The list item.",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "supporting": [
        {
          "name": "SwipeToDismissBoxState",
          "use": "Says where a swiped item rests and is going: currentValue, targetValue and dismissDirection. Call reset() or snapTo() from a coroutine."
        },
        {
          "name": "rememberSwipeToDismissBoxState",
          "use": "Creates and keeps a SwipeToDismissBoxState, with the first value and the swipe threshold."
        },
        {
          "name": "SwipeToDismissBoxValue",
          "use": "Where a swiped item rests: Settled, StartToEnd or EndToStart."
        },
        {
          "name": "SwipeToDismissBoxDefaults",
          "use": "The default positionalThreshold for how far the user must swipe."
        }
      ]
    }
  }
};
