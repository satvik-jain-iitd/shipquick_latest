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
        {"name": "TimelineView", "note": "iOS 15.0. Apple: \"A view that updates according to a schedule that you provide.\""},
        {"name": "animation", "note": "`.animation(_:value:)`, iOS 13.0. Apple: \"Applies the given animation to this view when the specified value changes.\""},
        {"name": "contentTransition", "note": "`.contentTransition(_:)`, iOS 16.0. Apple: \"Modifies the view to use a given transition as its method of animating changes to the contents of its views.\""},
        {"name": "geometryGroup", "note": "`.geometryGroup()`, iOS 17.0. Apple: \"Isolates the geometry (e.g. position and size) of the view from its parent view.\""},
        {"name": "keyframeAnimator", "note": "`.keyframeAnimator(initialValue:repeating:content:keyframes:)`, iOS 17.0. Apple: \"Loops the given keyframes continuously, updating the view using the modifiers you apply in `body`.\""},
        {"name": "matchedGeometryEffect", "note": "`.matchedGeometryEffect(id:in:properties:anchor:isSource:)`, iOS 14.0. Apple: \"Defines a group of views with synchronized geometry using an identifier and namespace that you provide.\""},
        {"name": "matchedTransitionSource", "note": "`.matchedTransitionSource(id:in:)`, iOS 18.0. Apple: \"Identifies this view as the source of a navigation transition, such as a zoom transition.\""},
        {"name": "phaseAnimator", "note": "`.phaseAnimator(_:content:animation:)`, iOS 17.0. Apple: \"Animates effects that you apply to a view over a sequence of phases that change continuously.\""},
        {"name": "transaction", "note": "`.transaction(_:)`, iOS 13.0. Apple: \"Applies the given transaction mutation function to all animations used within the view.\""},
        {"name": "transition", "note": "`.transition(_:)`, iOS 17.0. Apple: \"Associates a transition with the view.\""}
      ]
    }
  }
};
