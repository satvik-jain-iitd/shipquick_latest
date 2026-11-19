/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Redaction",
  "displayName": "Redaction and privacy",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Redaction",
  "category": "Utility",
  "keywords": [
      "redacted",
      "placeholder",
      "privacy sensitive",
      "screen capture",
      "skeleton"
  ],
  "usage": {
    "description": "Modifiers that hide content as a placeholder, mark it private, or block screen capture of it. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Redaction and privacy",
      "variants": [
        {"name": "redacted", "note": "`.redacted(reason:)`, iOS 14.0. Apple: \"Adds a reason to apply a redaction to this view hierarchy.\""},
        {"name": "unredacted", "note": "`.unredacted()`, iOS 14.0. Apple: \"Removes any reason to apply a redaction to this view hierarchy.\""},
        {"name": "privacySensitive", "note": "`.privacySensitive(_:)`, iOS 15.0. Apple: \"Marks the view as containing sensitive, private user data.\""},
        {"name": "invalidatableContent", "note": "`.invalidatableContent(_:)`, iOS 17.0. Apple: \"Mark the receiver as their content might be invalidated.\""},
        {"name": "contentCaptureProtected", "note": "`.contentCaptureProtected(_:)`, not on iOS. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/contentcaptureprotected(_:)", "status": "unavailable-ios", "replacement": "nothing on iOS (visionOS 26 only, Apple's page names no iOS twin)"}
      ]
    }
  }
};
