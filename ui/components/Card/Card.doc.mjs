/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/card (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Card",
  "displayName": "Card",
  "platforms": {
    "android": "androidx.compose.material3.Card",
    "ios": "SwiftUI.GroupBox",
    "web": "@astryxdesign/core/Card"
  },
  "platformUsage": {
    "android": {
      "description": "It lays its content out in a column. ElevatedCard adds a shadow. OutlinedCard adds a border.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Pass onClick when the whole card opens the item."
        },
        {
          "guidance": false,
          "description": "Use a card for a whole screen. Use Scaffold for that."
        }
      ],
      "accessibility": [
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "48dp",
          "description": "Google: anything a user can tap is at least 48dp. Material sets this on a clickable card only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
        }
      ]
    },
    "ios": {
      "description": "On iOS the twin is GroupBox. Apple: \"A stylized view, with an optional label, that visually collects a logical grouping of content.\"",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Give the box a title: GroupBox(\"Title\") { ... }, or a custom label with GroupBox(content:label:)."
        },
        {
          "guidance": true,
          "description": "Make the whole box tappable by putting it inside a Button or a NavigationLink."
        },
        {
          "guidance": false,
          "description": "Nest boxes inside boxes. Apple: group things inside a box with padding and alignment."
        }
      ],
      "accessibility": [
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "44 by 44 pt",
          "description": "Apple: a control needs a hit region of at least 44 by 44 pt (HIG, Buttons). The feel.touchTarget.ios token is 44pt."
        }
      ]
    }
  },
  "group": "Card",
  "category": "Container",
  "keywords": [
    "card",
    "tile",
    "container",
    "item"
  ],
  "usage": {
    "description": "A card holds one piece of content, like a product, a news story or a message.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use a card for one item inside a bigger layout."
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
        "name": "Container",
        "required": true,
        "description": "The surface."
      },
      {
        "name": "Content",
        "required": true,
        "description": "Text, images and actions in a column."
      }
    ]
  },
  "props": [
    {
      "name": "onClick",
      "type": "() => void",
      "description": "Makes the whole card clickable. Leave it out for a still card."
    },
    {
      "name": "enabled",
      "type": "boolean",
      "description": "When false, the part is greyed out and ignores the user.",
      "default": "true"
    },
    {
      "name": "content",
      "type": "@Composable ColumnScope.() -> Unit",
      "description": "What the card holds, in a column.",
      "required": true
    },
    {
      "name": "titleKey",
      "type": "LocalizedStringKey",
      "description": "The title at the top of the box.",
      "platform": "ios"
    },
    {
      "name": "content",
      "type": "() -> some View",
      "description": "What the box holds.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "label",
      "type": "() -> some View",
      "description": "A custom label instead of a title.",
      "platform": "ios"
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "groupBoxStyle", "note": "`.groupBoxStyle(_:)`, iOS 14.0. Apple: \"Sets the style for group boxes within this view.\""}
      ]
    }
  }
};
