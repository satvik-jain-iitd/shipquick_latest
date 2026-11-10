/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Gestures",
  "displayName": "Gestures",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Gestures",
  "category": "Utility",
  "keywords": [
    "gesture",
    "tap",
    "long press",
    "hit testing",
    "pencil"
  ],
  "usage": {
    "description": "Modifiers that make a view answer touches: taps, long presses, custom gestures, hit testing and Apple Pencil input. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Prefer a Button or a List swipe action over a bare tap gesture: they come with accessibility built in."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Gestures",
      "variants": [
        {"name": "allowsHitTesting", "note": "`.allowsHitTesting(_:)`, iOS 13.0. Apple: \"Configures whether this view participates in hit test operations.\""},
        {"name": "allowsWindowActivationEvents", "note": "`.allowsWindowActivationEvents()`, iOS 18.0. Apple: \"Configures gestures in this view hierarchy to handle events that activate the containing window.\""},
        {"name": "contentShape", "note": "`.contentShape(_:eoFill:)`, iOS 13.0. Apple: \"Defines the content shape for hit testing.\""},
        {"name": "defersSystemGestures", "note": "`.defersSystemGestures(on:)`, iOS 16.0. Apple: \"Sets the screen edge from which you want your gesture to take precedence over the system gesture.\""},
        {"name": "gesture", "note": "`.gesture(_:isEnabled:)`, iOS 13.0. Apple: \"Attaches a gesture to the view with a lower precedence than gestures defined by the view.\""},
        {"name": "handGestureShortcut", "note": "`.handGestureShortcut(_:isEnabled:)`, iOS 18.0. Apple: \"Assigns a hand gesture shortcut to the modified control.\""},
        {"name": "highPriorityGesture", "note": "`.highPriorityGesture(_:including:)`, iOS 13.0. Apple: \"Attaches a gesture to the view with a higher precedence than gestures defined by the view.\""},
        {"name": "manipulable", "note": "`.manipulable(coordinateSpace:operations:inertia:isEnabled:onChanged:)`, not on iOS. Apple: \"Allows this view to be manipulated using common hand gestures.\"", "status": "unavailable-ios", "replacement": "gesture"},
        {"name": "manipulationGesture", "note": "`.manipulationGesture(updating:coordinateSpace:operations:inertia:isEnabled:onChanged:)`, not on iOS. Apple: \"Adds a manipulation gesture to this view without allowing this view to be manipulable itself.\"", "status": "unavailable-ios", "replacement": "gesture"},
        {"name": "onLongPressGesture", "note": "`.onLongPressGesture(minimumDuration:maximumDistance:perform:onPressingChanged:)`, iOS 13.0. Apple: \"Adds an action to perform when this view recognizes a long press gesture.\""},
        {"name": "onLongTouchGesture", "note": "`.onLongTouchGesture(minimumDuration:perform:onTouchingChanged:)`, not on iOS. Apple: \"Adds an action to perform when this view recognizes a remote long touch gesture. A long touch gesture is when the finger is on the remote touch surface without actually pressing.\"", "status": "unavailable-ios", "replacement": "onLongPressGesture"},
        {"name": "onPencilDoubleTap", "note": "`.onPencilDoubleTap(perform:)`, iOS 17.5. Apple: \"Adds an action to perform after the user double-taps their Apple Pencil.\""},
        {"name": "onPencilSqueeze", "note": "`.onPencilSqueeze(perform:)`, iOS 17.5. Apple: \"Adds an action to perform when the user squeezes their Apple Pencil.\""},
        {"name": "onTapGesture", "note": "`.onTapGesture(count:perform:)`, iOS 13.0. Apple: \"Adds an action to perform when this view recognizes a tap gesture.\""},
        {"name": "simultaneousGesture", "note": "`.simultaneousGesture(_:including:)`, iOS 13.0. Apple: \"Attaches a gesture to the view to process simultaneously with gestures defined by the view.\""}
      ]
    }
  }
};
