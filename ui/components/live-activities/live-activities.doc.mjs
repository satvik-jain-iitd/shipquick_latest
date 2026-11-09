/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "live-activities",
  "displayName": "Live Activities",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Live Activities",
  "category": "Feedback & Status",
  "keywords": [
    "live activity",
    "dynamic island",
    "lock screen",
    "activitykit"
  ],
  "usage": {
    "description": "A Live Activity shows the live state of a task, like a delivery, on the Lock Screen and in the Dynamic Island."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use ActivityKit: https://developer.apple.com/documentation/activitykit."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "Activity",
          "use": "iOS 16.1. Apple: \"The object you use to start, update, and end a Live Activity.\""
        },
        {
          "name": "ActivityAttributes",
          "use": "iOS 16.1. Apple: \"The protocol you implement to describe the content of a Live Activity.\""
        },
        {
          "name": "ActivityConfiguration",
          "use": "iOS 16.1. Apple: \"An object that describes the content of a Live Activity.\""
        }
      ]
    }
  }
};
