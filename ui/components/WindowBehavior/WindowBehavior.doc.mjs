/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "WindowBehavior",
  "displayName": "Window behavior",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "WindowBehavior",
  "category": "Utility",
  "keywords": [
      "window",
      "full screen",
      "minimize",
      "resize",
      "dismiss",
      "macOS window"
  ],
  "usage": {
    "description": "Modifiers that set how a window resizes, minimizes, goes full screen and dismisses, plus its clipping margins. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Window behavior",
      "variants": [
        {"name": "windowDismissBehavior", "note": "`.windowDismissBehavior(_:)`, not on iOS. Apple: \"Configures the dismiss functionality for the window enclosing `self`.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowFullScreenBehavior", "note": "`.windowFullScreenBehavior(_:)`, not on iOS. Apple: \"Configures the full screen functionality for the window enclosing `self`.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowMinimizeBehavior", "note": "`.windowMinimizeBehavior(_:)`, not on iOS. Apple: \"Configures the minimize functionality for the window enclosing `self`.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowResizeAnchor", "note": "`.windowResizeAnchor(_:)`, not on iOS. Apple: \"Sets the window anchor point used when the size of the view changes such that the window must resize.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowResizeBehavior", "note": "`.windowResizeBehavior(_:)`, not on iOS. Apple: \"Configures the resize functionality for the window enclosing `self`.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowToolbarFullScreenVisibility", "note": "`.windowToolbarFullScreenVisibility(_:)`, iOS 18.0. Apple: \"Configures the visibility of the window toolbar when the window enters full screen mode.\""},
        {"name": "preferredWindowClippingMargins", "note": "`.preferredWindowClippingMargins(_:_:)`, not on iOS. Apple: \"Requests additional margins for drawing beyond the bounds of the window.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (drawing past a visionOS window's bounds)"}
      ]
    }
  }
};
