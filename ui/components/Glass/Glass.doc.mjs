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
        {"name": "glassEffect", "note": "`.glassEffect(_:in:)`, iOS 26.0. Apple: \"Applies the Liquid Glass effect to a view.\""},
        {"name": "glassEffectID", "note": "`.glassEffectID(_:in:)`, iOS 26.0. Apple: \"Associates an identity value to Liquid Glass effects defined within this view.\""},
        {"name": "glassEffectTransition", "note": "`.glassEffectTransition(_:)`, iOS 26.0. Apple: \"Associates a glass effect transition with any glass effects defined within this view.\""},
        {"name": "glassEffectUnion", "note": "`.glassEffectUnion(id:namespace:)`, iOS 26.0. Apple: \"Associates any Liquid Glass effects defined within this view to a union with the provided identifier.\""}
      ]
    }
  }
};
