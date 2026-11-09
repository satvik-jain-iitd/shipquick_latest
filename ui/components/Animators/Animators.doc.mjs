/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Animators",
  "displayName": "Animation",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Animators",
  "category": "Utility",
  "keywords": [
    "animation",
    "transition",
    "timeline",
    "keyframe",
    "phase animator"
  ],
  "usage": {
    "description": "These types and modifiers animate views or redraw them on a schedule. Use the SwiftUI type as Apple ships it. Do not redraw it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Respect Reduce Motion. Check the accessibilityReduceMotion setting before a big motion."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "KeyframeAnimator", "note": "iOS 17.0. Apple: \"A container that animates its content with keyframes.\""},
        {"name": "PhaseAnimator", "note": "iOS 17.0. Apple: \"A container that animates its content by automatically cycling through a collection of phases that you provide, each defining a discrete step within an animation.\""},
        {"name": "TimelineView", "note": "iOS 15.0. Apple: \"A view that updates according to a schedule that you provide.\""}
      ]
    }
  }
};
