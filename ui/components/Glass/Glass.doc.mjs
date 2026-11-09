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
        {"name": "glassBackgroundEffect", "note": "`.glassBackgroundEffect(displayMode:)`, not on iOS. Apple: \"Fills the view’s background with an automatic glass background effect and container-relative rounded rectangle shape.\"", "status": "unavailable-ios", "replacement": "glassEffect"}
      ]
    }
  }
};
