/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "widgets",
  "displayName": "Widgets",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Widgets",
  "category": "Content",
  "keywords": [
    "widget",
    "home screen",
    "lock screen",
    "widgetkit",
    "timeline"
  ],
  "usage": {
    "description": "A widget shows a small, glanceable view of the app outside the app."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use WidgetKit: https://developer.apple.com/documentation/widgetkit."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "Widget",
          "use": "iOS 14.0. Apple: \"The configuration and content of a widget to display on the Home screen or in Notification Center.\""
        },
        {
          "name": "WidgetConfiguration",
          "use": "iOS 14.0. Apple: \"A type that describes a widget’s content.\""
        },
        {
          "name": "TimelineProvider",
          "use": "iOS 14.0. Apple: \"A type that advises WidgetKit when to update a widget’s display.\""
        }
      ]
    }
  }
};
