/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ColorAdjustments",
  "displayName": "Color adjustments",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "ColorAdjustments",
  "category": "Utility",
  "keywords": [
      "brightness",
      "contrast",
      "saturation",
      "grayscale",
      "hue",
      "invert"
  ],
  "usage": {
    "description": "Modifiers that adjust the colors a view draws: brightness, contrast, saturation, hue, invert, grayscale and multiply. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Color adjustments",
      "variants": [
        {"name": "brightness", "note": "`.brightness(_:)`, iOS 13.0. Apple: \"Brightens this view by the specified amount.\""},
        {"name": "contrast", "note": "`.contrast(_:)`, iOS 13.0. Apple: \"Sets the contrast and separation between similar colors in this view.\""},
        {"name": "colorInvert", "note": "`.colorInvert()`, iOS 13.0. Apple: \"Inverts the colors in this view.\""},
        {"name": "colorMultiply", "note": "`.colorMultiply(_:)`, iOS 13.0. Apple: \"Adds a color multiplication effect to this view.\""},
        {"name": "grayscale", "note": "`.grayscale(_:)`, iOS 13.0. Apple: \"Adds a grayscale effect to this view.\""},
        {"name": "hueRotation", "note": "`.hueRotation(_:)`, iOS 13.0. Apple: \"Applies a hue rotation effect to this view.\""},
        {"name": "luminanceToAlpha", "note": "`.luminanceToAlpha()`, iOS 13.0. Apple: \"Adds a luminance to alpha effect to this view.\""},
        {"name": "saturation", "note": "`.saturation(_:)`, iOS 13.0. Apple: \"Adjusts the color saturation of this view.\""}
      ]
    }
  }
};
