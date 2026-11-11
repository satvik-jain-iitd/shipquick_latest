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
    },
    "android": {
      "description": "Use Jetpack Glance: https://developer.android.com/develop/ui/compose/glance. A Glance widget is built with Glance's own composables, which become RemoteViews; Material 3 composables do not run in a widget.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Build the content inside provideContent, in your GlanceAppWidget's provideGlance."
        },
        {
          "guidance": false,
          "description": "Use Material 3 composables or Compose modifiers in a widget. Use Glance's composables and GlanceModifier."
        }
      ]
    }
  },
  "platformApi": {
    "ios": {
      "family": "widgets",
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
      ],
      "variants": [
        {"name": "widgetURL", "note": "`.widgetURL(_:)`, iOS 14.0. Apple: \"Sets the URL to open in the containing app when the user clicks the widget.\""}
      ]
    },
    "android": {
      "supporting": [
        {
          "name": "GlanceAppWidget",
          "use": "The widget. Override provideGlance(context, id) and call provideContent with the content."
        },
        {
          "name": "GlanceAppWidgetReceiver",
          "use": "The receiver the system talks to. Set its glanceAppWidget, and declare it in the manifest with an appwidget-provider file."
        },
        {
          "name": "GlanceModifier",
          "use": "Glance's modifier for size, padding, background and clicks."
        },
        {
          "name": "androidx.glance.appwidget.updateAll",
          "use": "Redraws every placed copy of a GlanceAppWidget after its data changes."
        }
      ]
    }
  }
};
