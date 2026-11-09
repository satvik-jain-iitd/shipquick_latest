/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "NavigationStack",
  "displayName": "Navigation stack",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "NavigationStack",
  "category": "Navigation",
  "keywords": [
    "navigation",
    "stack",
    "push",
    "back button",
    "navigation link",
    "title"
  ],
  "usage": {
    "description": "NavigationStack shows one screen at a time. A NavigationLink pushes the next screen. The back button goes back. Use the SwiftUI type as Apple ships it. Do not redraw it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use NavigationStack for new code. NavigationView is deprecated."
      },
      {
        "guidance": true,
        "description": "Use NavigationSplitView when the screen has two or three columns on iPad."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "NavigationStack", "note": "iOS 16.0. Apple: \"A view that displays a root view and enables you to present additional views over the root view.\""},
        {"name": "NavigationLink", "note": "iOS 13.0. Apple: \"A view that controls a navigation presentation.\""},
        {"name": "NavigationView", "note": "iOS 13.0. Apple: \"A view for presenting a stack of views that represents a visible path in a navigation hierarchy.\"", "status": "deprecated", "replacement": "NavigationStack"}
      ]
    }
  }
};
