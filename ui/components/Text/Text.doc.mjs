/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Text",
  "displayName": "Text",
  "platforms": {
    "android": null,
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
    }
  ]
};
