/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ShaderEffects",
  "displayName": "Shader effects",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "ShaderEffects",
  "category": "Utility",
  "keywords": [
      "shader",
      "metal",
      "color effect",
      "distortion effect",
      "layer effect",
      "visual effect"
  ],
  "usage": {
    "description": "Modifiers that run a Metal shader on a view or read its geometry to change how it draws. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Shader effects",
      "variants": [
        {"name": "colorEffect", "note": "`.colorEffect(_:isEnabled:)`, iOS 17.0. Apple: \"Returns a new view that applies `shader` to `self` as a filter effect on the color of each pixel.\""},
        {"name": "distortionEffect", "note": "`.distortionEffect(_:maxSampleOffset:isEnabled:)`, iOS 17.0. Apple: \"Returns a new view that applies `shader` to `self` as a geometric distortion effect on the location of each pixel.\""},
        {"name": "layerEffect", "note": "`.layerEffect(_:maxSampleOffset:isEnabled:)`, iOS 17.0. Apple: \"Returns a new view that applies `shader` to `self` as a filter on the raster layer created from `self`.\""},
        {"name": "visualEffect", "note": "`.visualEffect(_:)`, iOS 17.0. Apple: \"Applies effects to this view, while providing access to layout information through a geometry proxy.\""}
      ]
    }
  }
};
