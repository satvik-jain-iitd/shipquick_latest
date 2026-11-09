/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "app-intents-and-app-shortcuts",
  "displayName": "App Intents and App Shortcuts",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "App Intents and App Shortcuts",
  "category": "Action",
  "keywords": [
    "app intents",
    "shortcuts",
    "siri",
    "spotlight",
    "action"
  ],
  "usage": {
    "description": "App Intents let Siri, Spotlight, Shortcuts and widgets run an action of the app."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use App Intents: https://developer.apple.com/documentation/appintents and App Shortcuts: https://developer.apple.com/documentation/appintents/app-shortcuts."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "AppIntent",
          "use": "iOS 16.0. Apple: \"An interface you use to express app-specific actions and make them available to the rest of the system.\""
        },
        {
          "name": "AppShortcutsProvider",
          "use": "iOS 16.0. Apple: \"A type alias for the type that provides an app’s preconfigured shortcuts.\""
        },
        {
          "name": "AppShortcut",
          "use": "iOS 16.0. Apple: \"A type that defines a preconfigured shortcut for a specific app intent.\""
        }
      ]
    }
  }
};
