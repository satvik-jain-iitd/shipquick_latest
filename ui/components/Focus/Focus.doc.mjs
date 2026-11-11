/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Focus",
  "displayName": "Focus",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Focus",
  "category": "Utility",
  "keywords": [
    "focus",
    "focus state",
    "default focus",
    "focused value"
  ],
  "usage": {
    "description": "Modifiers that move, read or share focus: which view takes keyboard and hardware input next. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Bind focus with @FocusState and `.focused`; let the system draw the focus effect."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Focus",
      "variants": [
        {"name": "defaultFocus", "note": "`.defaultFocus(_:_:priority:)`, iOS 17.0. Apple: \"Defines a region of the window in which default focus is evaluated by assigning a value to a given focus state binding.\""},
        {"name": "focusable", "note": "`.focusable(_:)`, iOS 17.0. Apple: \"Specifies if the view is focusable.\""},
        {"name": "focused", "note": "`.focused(_:equals:)`, iOS 15.0. Apple: \"Modifies this view by binding its focus state to the given state value.\""},
        {"name": "focusedObject", "note": "`.focusedObject(_:)`, iOS 16.0. Apple: \"Creates a new view that exposes the provided object to other views whose whose state depends on the focused view hierarchy.\""},
        {"name": "focusedSceneObject", "note": "`.focusedSceneObject(_:)`, iOS 16.0. Apple: \"Creates a new view that exposes the provided object to other views whose whose state depends on the active scene.\""},
        {"name": "focusedSceneValue", "note": "`.focusedSceneValue(_:_:)`, iOS 15.0. Apple: \"Modifies this view by injecting a value that you provide for use by other views whose state depends on the focused scene.\""},
        {"name": "focusedValue", "note": "`.focusedValue(_:_:)`, iOS 14.0. Apple: \"Modifies this view by injecting a value that you provide for use by other views whose state depends on the focused view hierarchy.\""},
        {"name": "focusEffectDisabled", "note": "`.focusEffectDisabled(_:)`, iOS 17.0. Apple: \"Adds a condition that controls whether this view can display focus effects, such as a default focus ring or hover effect.\""},
        {"name": "focusScope", "note": "`.focusScope(_:)`, not on iOS. Apple: \"Creates a focus scope that SwiftUI uses to limit default focus preferences.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (scopes prefersDefaultFocus on Mac, TV and Watch; iOS defaultFocus needs no scope)"},
        {"name": "focusSection", "note": "`.focusSection()`, not on iOS. Apple: \"Indicates that the view’s frame and cohort of focusable descendants should be used to guide focus movement.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (guides tvOS and Mac focus moves; iOS has no focus engine sections)"},
        {"name": "prefersDefaultFocus", "note": "`.prefersDefaultFocus(_:in:)`, not on iOS. Apple: \"Indicates that the view should receive focus by default for a given namespace.\"", "status": "unavailable-ios", "replacement": "defaultFocus"},
        {"name": "accessibilityFocused", "note": "`.accessibilityFocused(_:)`, iOS 15.0. Apple: \"Modifies this view by binding its accessibility element’s focus state to the given boolean state value.\""},
        {"name": "accessibilityDefaultFocus", "note": "`.accessibilityDefaultFocus(_:_:)`, iOS 26.0. Apple: \"Defines a region in which default accessibility focus is evaluated by assigning a value to a given accessibility focus state binding.\""}
      ]
    }
  }
};
