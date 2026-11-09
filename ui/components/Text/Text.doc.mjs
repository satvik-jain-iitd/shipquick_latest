/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Text",
  "displayName": "Text",
  "platforms": {
    "android": "androidx.compose.material3.Text",
    "ios": "SwiftUI.Text",
    "web": null
  },
  "group": "Text",
  "category": "Content",
  "keywords": [
    "text",
    "copy",
    "words",
    "paragraph",
    "heading"
  ],
  "usage": {
    "description": "Text shows read-only words, one line or many. Apple: \"A view that displays one or more lines of read-only text.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use the type tokens for font and size, so Dynamic Type still works."
      },
      {
        "guidance": true,
        "description": "Let people select useful text, like an error code, with textSelection(.enabled)."
      },
      {
        "guidance": false,
        "description": "Use Text for words people must edit. Use a TextField instead."
      }
    ],
    "accessibility": [
      {
        "name": "Dynamic Type",
        "category": "Content",
        "criterion": "1.4.4 Resize Text",
        "requirement": "200% text size",
        "description": "Text grows with the person's text size setting. Never fix the font size; use the type tokens."
      },
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Body text has at least 4.5:1 contrast with what is behind it."
      }
    ],
    "anatomy": [
      {
        "name": "Words",
        "required": true,
        "description": "The string shown."
      }
    ]
  },
  "props": [
    {
      "name": "content",
      "type": "string",
      "description": "The words to show. init(_:) looks them up for translation; init(verbatim:) shows them as they are.",
      "required": true
    },
    {
      "name": "content",
      "platform": "android",
      "type": "string",
      "description": "The words to show. Compose names this parameter text; an overload takes an AnnotatedString.",
      "required": true
    },
    {
      "name": "style",
      "platform": "android",
      "type": "TextStyle",
      "description": "The text style. Pass one from MaterialTheme.typography, never a hand-set font size.",
      "default": "LocalTextStyle.current"
    },
    {
      "name": "maxLines",
      "platform": "android",
      "type": "number",
      "description": "The most lines to show before the text is cut.",
      "default": "Int.MAX_VALUE"
    }
  ],
  "platformUsage": {
    "android": {
      "description": "On Android, Material 3 Text takes its colour from the content colour of what is behind it, and its style from the theme.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Size text through the type scale, so it grows with the system font size."
        }
      ]
    }
  },
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "ProvideTextStyle",
          "note": "Sets the text style for all Text inside it. Parts like buttons and app bars use it for their labels."
        }
      ]
    }
  }
};
