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
      "family": "Glass",
      "variants": [
        {"name": "GlassEffectContainer", "note": "iOS 26.0. Apple: \"A view that combines multiple Liquid Glass shapes into a single shape that can morph individual shapes into one another.\""},
        {"name": "glassEffect", "note": "`.glassEffect(_:in:)`, iOS 26.0. Apple: \"Applies the Liquid Glass effect to a view.\""},
        {"name": "glassEffectID", "note": "`.glassEffectID(_:in:)`, iOS 26.0. Apple: \"Associates an identity value to Liquid Glass effects defined within this view.\""},
        {"name": "glassEffectTransition", "note": "`.glassEffectTransition(_:)`, iOS 26.0. Apple: \"Associates a glass effect transition with any glass effects defined within this view.\""},
        {"name": "glassEffectUnion", "note": "`.glassEffectUnion(id:namespace:)`, iOS 26.0. Apple: \"Associates any Liquid Glass effects defined within this view to a union with the provided identifier.\""},
        {"name": "glassBackgroundEffect", "note": "`.glassBackgroundEffect(displayMode:)`, not on iOS. Apple: \"Fills the view’s background with an automatic glass background effect and container-relative rounded rectangle shape.\"", "status": "unavailable-ios", "replacement": "glassEffect"}
      ],
      "supporting": [
        {"name": "GlassBackgroundEffectConfiguration.Content", "use": "not on iOS. Apple: \"A type-erased content of a glass background.\"", "status": "unavailable-ios", "replacement": "glassEffect"},
        {"name": "DefaultGlassEffectShape", "use": "iOS 26.0. Apple: \"The default shape applied by glass effects, a capsule.\""}
      ]
    }
  }
};
