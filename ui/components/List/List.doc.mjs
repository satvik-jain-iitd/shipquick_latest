/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/lists (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "List",
  "displayName": "List",
  "platforms": {
    "android": "androidx.compose.material3.ListItem",
    "ios": null,
    "web": "@astryxdesign/core/List"
  },
  "group": "List",
  "category": "Table & List",
  "keywords": [
    "list",
    "row",
    "item",
    "lazy",
    "recycler"
  ],
  "usage": {
    "description": "A list shows a set of items. For a long list or one of unknown length, use LazyColumn (a layout container): it only builds the rows on screen. Build each row with ListItem.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use LazyColumn or LazyRow for long lists."
      },
      {
        "guidance": true,
        "description": "Give each item a stable key."
      },
      {
        "guidance": false,
        "description": "Put a long list in a plain Column. It builds every row at once."
      }
    ],
    "accessibility": [
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "48dp",
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on a clickable row only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      },
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Text has at least 4.5:1 contrast with its fill. The colours come from the tokens, never typed in."
      }
    ],
    "anatomy": [
      {
        "name": "Leading",
        "required": false,
        "description": "An icon or a picture."
      },
      {
        "name": "Headline",
        "required": true,
        "description": "The main words."
      },
      {
        "name": "Supporting",
        "required": false,
        "description": "A second line."
      },
      {
        "name": "Trailing",
        "required": false,
        "description": "Meta text or a control."
      }
    ]
  },
  "props": [
    {
      "name": "headlineContent",
      "type": "@Composable () -> Unit",
      "description": "The main line of the row.",
      "required": true
    },
    {
      "name": "overlineContent",
      "type": "@Composable () -> Unit",
      "description": "A small line above."
    },
    {
      "name": "supportingContent",
      "type": "@Composable () -> Unit",
      "description": "A line below."
    },
    {
      "name": "leadingContent",
      "type": "@Composable () -> Unit",
      "description": "At the start, like an icon."
    },
    {
      "name": "trailingContent",
      "type": "@Composable () -> Unit",
      "description": "At the end, like a switch."
    }
  ]
};
