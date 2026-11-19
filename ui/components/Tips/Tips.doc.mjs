/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Tips",
  "displayName": "Tips",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Tips",
  "category": "Utility",
  "keywords": [
    "tip kit",
    "tip",
    "popover tip",
    "hint"
  ],
  "usage": {
    "description": "Modifiers for TipKit tips: a popover tip on a view and the look of a TipView. Each entry is a SwiftUI view modifier from TipKit. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Tips",
      "variants": [
        {"name": "popoverTip", "note": "`.popoverTip(_:arrowEdge:action:)`, iOS 17.0. Apple: \"Presents a popover tip on the modified view.\""},
        {"name": "tipAnchor", "note": "`.tipAnchor(_:)`, iOS 26.0. Apple: \"Sets a value for the specified tip anchor to be used to anchor a tip view to the `.bounds` of the view.\""},
        {"name": "tipBackground", "note": "`.tipBackground(_:)`, iOS 17.0. Apple: \"Sets the tip’s view background to a style.\""},
        {"name": "tipBackgroundInteraction", "note": "`.tipBackgroundInteraction(_:)`, iOS 26.0. Apple: \"Controls whether people can interact with the view behind a presented tip.\""},
        {"name": "tipCornerRadius", "note": "`.tipCornerRadius(_:antialiased:)`, iOS 17.0. Apple: \"Sets the corner radius for an inline tip view.\""},
        {"name": "tipImageSize", "note": "`.tipImageSize(_:)`, iOS 17.0. Apple: \"Sets the size for a tip’s image.\""},
        {"name": "tipImageStyle", "note": "`.tipImageStyle(_:)`, iOS 18.0. Apple: \"Sets the style for a tip’s image.\""},
        {"name": "tipViewStyle", "note": "`.tipViewStyle(_:)`, iOS 17.0. Apple: \"Sets the given style for TipView within the view hierarchy.\""}
      ]
    }
  }
};
