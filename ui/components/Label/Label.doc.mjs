/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Label",
  "displayName": "Label",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.Label",
    "web": null
  },
  "group": "Label",
  "category": "Content",
  "keywords": [
    "label",
    "icon",
    "title",
    "row",
    "caption"
  ],
  "usage": {
    "description": "Label shows an icon with a title, the standard way to name an item. Apple: \"A standard label for user interface items, consisting of an icon with a title.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use Label for a menu item, a list row title or a toolbar item with an icon."
      },
      {
        "guidance": true,
        "description": "Use system label colours to show how important the text is."
      },
      {
        "guidance": false,
        "description": "Use Label for text people edit. Use a TextField."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "The title is the spoken name, even when a style shows only the icon."
      },
      {
        "name": "Dynamic Type",
        "category": "Content",
        "criterion": "1.4.4 Resize Text",
        "requirement": "200% text size",
        "description": "Text grows with the person's text size setting. Never fix the font size; use the type tokens."
      }
    ],
    "anatomy": [
      {
        "name": "Icon",
        "required": true,
        "description": "An SF Symbol or an image."
      },
      {
        "name": "Title",
        "required": true,
        "description": "The words."
      }
    ]
  },
  "props": [
    {
      "name": "title",
      "type": "string",
      "description": "The words. init(_:systemImage:).",
      "required": true
    },
    {
      "name": "systemImage",
      "type": "string",
      "description": "The SF Symbol name for the icon.",
      "required": true
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "labelStyle", "note": "`.labelStyle(_:)`, iOS 14.0. Apple: \"Sets the style for labels within this view.\""}
      ],
      "supporting": [
        {"name": "LabelStyleConfiguration.Icon", "use": "iOS 14.0. Apple: \"A type-erased icon view of a label.\""},
        {"name": "LabelStyleConfiguration.Title", "use": "iOS 14.0. Apple: \"A type-erased title view of a label.\""}
      ]
    }
  }
};
