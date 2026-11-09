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
      "supporting": [
        {
          "name": "UIEditMenuInteraction",
          "use": "iOS 16.0. Apple: \"An interaction that provides edit operations using a menu.\""
        }
      ]
    }
  }
};
