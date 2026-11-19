/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/badges (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Badge",
  "displayName": "Badge",
  "platforms": {
    "android": "androidx.compose.material3.BadgedBox",
    "ios": null,
    "web": "@astryxdesign/core/Badge"
  },
  "platformUsage": {
    "android": {
      "description": "BadgedBox holds the part, and Badge is the mark. A Badge with no content is a small dot.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Put a Badge in BadgedBox's badge slot and the icon in its content slot."
        }
      ],
      "accessibility": [
        {
          "name": "Count is read out",
          "category": "Semantics",
          "criterion": "1.1.1 Non-text Content",
          "requirement": "contentDescription",
          "description": "The badge is only a picture. Say the number in the icon's contentDescription, like \"Mail, 3 unread\"."
        }
      ]
    }
  },
  "group": "Badge",
  "category": "Feedback & Status",
  "keywords": [
    "badge",
    "count",
    "notification",
    "dot",
    "unread"
  ],
  "usage": {
    "description": "A badge is a small mark on another part that shows a status or a number, like unread messages or items in a cart.",
    "bestPractices": [
      {
        "guidance": false,
        "description": "Put the only copy of important news in a badge. Show it on the screen too."
      }
    ],
    "accessibility": [
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
        "name": "Anchor",
        "required": true,
        "description": "The part the badge sits on, usually an Icon."
      },
      {
        "name": "Badge",
        "required": true,
        "description": "The dot or the number."
      }
    ]
  },
  "props": [
    {
      "name": "badge",
      "type": "@Composable BoxScope.() -> Unit",
      "description": "The mark, usually Badge.",
      "required": true
    },
    {
      "name": "content",
      "type": "@Composable BoxScope.() -> Unit",
      "description": "The part the badge sits on.",
      "required": true
    }
  ],
  "platformApi": {
    "ios": {
      "family": "Badge",
      "variants": [
        {"name": "badge", "note": "`.badge(_:)`, iOS 16.0. Apple: \"Generates a badge for the view from a localized string resource.\""},
        {"name": "badgeProminence", "note": "`.badgeProminence(_:)`, iOS 17.0. Apple: \"Specifies the prominence of badges created by this view.\""}
      ]
    },
    "android": {
      "variants": [
        {
          "name": "Badge",
          "note": "The small dot or count itself. Put it in the badge slot of BadgedBox. Leave content out for a dot."
        }
      ],
      "supporting": [
        {
          "name": "BadgeDefaults",
          "use": "The default container colour of a badge."
        }
      ]
    }
  }
};
