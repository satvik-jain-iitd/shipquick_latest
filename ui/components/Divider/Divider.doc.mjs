/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/divider (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Divider",
  "displayName": "Divider",
  "platforms": {
    "android": "androidx.compose.material3.HorizontalDivider",
    "ios": null,
    "web": "@astryxdesign/core/Divider"
  },
  "group": "Divider",
  "category": "Layout",
  "keywords": [
    "divider",
    "separator",
    "line",
    "rule"
  ],
  "usage": {
    "description": "A divider is a thin line between items in a list or other container. HorizontalDivider splits items in a column. VerticalDivider splits items in a row.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use the default thickness and colour from the theme."
      },
      {
        "guidance": true,
        "description": "Use modifier padding for space around it."
      },
      {
        "guidance": false,
        "description": "Draw your own line with a Box or Canvas."
      }
    ],
    "accessibility": [
      {
        "name": "Not read out",
        "category": "Semantics",
        "criterion": "1.3.1 Info and Relationships",
        "requirement": "no meaning by line alone",
        "description": "A screen reader does not see the line. Group items with headings or lists, not only with lines."
      }
    ],
    "anatomy": [
      {
        "name": "Line",
        "required": true,
        "description": "The thin line."
      }
    ]
  },
  "props": [
    {
      "name": "thickness",
      "type": "Dp",
      "description": "How thick the line is.",
      "default": "DividerDefaults.Thickness"
    }
  ]
};
