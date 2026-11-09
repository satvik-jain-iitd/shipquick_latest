/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "quick-actions",
  "displayName": "Quick actions",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Quick actions",
  "category": "Action",
  "keywords": [
    "quick actions",
    "home screen",
    "shortcut item",
    "long press app icon"
  ],
  "usage": {
    "description": "Quick actions are the short menu people see when they press and hold the app icon."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use UIKit Home Screen quick actions: https://developer.apple.com/documentation/uikit/add-home-screen-quick-actions."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "UIApplicationShortcutItem",
          "use": "iOS 9.0. Apple: \"An application shortcut item, also called a Home Screen dynamic quick action, that specifies a user-initiated action for your app.\""
        }
      ]
    }
  }
};
