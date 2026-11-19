/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "edit-menus",
  "displayName": "Edit menus",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Edit menus",
  "category": "Overlay",
  "keywords": [
    "edit menu",
    "copy",
    "paste",
    "text selection menu",
    "uieditmenuinteraction"
  ],
  "usage": {
    "description": "An edit menu shows Copy, Paste and other edit actions."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Text fields and text views show the system edit menu on their own. For a custom view, use UIKit's UIEditMenuInteraction: https://developer.apple.com/documentation/uikit/uieditmenuinteraction."
    }
  },
  "platformApi": {
    "ios": {
      "family": "edit-menus",
      "supporting": [
        {
          "name": "UIEditMenuInteraction",
          "use": "iOS 16.0. Apple: \"An interaction that provides edit operations using a menu.\""
        }
      ],
      "variants": [
        {"name": "copyable", "note": "`.copyable(_:)`, iOS 27.0. Apple: \"Specifies a list of items to copy in response to the system’s Copy command.\""},
        {"name": "cuttable", "note": "`.cuttable(for:action:)`, iOS 27.0. Apple: \"Specifies an action that moves items to the Clipboard in response to the system’s Cut command.\""},
        {"name": "onCopyCommand", "note": "`.onCopyCommand(perform:)`, not on iOS. Apple: \"Adds an action to perform in response to the system’s Copy command.\"", "status": "unavailable-ios", "replacement": "copyable"},
        {"name": "onCutCommand", "note": "`.onCutCommand(perform:)`, not on iOS. Apple: \"Adds an action to perform in response to the system’s Cut command.\"", "status": "unavailable-ios", "replacement": "cuttable"},
        {"name": "onPasteCommand", "note": "`.onPasteCommand(of:perform:)`, not on iOS. Apple: \"Adds an action to perform in response to the system’s Paste command.\"", "status": "unavailable-ios", "replacement": "pasteDestination"}
      ]
    }
  }
};
