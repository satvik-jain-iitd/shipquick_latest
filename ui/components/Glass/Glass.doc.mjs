/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Glass",
  "displayName": "Liquid Glass",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Glass",
  "category": "Utility",
  "keywords": [
    "glass",
    "liquid glass",
    "glass effect",
    "material"
  ],
  "usage": {
    "description": "Liquid Glass is the system glass material. Use the SwiftUI type as Apple ships it. Do not redraw it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "GlassEffectContainer", "note": "iOS 26.0. Apple: \"A view that combines multiple Liquid Glass shapes into a single shape that can morph individual shapes into one another.\""}
      ],
      "supporting": [
        {"name": "GlassBackgroundEffectConfiguration.Content", "use": "not on iOS. Apple: \"A type-erased content of a glass background.\"", "status": "unavailable-ios", "replacement": "glassEffect"},
        {"name": "DefaultGlassEffectShape", "use": "iOS 26.0. Apple: \"The default shape applied by glass effects, a capsule.\""}
      ]
    }
  }
};
