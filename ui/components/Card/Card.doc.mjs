/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/card (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Card",
  "displayName": "Card",
  "platforms": {
    "android": "androidx.compose.material3.Card",
    "ios": null,
    "web": "@astryxdesign/core/Card"
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
    "description": "A card holds one piece of content, like a product, a news story or a message. It lays its content out in a column. ElevatedCard adds a shadow. OutlinedCard adds a border.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use a card for one item inside a bigger layout."
      },
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
    }
  ]
};
