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
      "family": "live-activities",
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
      ],
      "variants": [
        {"name": "activityBackgroundTint", "note": "`.activityBackgroundTint(_:)`, iOS 16.0. Apple: \"Sets the tint color for the background of a Live Activity that appears on the Lock Screen.\""},
        {"name": "activitySystemActionForegroundColor", "note": "`.activitySystemActionForegroundColor(_:)`, iOS 16.1. Apple: \"The text color for the auxiliary action button that the system shows next to a Live Activity on the Lock Screen.\""},
        {"name": "dynamicIsland", "note": "`.dynamicIsland(verticalPlacement:)`, iOS 16.1. Apple: \"Specifies the vertical placement for a view of an expanded Live Activity that appears in the Dynamic Island.\""}
      ]
    }
  }
};
