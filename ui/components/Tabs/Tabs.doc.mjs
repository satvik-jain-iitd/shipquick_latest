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
  "platformUsage": {
    "android": {
      "bestPractices": [
        {
          "guidance": true,
          "description": "Use PrimaryTabRow for one set of tabs."
        },
        {
          "guidance": true,
          "description": "Use SecondaryTabRow only for a second level."
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
      ]
    }
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
        "guidance": false,
        "description": "Use tabs to step through a task. Use a step flow."
      }
    ],
    "accessibility": [],
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
  ],
  "platformApi": {
    "android": {
      "family": "TabRow",
      "variants": [
        {
          "name": "Tab",
          "note": "One tab in a tab row: text, an icon or both, and selected and onClick."
        },
        {
          "name": "LeadingIconTab",
          "note": "A tab with the icon beside the text, not above it."
        },
        {
          "name": "SecondaryTabRow",
          "note": "A tab row for tabs inside one part of the screen, below a PrimaryTabRow or inside content."
        },
        {
          "name": "PrimaryScrollableTabRow",
          "note": "A PrimaryTabRow that scrolls sideways. Use it when the tabs do not fit the width."
        },
        {
          "name": "SecondaryScrollableTabRow",
          "note": "A SecondaryTabRow that scrolls sideways. Use it when the tabs do not fit the width."
        },
        {
          "name": "TabRowDefaults.PrimaryIndicator",
          "note": "The indicator line PrimaryTabRow draws under the selected tab, as wide as its content."
        },
        {
          "name": "TabRowDefaults.SecondaryIndicator",
          "note": "The indicator line SecondaryTabRow draws under the selected tab, as wide as the tab."
        },
        {
          "name": "TabRow",
          "note": "The old tab row.",
          "status": "deprecated",
          "replacement": "PrimaryTabRow or SecondaryTabRow (Google: \"Replaced with PrimaryTabRow and SecondaryTabRow.\")"
        },
        {
          "name": "ScrollableTabRow",
          "note": "The old scrolling tab row.",
          "status": "deprecated",
          "replacement": "PrimaryScrollableTabRow or SecondaryScrollableTabRow (Google: \"Replaced with PrimaryScrollableTabRow and SecondaryScrollableTabRow tab variants.\")"
        },
        {
          "name": "TabRowDefaults.Indicator",
          "note": "The old indicator.",
          "status": "deprecated",
          "replacement": "TabRowDefaults.SecondaryIndicator (Google: \"Use SecondaryIndicator instead.\")"
        }
      ],
      "supporting": [
        {
          "name": "TabRowDefaults",
          "use": "Default colours, the indicator composables, and the edge padding and minimum tab width of scrollable rows."
        },
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
