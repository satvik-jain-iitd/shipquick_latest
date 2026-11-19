/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "AccessibilityActions",
  "displayName": "Accessibility actions",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "AccessibilityActions",
  "category": "Utility",
  "keywords": [
      "accessibility action",
      "voiceover",
      "adjustable",
      "scroll action",
      "zoom action",
      "quick action"
  ],
  "usage": {
    "description": "Modifiers that give VoiceOver and other assistive tools custom actions on a view: named actions, adjust, scroll, zoom and quick actions. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Accessibility actions",
      "variants": [
        {"name": "accessibilityAction", "note": "`.accessibilityAction(_:_:)`, iOS 13.0. Apple: \"Adds an accessibility action to the view. Actions allow assistive technologies, such as the VoiceOver, to interact with the view by invoking the action.\""},
        {"name": "accessibilityActions", "note": "`.accessibilityActions(_:)`, iOS 16.0. Apple: \"Adds multiple accessibility actions to the view.\""},
        {"name": "accessibilityAdjustableAction", "note": "`.accessibilityAdjustableAction(_:)`, iOS 13.0. Apple: \"Adds an accessibility adjustable action to the view. Actions allow assistive technologies, such as the VoiceOver, to interact with the view by invoking the action.\""},
        {"name": "accessibilityScrollAction", "note": "`.accessibilityScrollAction(_:)`, iOS 13.0. Apple: \"Adds an accessibility scroll action to the view. Actions allow assistive technologies, such as the VoiceOver, to interact with the view by invoking the action.\""},
        {"name": "accessibilityZoomAction", "note": "`.accessibilityZoomAction(_:)`, iOS 16.0. Apple: \"Adds an accessibility zoom action to the view. Actions allow assistive technologies, such as VoiceOver, to interact with the view by invoking the action.\""},
        {"name": "accessibilityQuickAction", "note": "`.accessibilityQuickAction(style:content:)`, not on iOS. Apple: \"Adds a quick action to be shown by the system when active.\"", "status": "unavailable-ios", "replacement": "accessibilityAction"}
      ]
    }
  }
};
