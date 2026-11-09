/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Link",
  "displayName": "Link",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Link",
  "category": "Navigation",
  "keywords": [
    "link",
    "url",
    "open web page",
    "help link",
    "settings link"
  ],
  "usage": {
    "description": "Link opens a web address or an app link. Use the SwiftUI type as Apple ships it. Do not redraw it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use Link for a place outside the app. Use NavigationLink for a screen inside the app."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Link",
      "variants": [
        {"name": "HelpLink", "note": "not on iOS. Apple: \"A button with a standard appearance that opens app-specific help documentation.\"", "status": "unavailable-ios", "replacement": "Link"},
        {"name": "Link", "note": "iOS 14.0. Apple: \"A control for navigating to a URL.\""},
        {"name": "SettingsLink", "note": "not on iOS. Apple: \"A view that opens the Settings scene defined by an app.\"", "status": "unavailable-ios", "replacement": "Link"}
      ],
      "supporting": [
        {"name": "DefaultSettingsLinkLabel", "use": "not on iOS. Apple: \"The default label to use for a settings link.\"", "status": "unavailable-ios", "replacement": "Link"}
      ]
    }
  }
};
