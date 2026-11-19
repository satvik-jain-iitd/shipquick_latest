/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ImagePlayground",
  "displayName": "Image Playground",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "ImagePlayground",
  "category": "Utility",
  "keywords": [
    "image playground",
    "generate image",
    "image generation sheet"
  ],
  "usage": {
    "description": "Modifiers for the Image Playground sheet: present it, and pick its styles and options. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Image Playground",
      "variants": [
        {"name": "imagePlaygroundPersonalizationPolicy", "note": "`.imagePlaygroundPersonalizationPolicy(_:)`, iOS 18.4. Apple: \"Policy determining whether to support the usage of people in the playground or not.\"", "status": "deprecated", "replacement": "imagePlaygroundOptions"},
        {"name": "imagePlaygroundGenerationStyle", "note": "`.imagePlaygroundGenerationStyle(_:in:)`, iOS 18.4. Apple: \"Sets the selected and allowed styles to use when displaying the image generation sheet.\""},
        {"name": "imagePlaygroundOptions", "note": "`.imagePlaygroundOptions(_:)`, iOS 26.4. Apple: \"Sets the options to use when generating an image.\""},
        {"name": "imagePlaygroundSheet", "note": "`.imagePlaygroundSheet(isPresented:concept:sourceImage:onCompletion:onCancellation:)`, iOS 18.1. Apple: \"Presents the system sheet to create an image using the specified string and optional starting image.\""}
      ]
    }
  }
};
