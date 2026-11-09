/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/tabs (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Tabs",
  "displayName": "Tabs",
  "platforms": {
    "android": "androidx.compose.material3.PrimaryTabRow",
    "ios": null,
    "web": "@astryxdesign/core/TabList"
  },
  "group": "Tabs",
  "category": "Navigation",
  "keywords": [
    "tabs",
    "tab bar",
    "segments",
    "pages"
  ],
  "usage": {
    "description": "Tabs group related content. Primary tabs sit under the top app bar and show the main content. Secondary tabs split content further inside an area.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use PrimaryTabRow for one set of tabs."
      },
      {
        "guidance": true,
        "description": "Use SecondaryTabRow only for a second level."
      },
      {
        "guidance": false,
        "description": "Use tabs to step through a task. Use a step flow."
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
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on each tab only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      }
    ],
    "anatomy": [
      {
        "name": "Row",
        "required": true,
        "description": "The tab row."
      },
      {
        "name": "Tab",
        "required": true,
        "description": "One tab."
      },
      {
        "name": "Indicator",
        "required": true,
        "description": "Marks the picked tab."
      }
    ]
  },
  "props": [
    {
      "name": "selectedTabIndex",
      "type": "number",
      "description": "The index of the picked tab.",
      "required": true
    },
    {
      "name": "tabs",
      "type": "@Composable () -> Unit",
      "description": "The Tab items.",
      "required": true
    }
  ]
};
