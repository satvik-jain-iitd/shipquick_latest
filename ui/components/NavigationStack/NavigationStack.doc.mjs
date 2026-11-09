/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "NavigationStack",
  "displayName": "Navigation stack",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "NavigationStack",
  "category": "Navigation",
  "keywords": [
    "navigation",
    "stack",
    "push",
    "back button",
    "navigation link",
    "title"
  ],
  "usage": {
    "description": "NavigationStack shows one screen at a time. A NavigationLink pushes the next screen. The back button goes back. Use the SwiftUI type as Apple ships it. Do not redraw it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use NavigationStack for new code. NavigationView is deprecated."
      },
      {
        "guidance": true,
        "description": "Use NavigationSplitView when the screen has two or three columns on iPad."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "NavigationStack", "note": "iOS 16.0. Apple: \"A view that displays a root view and enables you to present additional views over the root view.\""},
        {"name": "NavigationLink", "note": "iOS 13.0. Apple: \"A view that controls a navigation presentation.\""},
        {"name": "NavigationView", "note": "iOS 13.0. Apple: \"A view for presenting a stack of views that represents a visible path in a navigation hierarchy.\"", "status": "deprecated", "replacement": "NavigationStack"},
        {"name": "navigationBarBackButtonHidden", "note": "`.navigationBarBackButtonHidden(_:)`, iOS 13.0. Apple: \"Hides the navigation bar back button for the view.\""},
        {"name": "navigationBarTitleDisplayMode", "note": "`.navigationBarTitleDisplayMode(_:)`, iOS 14.0. Apple: \"Configures the title display mode for this view.\""},
        {"name": "navigationDestination", "note": "`.navigationDestination(for:destination:)`, iOS 16.0. Apple: \"Associates a destination view with a presented data type for use within a navigation stack.\""},
        {"name": "navigationDocument", "note": "`.navigationDocument(_:)`, iOS 16.0. Apple: \"Configures the view’s document for purposes of navigation.\""},
        {"name": "navigationLinkIndicatorVisibility", "note": "`.navigationLinkIndicatorVisibility(_:)`, iOS 17.0. Apple: \"Configures whether navigation links show a disclosure indicator.\""},
        {"name": "navigationSubtitle", "note": "`.navigationSubtitle(_:)`, iOS 26.0. Apple: \"Configures the view’s subtitle for purposes of navigation, using a localized string resource.\""},
        {"name": "navigationTitle", "note": "`.navigationTitle(_:)`, iOS 16.0. Apple: \"Configures the view’s title for purposes of navigation, using a localized string resource.\""},
        {"name": "navigationTransition", "note": "`.navigationTransition(_:)`, iOS 18.0. Apple: \"Sets the navigation transition style for this view.\""}
      ]
    }
  }
};
