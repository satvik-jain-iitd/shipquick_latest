/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ShareLink",
  "displayName": "ShareLink",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.ShareLink",
    "web": null
  },
  "group": "ShareLink",
  "category": "Action",
  "keywords": [
    "share",
    "share sheet",
    "activity",
    "send"
  ],
  "usage": {
    "description": "ShareLink is a share button. It opens the system share sheet. Apple: \"A view that controls a sharing presentation.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use the Share button for sharing. People know where to look."
      },
      {
        "guidance": false,
        "description": "Build your own copy of an action the share sheet already has, like Print."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "The button's title is its spoken name. The default is \"Share\"."
      }
    ],
    "anatomy": [
      {
        "name": "Button",
        "required": true,
        "description": "The share icon and title."
      },
      {
        "name": "Share sheet",
        "required": true,
        "description": "The system sheet that opens."
      }
    ]
  },
  "props": [
    {
      "name": "title",
      "type": "string",
      "description": "The button words. init(_:item:subject:message:).",
      "default": "\"Share\""
    },
    {
      "name": "item",
      "type": "Transferable",
      "description": "What to share: a URL, a string, or any Transferable.",
      "required": true
    },
    {
      "name": "subject",
      "type": "string",
      "description": "A subject line, used by Mail."
    },
    {
      "name": "message",
      "type": "string",
      "description": "A message sent with the item."
    }
  ],
  "platformApi": {
    "ios": {
      "supporting": [
        {"name": "DefaultShareLinkLabel", "use": "iOS 16.0. Apple: \"The default label used for a share link.\""}
      ]
    }
  }
};
