/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "ShortNavigationBar",
  "displayName": "Short navigation bar",
  "platforms": {
    "android": "androidx.compose.material3.ShortNavigationBar",
    "ios": null,
    "web": null
  },
  "group": "NavigationBar",
  "category": "Navigation",
  "keywords": [
    "navigation",
    "bottom bar",
    "tabs",
    "destinations"
  ],
  "usage": {
    "description": "ShortNavigationBar is the newer, shorter bottom bar for three to five top destinations of an app.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it for three to five top destinations."
      },
      {
        "guidance": true,
        "description": "Give each item a short label."
      },
      {
        "guidance": false,
        "description": "Use it for actions. Use an app bar or a FAB."
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
      "name": "arrangement",
      "type": "'EqualWeight' | 'Centered'",
      "description": "How the items spread: the same width each, or close together in the middle.",
      "default": "'EqualWeight'"
    },
    {
      "name": "content",
      "type": "@Composable () -> Unit",
      "description": "The ShortNavigationBarItem items.",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "ShortNavigationBarItem",
          "note": "One destination in a ShortNavigationBar. Its iconPosition puts the label under the icon or beside it."
        }
      ],
      "supporting": [
        {
          "name": "ShortNavigationBarDefaults",
          "use": "Default colours, arrangement and window insets for ShortNavigationBar."
        },
        {
          "name": "ShortNavigationBarItemDefaults",
          "use": "Default colours for ShortNavigationBarItem."
        },
        {
          "name": "ShortNavigationBarArrangement",
          "use": "How ShortNavigationBar spreads its items: EqualWeight (each item gets the same width) or Centered (the items sit in the middle)."
        },
        {
          "name": "NavigationItemColors",
          "use": "The icon, text and indicator colours that ShortNavigationBarItem and WideNavigationRailItem use, selected and not."
        },
        {
          "name": "NavigationItemIconPosition",
          "use": "Where an item's icon sits next to its label: Top (label below) or Start (label beside)."
        }
      ]
    }
  }
};
