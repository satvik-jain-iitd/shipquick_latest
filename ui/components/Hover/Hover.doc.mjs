/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Hover",
  "displayName": "Hover and pointer",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Hover",
  "category": "Utility",
  "keywords": [
    "hover",
    "pointer",
    "trackpad",
    "mouse",
    "hover effect"
  ],
  "usage": {
    "description": "Modifiers for a pointer over a view: hover effects and hover actions on iPad with a trackpad or mouse. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use `.hoverEffect` on tappable views; never make hover the only way to reach something."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Hover and pointer",
      "variants": [
        {"name": "defaultHoverEffect", "note": "`.defaultHoverEffect(_:)`, iOS 17.0. Apple: \"Sets the default hover effect to use for views within this view.\""},
        {"name": "handPointerBehavior", "note": "`.handPointerBehavior(_:)`, not on iOS. Apple: \"Sets the behavior of the hand pointer while the user is interacting with the view.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (the visionOS hand pointer)"},
        {"name": "hoverEffect", "note": "`.hoverEffect(_:)`, iOS 13.4. Apple: \"Applies a hover effect to this view.\""},
        {"name": "hoverEffectDisabled", "note": "`.hoverEffectDisabled(_:)`, iOS 17.0. Apple: \"Adds a condition that controls whether this view can display hover effects.\""},
        {"name": "hoverEffectGroup", "note": "`.hoverEffectGroup()`, not on iOS. Apple: \"Adds an implicit `HoverEffectGroup` to all effects defined on descendant views, so that all effects added to subviews activate as a group whenever this view or any descendant views are hovered.\"", "status": "unavailable-ios", "replacement": "hoverEffect"},
        {"name": "onContinuousHover", "note": "`.onContinuousHover(coordinateSpace:perform:)`, iOS 17.0. Apple: \"Adds an action to perform when the pointer enters, moves within, and exits the view’s bounds.\""},
        {"name": "onHover", "note": "`.onHover(perform:)`, iOS 13.4. Apple: \"Adds an action to perform when the user moves the pointer over or away from the view’s frame.\""},
        {"name": "pointerStyle", "note": "`.pointerStyle(_:)`, not on iOS. Apple: \"Sets the pointer style to display when the pointer is over the view.\"", "status": "unavailable-ios", "replacement": "hoverEffect"},
        {"name": "pointerVisibility", "note": "`.pointerVisibility(_:)`, not on iOS. Apple: \"Sets the visibility of the pointer when it’s over the view.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (hides the Mac pointer only)"}
      ]
    }
  }
};
