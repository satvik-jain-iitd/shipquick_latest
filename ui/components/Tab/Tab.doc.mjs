/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Tab",
  "displayName": "Tab",
  "platforms": {
    "android": "androidx.compose.material3.Tab",
    "ios": null,
    "web": null
  },
  "group": "Tabs",
  "category": "Navigation",
  "keywords": [
    "tab",
    "tabs",
    "section"
  ],
  "usage": {
    "description": "A Tab is one tab in a tab row. It shows text, an icon or both, and it is selected or not.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Keep tab labels short, one or two words."
      },
      {
        "guidance": false,
        "description": "Mix tabs with text and tabs with only icons in one row."
      }
    ],
    "accessibility": [
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "the feel.touchTarget token",
        "description": "Each control in it is at least the feel.touchTarget token in design/tokens.json."
      },
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Text has at least 4.5:1 contrast with its container."
      }
    ]
  },
  "props": [
    {
      "name": "selected",
      "type": "boolean",
      "description": "Whether this tab is the one on show.",
      "required": true
    },
    {
      "name": "onClick",
      "type": "() -> Unit",
      "description": "Runs when the user picks the tab.",
      "required": true
    },
    {
      "name": "text",
      "type": "@Composable () -> Unit",
      "description": "The tab label."
    },
    {
      "name": "icon",
      "type": "@Composable () -> Unit",
      "description": "The tab icon."
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "LeadingIconTab",
          "note": "A tab with the icon beside the text, not above it."
        }
      ],
      "supporting": [
        {
          "name": "TabIndicatorScope",
          "use": "The scope of a tab row's indicator. Its tabIndicatorOffset moves the indicator under the selected tab."
        },
        {
          "name": "TabPosition",
          "use": "The left edge, width and content width of one tab, for an old-style indicator."
        }
      ]
    }
  }
};
