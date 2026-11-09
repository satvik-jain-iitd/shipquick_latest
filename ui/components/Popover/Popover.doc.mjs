/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Popover",
  "displayName": "Popover",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.View.popover(isPresented:attachmentAnchor:arrowEdge:content:)",
    "web": null
  },
  "group": "Popover",
  "category": "Overlay",
  "keywords": [
    "popover",
    "bubble",
    "callout",
    "overlay"
  ],
  "usage": {
    "description": "A popover is a short-lived view over the screen, pointing at the control that opened it. On iPhone it shows as a sheet. Apple: \"Presents a popover when a given condition is true.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Keep a popover small: a few related tasks."
      },
      {
        "guidance": true,
        "description": "Save the person's work when a popover closes by itself."
      },
      {
        "guidance": false,
        "description": "Show two popovers at once, or open a popover from a popover."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "Focus moves into the popover when it opens and back when it closes."
      }
    ],
    "anatomy": [
      {
        "name": "Arrow",
        "required": false,
        "description": "Points at the control that opened it."
      },
      {
        "name": "Content",
        "required": true,
        "description": "The view inside."
      }
    ]
  },
  "props": [
    {
      "name": "isPresented",
      "type": "Binding<Bool>",
      "description": "Shows the popover while true.",
      "required": true
    },
    {
      "name": "arrowEdge",
      "type": "'top' | 'leading' | 'bottom' | 'trailing'",
      "description": "Which edge the arrow comes from. nil lets the system choose.",
      "default": "nil"
    },
    {
      "name": "content",
      "type": "() -> some View",
      "description": "The view inside the popover.",
      "required": true
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "popover", "note": "`.popover(item:attachmentAnchor:arrowEdge:content:)`, iOS 13.0. Apple: \"Presents a popover using the given item as a data source for the popover’s content.\""}
      ]
    }
  }
};
